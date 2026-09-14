#!/usr/bin/env python3
# w3m_pty.py -- the spark page inside a real w3m, in a pty, against a
# stub `spark` (on PATH: the wrapper says `spark` plainly, and that is
# what must be proven) that logs what it was asked and answers a fixed
# word. Proves the loop the snippet promises: M-s stashes the RENDERED
# page (never the HTML) and opens the quiet spark page -- a form field,
# an overview link, part links past 16000 chars -- where nothing runs
# until the reader asks; a question (typed, or a link) runs `spark
# read` on the stash and answers as a page carrying the form again; a
# refusal shows on the page. The test performs the README's install
# lines: keymap.spark appended to a throwaway ~/.w3m/keymap, cgi_bin
# written to ~/.w3m/config, the wrapper on PATH. Skips (exit 0)
# without w3m. w3m draws word by word in a pty: expectations match ONE
# token.
#
#   python3 tests/w3m_pty.py

import fcntl
import os
import re
import pty
import select
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
import termios
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = REPO                                   # the repo root is the plugin
CSI = re.compile(r"\x1b(?:\[[0-9;?]*[ -/]*[@-~]|\([A-Za-z0-9]|\][^\x07\x1b]*(?:\x07|\x1b\\)|[@-Z\\-_])")

STUB = r'''#!/bin/sh
# the stub spark: log argv and stdin, answer one word
printf '%s\n' "$*" >> "$STUB_LOG"
cat > "$STUB_LOG.stdin"
case " $* " in
    *" fail "*)   printf 'spark: the source does not answer -- it opens: "STUB-OPENING ..."\n' >&2; exit 1 ;;
    *" long "*)   i=0; while [ $i -lt 40 ]; do printf 'wrapword '; i=$((i+1)); done; printf '\n'; exit 0 ;;
esac
printf 'STUB-READ\n'
'''

PAGE = """<html><head><title>gate</title></head><body>
<h1>The gate</h1>
<p>The gate opens at nine and closes at noon.</p>
<p>Tickets are two dollars, free for children.</p>
</body></html>
"""


class Browser:
    def __init__(self, argv, env, cwd, rows=30, cols=100):
        self.buf = b""
        self.pos = 0
        pid, fd = pty.fork()
        if pid == 0:
            os.chdir(cwd)
            os.execvpe(argv[0], argv, env)
        self.pid, self.fd = pid, fd
        fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))

    def read(self, timeout):
        end = time.time() + timeout
        while time.time() < end:
            r, _, _ = select.select([self.fd], [], [], 0.1)
            if r:
                try:
                    data = os.read(self.fd, 4096)
                except OSError:
                    return
                if not data:
                    return
                self.buf += data

    def plain(self):
        """what was drawn since mark(), with the escape sequences removed"""
        return CSI.sub("", self.buf[self.pos:].decode("utf-8", "replace"))

    def expect(self, text, timeout=10):
        end = time.time() + timeout
        while time.time() < end:
            if text in self.plain():
                return True
            self.read(0.2)
        return False

    def send(self, s, wait=0.5):
        os.write(self.fd, s.encode())
        time.sleep(wait)

    def mark(self):
        self.pos = len(self.buf)

    def close(self):
        try:
            os.close(self.fd)
        except OSError:
            pass
        try:
            os.kill(self.pid, 15)
        except OSError:
            pass
        try:
            os.waitpid(self.pid, 0)
        except OSError:
            pass


def main():
    w3m = shutil.which("w3m")
    if not w3m:
        print("w3m_pty: w3m is not installed here -- skipped (apt-get install w3m / brew install w3m)")
        return 0
    fail = 0

    def ok(cond, what, extra=""):
        nonlocal fail
        print("  %s %s%s" % ("ok  " if cond else "FAIL", what, ("   " + extra) if extra and not cond else ""))
        if not cond:
            fail += 1

    with tempfile.TemporaryDirectory(prefix="spark-w3m-") as tmp:
        work, bindir = [os.path.join(tmp, d) for d in ("work", "bin")]
        os.makedirs(work)
        os.makedirs(bindir)
        # the README's install lines, performed: the snippet appended to
        # a fresh ~/.w3m/keymap, cgi_bin into ~/.w3m/config, the wrapper
        # on PATH as shipped (no chmod: the repo files must already be
        # executable, or this test must fail the way the box once did)
        os.makedirs(os.path.join(tmp, ".w3m"))
        with open(os.path.join(REPO, "keymap.spark")) as f:
            snippet = f.read()
        with open(os.path.join(tmp, ".w3m", "keymap"), "a") as f:
            f.write(snippet)
        with open(os.path.join(tmp, ".w3m", "config"), "w") as f:
            f.write("cgi_bin %s\n" % PLUGIN)
        os.symlink(os.path.join(REPO, "spark-w3m"), os.path.join(bindir, "spark-w3m"))
        stub = os.path.join(bindir, "spark")
        with open(stub, "w") as f:
            f.write(STUB)
        os.chmod(stub, 0o755)
        log = os.path.join(tmp, "stub.log")
        stash = os.path.join(tmp, "stash")
        page = os.path.join(work, "page.html")
        with open(page, "w") as f:
            f.write(PAGE)
        env = {"HOME": tmp, "TERM": "xterm-256color",
               "PATH": bindir + ":" + os.environ.get("PATH", "/usr/bin:/bin"),
               "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "STUB_LOG": log,
               "SPARK_W3M_STASH": stash}
        argv = [w3m, "page.html"]

        def logged():
            try:
                with open(log) as f:
                    return f.read()
            except OSError:
                return ""

        def fresh(doc="page.html", token="gate"):
            for p in (log, log + ".stdin", stash):
                if os.path.exists(p):
                    os.unlink(p)
            b = Browser([w3m, doc], env, work)
            ok(b.expect(token), "w3m draws the page")
            b.mark()
            return b

        def spark_page(b):
            b.send("\x1bs", 1.5)
            return b.expect("spark>")

        # A. M-s stashes the page and opens the QUIET spark page:
        # form, overview link, nothing run
        b = fresh()
        ok(spark_page(b), "M-s opens the spark page", b.plain()[-200:])
        ok(b.expect("overview"), "the overview link is on it")
        ok(b.expect("ask"), "the form's ask button is on it")
        with open(stash) as f:
            st = f.read()
        ok("Tickets are two dollars" in st and "<p>" not in st,
           "the RENDERED page is stashed, not the HTML", repr(st[:120]))
        ok(stat.S_IMODE(os.stat(stash).st_mode) == 0o600, "the stash is 0600")
        ok(not os.path.exists(log), "the quiet page runs nothing unasked")
        b.close()

        # B. the overview link asks what the page covers; the answer is
        # a page carrying the form again; the stash travelled, no path
        b = fresh()
        spark_page(b)
        b.send("\t"); b.send("\t"); b.send("\t")
        b.mark()
        b.send("\r", 1.5)
        ok(b.expect("STUB-READ"), "the overview link answers in a page", b.plain()[-300:])
        got = logged()
        ok(got.strip() == "read", "spark read got no words -- the overview, no name, no path", got)
        with open(log + ".stdin") as f:
            stdin = f.read()
        ok("Tickets" in stdin and tmp not in got, "the stash travelled on stdin; no path in argv", repr(stdin[:120]))
        ok(b.expect("ask"), "the answer page carries the form: the follow-up lives there")
        b.mark()
        b.send("B", 1.0)
        ok(b.expect("overview"), "B walks back to the spark page", b.plain()[-200:])
        b.close()

        # C. words typed into the field are the question; a leading ?
        # is stripped, the editors' habit
        b = fresh()
        spark_page(b)
        b.send("\t")
        b.send("\r", 0.8)
        b.send("?does it mention prices", 0.6)
        b.send("\r", 0.8)
        b.send("\t")
        b.send("\r", 1.5)
        ok(b.expect("STUB-READ"), "a typed question answers in a page", b.plain()[-300:])
        ok(logged().strip() == "read does it mention prices",
           "the words reach spark read, the leading ? stripped", logged())
        b.close()

        # D. a page past 16000 chars: part links on the spark page; a
        # part link reads that part
        big = os.path.join(work, "big.html")
        with open(big, "w") as f:
            f.write("<html><body><p>bigword " + "filler " * 3500 + "</p></body></html>")
        b = fresh("big.html", "bigword")
        spark_page(b)
        ok(b.expect("part"), "part links on a long page", b.plain()[-200:])
        for _ in range(5):
            b.send("\t")
        b.send("\r", 1.5)
        ok(b.expect("STUB-READ") and logged().strip() == "read --part 2",
           "the part 2 link reads part 2", logged())
        b.close()

        # E. a refusal on spark's stderr shows on the answer page
        b = fresh()
        spark_page(b)
        b.send("\t")
        b.send("\r", 0.8)
        b.send("fail", 0.5)
        b.send("\r", 0.8)
        b.send("\t")
        b.send("\r", 1.5)
        ok(b.expect("STUB-OPENING"), "a refusal shows on the page, not lost on stderr", b.plain()[-300:])
        b.close()

        # F. from a plain shell the wrapper takes the words directly,
        # and a long answer wraps at spaces
        if os.path.exists(log):
            os.unlink(log)
        p = subprocess.run([os.path.join(bindir, "spark-w3m"), "long"],
                           input="body\n", capture_output=True, text=True, env=env)
        ok(p.returncode == 0 and all(len(l) <= 78 for l in p.stdout.splitlines()),
           "pipe mode: a long answer wraps at spaces, at most 78 columns", p.stdout[:100])
        ok(logged().strip() == "read long", "pipe mode passes the words", logged())

        ok(not os.path.exists(os.path.join(REPO, "stub.log")), "the repo tree is untouched")

    print("w3m_pty: %s" % ("all ok" if fail == 0 else "%d FAILED" % fail))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())

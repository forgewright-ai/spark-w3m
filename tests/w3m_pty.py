#!/usr/bin/env python3
# w3m_pty.py -- the spark keymap inside a real w3m, in a pty, against a
# stub `spark` (on PATH: the wrapper says `spark` plainly, and that is
# what must be proven) that logs what it was asked and answers a fixed
# word. Proves the whole loop the snippet promises: M-s pipes the
# RENDERED page (never the HTML) through `spark-w3m` into a new buffer,
# M-a opens w3m's pipe prompt for a question, the words reach `spark
# read` with the page on stdin and no path, and a refusal on spark's
# stderr still shows in the buffer (the wrapper folds it in). The test
# performs the README's install lines: the repo's keymap.spark is
# appended to a throwaway ~/.w3m/keymap and the wrapper is put on PATH.
# Skips (exit 0) without w3m.
#
#   python3 tests/w3m_pty.py

import fcntl
import os
import re
import pty
import select
import shutil
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

    def send(self, s):
        os.write(self.fd, s.encode())
        time.sleep(0.3)

    def mark(self):
        self.pos = len(self.buf)

    def close(self):
        try:
            os.close(self.fd)
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
        # the README's install lines, performed: the snippet appended to a
        # fresh ~/.w3m/keymap, the wrapper on PATH
        os.makedirs(os.path.join(tmp, ".w3m"))
        with open(os.path.join(REPO, "keymap.spark")) as f:
            snippet = f.read()
        with open(os.path.join(tmp, ".w3m", "keymap"), "a") as f:
            f.write(snippet)
        # the README's ln -s, performed as shipped: no chmod here -- the
        # repo file must already be executable, or this test must fail
        # the way the box did
        os.symlink(os.path.join(REPO, "spark-w3m"), os.path.join(bindir, "spark-w3m"))
        stub = os.path.join(bindir, "spark")
        with open(stub, "w") as f:
            f.write(STUB)
        os.chmod(stub, 0o755)
        log = os.path.join(tmp, "stub.log")
        page = os.path.join(work, "page.html")
        with open(page, "w") as f:
            f.write(PAGE)
        env = {"HOME": tmp, "TERM": "xterm-256color",
               "PATH": bindir + ":" + os.environ.get("PATH", "/usr/bin:/bin"),
               "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "STUB_LOG": log}
        argv = [w3m, "page.html"]

        def logged():
            try:
                with open(log) as f:
                    return f.read()
            except OSError:
                return ""

        def fresh():
            if os.path.exists(log):
                os.unlink(log)
            b = Browser(argv, env, work)
            ok(b.expect("The gate"), "w3m draws the page")
            b.mark()
            return b

        # A. M-s opens the spark prompt; Enter alone is the overview
        b = fresh()
        b.send("\x1bs")
        ok(b.expect("spark>"), "M-s opens the spark prompt on screen", b.plain()[-200:])
        ok(b"\x1b[9999;1H\x1b[2Kspark> " in b.buf,
           "the prompt homes to the screen's last row, not over the page",
           repr(b.buf[-120:]))
        b.send("\r")
        ok(b.expect("characters"), "the pulse names the page's size on the bottom row", b.plain()[-200:])
        ok(b.expect("STUB-READ"), "Enter alone is the overview: the answer opens in a buffer", b.plain()[-300:])
        got = logged()
        ok(got.strip() == "read", "spark read got no words -- the overview, no name, no path", got)
        ok(work not in got and "page.html" not in got, "the page's path never reaches spark", got)
        with open(log + ".stdin") as f:
            stdin = f.read()
        ok("Tickets are two dollars" in stdin and "<p>" not in stdin,
           "the RENDERED text travelled on stdin, not the HTML", repr(stdin[:120]))
        b.send("B")                 # back to the page
        b.send("Q")                 # quit, no confirmation
        b.read(1.0)
        b.close()

        # B. words at the prompt are the question; glob characters stay
        # literal (the wrapper word-splits under set -f); a backspace
        # edits, and the raw reader echoes NO newline for the Enter --
        # a newline on the bottom row scrolls the screen under w3m
        b = fresh()
        b.send("\x1bs")
        b.expect("spark>")
        b.send("does it mention *prices*X\x7f\r")
        ok(b.expect("STUB-READ"), "words run the question: the answer opens in a buffer", b.plain()[-300:])
        ok(logged().strip() == "read does it mention *prices*",
           "spark read got exactly the words, globs literal, backspace edits", logged())
        i = b.buf.find(b"*prices*X")
        ok(i > 0 and b"\n" not in b.buf[i:i + 40].split(b"STUB", 1)[0].replace(b"\x1b[2K", b""),
           "the Enter is swallowed: no newline echoed on the bottom row",
           repr(b.buf[i:i + 60]))
        b.send("B")
        b.send("Q")
        b.read(1.0)
        b.close()

        # C. the editors' habit and the flags: a leading ? is stripped,
        # --part rides to spark read
        b = fresh()
        b.send("\x1bs")
        b.expect("spark>")
        b.send("? is this clear\r")
        b.expect("STUB-READ")
        ok(logged().strip() == "read is this clear", "a leading ? is stripped, the editors' habit", logged())
        b.send("B")
        b.send("Q")
        b.read(1.0)
        b.close()
        b = fresh()
        b.send("\x1bs")
        b.expect("spark>")
        b.send("--part 2 what repeats about gates\r")
        b.expect("STUB-READ")
        ok(logged().strip() == "read --part 2 what repeats about gates",
           "flags typed at the prompt ride to spark read", logged())
        b.send("B")
        b.send("Q")
        b.read(1.0)
        b.close()

        # D. a refusal on spark's stderr still shows in the buffer: the
        # wrapper folds stderr into the answer. Match ONE token: w3m
        # draws a line word by word, each with its own cursor move
        b = fresh()
        b.send("\x1bs")
        b.expect("spark>")
        b.send("fail\r")
        ok(b.expect("STUB-OPENING"), "a refusal shows in the buffer, not lost on stderr", b.plain()[-300:])
        b.send("B")
        b.send("Q")
        b.read(1.0)
        b.close()

        # E. Ctrl-C at the prompt is never mind: nothing runs, w3m lives
        b = fresh()
        b.send("\x1bs")
        b.expect("spark>")
        b.send("\x03")
        time.sleep(0.6)
        ok(not os.path.exists(log), "Ctrl-C at the prompt runs nothing")
        b.mark()
        b.send("B")                 # back: the page is still there
        ok(b.expect("gate"), "B returns to the page after the cancel", b.plain()[-200:])
        b.send("Q")
        b.read(1.0)
        b.close()

        # D. long lines wrap at spaces before w3m sees them (the wrapper's
        # fold): w3m shows piped text as it comes, one long line otherwise
        long_out = subprocess.run([os.path.join(bindir, "spark-w3m"), "long"],
                                  input=b"x", env=env, cwd=work,
                                  stdout=subprocess.PIPE).stdout.decode()
        ok(long_out.strip() and all(len(l) <= 78 for l in long_out.splitlines())
           and not any(l.endswith("wrapwo") for l in long_out.splitlines()),
           "a long answer wraps at spaces, at most 78 columns", repr(long_out[:100]))

        # E. the page on disk is untouched (a reader never writes)
        with open(page) as f:
            ok(f.read() == PAGE, "the page on disk is untouched")

    print("w3m_pty: %s" % ("all ok" if not fail else "%d FAILED" % fail))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())

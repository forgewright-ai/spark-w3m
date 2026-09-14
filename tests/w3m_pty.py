#!/usr/bin/env python3
# w3m_pty.py -- the spark page inside a real w3m, in a pty, against a
# stub `spark` (on PATH: the wrapper says `spark` plainly, and that is
# what must be proven) that logs what it was asked and answers a fixed
# shape per verb. Proves the room the snippet promises: M-s stashes the
# RENDERED page and opens the quiet front room (the S, the card, hello,
# the chat> field, overview / questions / part links -- nothing runs
# unasked); words are the conversation (spark edit ? --thread, the
# transcript re-rendered whole, so the page is the log); the empty q is
# the overview and part=N one part (spark read, framed); questions is
# spark ask, each question a link that asks itself; a quit word never
# reaches the model; and the buffer stack keeps its law -- B from an
# answer is the front room, B again is the page you were reading
# (DELETE_PREVBUF discipline: only requests marked from=chat replace
# their page). The test performs the README's install lines. Skips
# (exit 0) without w3m.
#
# Spike lessons (2026-09-14) baked in: w3m draws word by word and
# overdraws in a pty, so screen expectations match ONE short token and
# the STUB LOG is the ground truth; markers avoid hyphens.
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
# the stub spark: log argv and stdin, answer a fixed shape per verb.
# `read --ledger` answers two lines and never touches the log, so the
# quiet front room stays provably quiet while its card can still count.
if [ "${1-}" = read ] && [ "${2-}" = --ledger ]; then
    printf 'one old question\nanother old question\n'
    exit 0
fi
printf '%s\n' "$*" >> "$STUB_LOG"
cat > "$STUB_LOG.stdin"
case " $* " in
    *" fail "*)   printf 'spark: the source does not answer -- it opens: "STUBOPENING ..."\n' >&2; exit 1 ;;
    *" long "*)   i=0; while [ $i -lt 40 ]; do printf 'wrapword '; i=$((i+1)); done; printf '\n'; exit 0 ;;
esac
case ${1-} in
    edit) printf 'the page holds "held words" [not in the text] STUBEDIT' ;;
    ask)  printf 'ASKONE?\nASKTWO?\nASKTHREE?\n' ;;
    *)    printf 'STUBREAD\n' ;;
esac
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
        fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 30, 100, 0, 0))

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
               "SPARK_W3M_STASH": stash, "USER": "prover"}

        def logged():
            try:
                with open(log) as f:
                    return f.read()
            except OSError:
                return ""

        def clean():
            for p in (log, log + ".stdin", stash, stash + ".thread",
                      stash + ".name", stash + ".chat"):
                if os.path.exists(p):
                    os.unlink(p)

        def fresh(doc="page.html", token="gate"):
            clean()
            b = Browser([w3m, doc], env, work)
            ok(b.expect(token), "w3m draws the page")
            b.mark()
            return b

        def spark_room(b):
            b.send("\x1bs", 1.8)
            return b.expect("hello")

        def field_say(b, words):
            """the cursor is on the field (NEXT_LINK): edit, type, commit,
            Tab to [say], submit"""
            b.send("\r", 0.8)
            b.send(words, 0.5)
            b.send("\r", 0.8)
            b.send("\t", 0.4)
            b.send("\r", 2.0)

        # A. M-s opens the QUIET front room: the S, the card, hello, the
        # ways in; nothing runs; the stash and its siblings are private
        b = fresh()
        ok(spark_room(b), "M-s opens the front room (hello)", b.plain()[-300:])
        ok(b.expect("overview") and b.expect("questions"), "the ways in are on the room")
        ok(b.expect("######"), "the S masthead stands (ASCII fallback: the stub is no symlink)")
        ok(b.expect("asked"), "the card counts what was asked before (the ledger line)")
        with open(stash) as f:
            st = f.read()
        ok("Tickets are two dollars" in st and "<p>" not in st,
           "the RENDERED page is stashed, not the HTML", repr(st[:120]))
        ok(stat.S_IMODE(os.stat(stash).st_mode) == 0o600, "the stash is 0600")
        with open(stash + ".thread") as f:
            tid = f.read().strip()
        ok(tid.startswith("w3m-"), "a thread is minted at the stash", tid)
        with open(stash + ".name") as f:
            ok(f.read().strip() == "gate", "the page's title is kept for --name (W3M_TITLE)")
        ok(not os.path.exists(log), "the quiet room runs nothing unasked")
        b.close()

        # B. the overview link: the verdict law, framed; the front room
        # SURVIVES (its links carry no from=chat), so B walks
        # answer -> front -> the page
        b = fresh()
        spark_room(b)
        # NEXT_LINK already parked the cursor on the field: say, overview
        b.send("\t", 0.4); b.send("\t", 0.4)
        b.send("\r", 2.0)
        ok(b.expect("STUBREAD"), "the overview answers in a frame", b.plain()[-300:])
        got = logged()
        ok(got.strip() == "read --name gate",
           "the overview is spark read with the page's name, no path", got)
        b.mark()
        b.send("B", 1.2)
        ok(b.expect("hello", 6), "B from the verdict lands on the front room", b.plain()[-200:])
        b.mark()
        b.send("B", 1.2)
        ok(b.expect("Tickets", 6), "B again lands on the page itself", b.plain()[-200:])
        b.close()

        # C+H+I+K. the conversation: words run spark edit ? with the
        # thread and the about-hint; the second turn rides the SAME
        # thread (the hidden field) and REPLACES the first answer page
        # (from=chat -> DELETE_PREVBUF), while the page shows the whole
        # log; B is front, B is the page
        b = fresh()
        spark_room(b)
        field_say(b, "?does it mention prices")
        ok(b.expect("STUBEDIT"), "words answer as the conversation", b.plain()[-300:])
        lines = [l for l in logged().splitlines() if l.startswith("edit")]
        ok(len(lines) == 1 and lines[0].startswith("edit ? does it mention prices --thread w3m-")
           and "--about a published page" in lines[0] and "--name gate" in lines[0],
           "spark edit ? got the words, the thread, the about-hint and the name", logged())
        field_say(b, "and the fine print")
        time.sleep(1.0)
        lines = [l for l in logged().splitlines() if l.startswith("edit")]

        def tid_of(l):
            w = l.split()
            return w[w.index("--thread") + 1] if "--thread" in w else "?"
        ok(len(lines) == 2 and tid_of(lines[0]) == tid_of(lines[1]),
           "the follow-up rides the same thread", logged())
        ok(b.expect("prices") and b.expect("fine"),
           "the page is the log: both turns visible together", b.plain()[-400:])
        b.mark()
        b.send("B", 1.2)
        ok(b.expect("hello", 6) and "STUBEDIT" not in b.plain(),
           "B from the conversation lands on the front room, answers replaced",
           b.plain()[-250:])
        b.mark()
        b.send("B", 1.2)
        ok(b.expect("Tickets", 6), "B again lands on the page: two presses from any depth")
        b.close()

        # D. a page past 16000 chars: part links; part 2 reads part 2
        big = os.path.join(work, "big.html")
        with open(big, "w") as f:
            f.write("<html><head><title>big</title></head><body><p>bigword "
                    + "filler " * 3500 + "</p></body></html>")
        b = fresh("big.html", "bigword")
        b.send("\x1bs", 1.8)
        ok(b.expect("part"), "part links on a long page", b.plain()[-200:])
        for _ in range(5):
            b.send("\t", 0.3)
        b.send("\r", 2.0)
        time.sleep(0.5)
        ok(logged().strip() == "read --part 2 --name big",
           "the part 2 link reads part 2, named", logged())
        b.close()

        # E. a refusal shows on the page, stderr folded
        b = fresh()
        spark_room(b)
        field_say(b, "fail")
        ok(b.expect("STUBOPENING"), "a refusal shows on the page, not lost", b.plain()[-300:])
        b.close()

        # J. the questions room: spark ask on the stash; every question
        # is a link, and following one asks it in the conversation
        b = fresh()
        spark_room(b)
        # from the field: say, overview, questions
        b.send("\t", 0.4); b.send("\t", 0.4); b.send("\t", 0.4)
        b.send("\r", 2.0)
        ok(b.expect("ASKONE?"), "the questions room lists what the page does not answer",
           b.plain()[-300:])
        got = logged()
        ok(got.strip() == "ask --name gate", "the room is spark ask with the name", got)
        # NEXT_LINK lands on the first question link; follow it
        b.send("\r", 2.0)
        time.sleep(0.5)
        lines = [l for l in logged().splitlines() if l.startswith("edit")]
        ok(len(lines) == 1 and lines[0].startswith("edit ? ASKONE? --thread w3m-"),
           "a question link asks itself in the conversation", logged())
        b.close()

        # L. a quit word never reaches the model
        b = fresh()
        spark_room(b)
        field_say(b, "q")
        time.sleep(0.8)
        ok(b.expect("never"), "the quit page says the word never reaches spark")
        ok(not os.path.exists(log), "a quit word runs nothing")
        b.close()

        # M. staleness, driven at the CGI directly: a form from a page
        # that predates the newest M-s runs nothing
        clean()
        with open(stash, "w") as f:
            f.write("some stashed text\n")
        with open(stash + ".thread", "w") as f:
            f.write("w3m-1-1\n")
        with open(stash + ".name", "w") as f:
            f.write("gate\n")
        env2 = dict(env)
        env2["QUERY_STRING"] = "q=hi&t=w3m-9-9&from=chat"
        p = subprocess.run([os.path.join(bindir, "spark-w3m"), "--page"],
                           capture_output=True, text=True, env=env2)
        ok("moved on" in p.stdout and not os.path.exists(log),
           "a stale form runs nothing and says the stash moved on", p.stdout[-200:])

        # F. from a plain shell the wrapper takes the words directly,
        # and a long answer wraps at spaces
        clean()
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

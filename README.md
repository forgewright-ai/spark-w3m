# spark-w3m -- spark inside w3m

spark (https://spark.forgewright.ai) is your own AI on your own machine;
this plugin puts it under one key in w3m. The page you are reading is
piped to `spark read`, and the answer says only what the page says:
every line quotes it, and the quote is checked -- a claim the page does
not hold never reaches you. The first client of `spark read`, and the
first spark app outside the editors.

One key, spark's key in every app: `M-s` (Esc then s). `spark> `
appears at the bottom of the screen, and the grammar is the family's:

    Enter or ?         the overview: what does this page cover?
    your words         your question: does it mention prices? (a
                       leading ? works too, the editors' habit)
    --part 2 words     a page past 16 kB answers with its part count;
                       this reads part 2 (the answer names its part)
    Ctrl-C             never mind (the buffer stays empty; B goes back)

The answer opens in a new buffer; `B` goes back. When the page does not
answer, the reply is one line showing the page's own opening words --
never a guess.

## Install

You need spark 1.20 or newer on this machine (`spark read -h` answers),
and w3m 0.5.3 or newer (`w3m -version`). Then:

```sh
git clone https://github.com/forgewright-ai/spark-w3m ~/.w3m/spark
ln -s ~/.w3m/spark/spark-w3m ~/.local/bin/spark-w3m
cat ~/.w3m/spark/keymap.spark >> ~/.w3m/keymap
```

`spark-w3m` is the wrapper around `spark read` that draws the `spark> `
prompt (w3m cannot pre-fill its own), folds stderr into the answer, so
a refusal shows in w3m's buffer instead of vanishing, and wraps long
lines at spaces, so the buffer reads without sideways scrolling
(`SPARK_W3M_WIDTH` sets the column, default 78). From a plain shell the
same wrapper takes the words directly: `w3m -dump URL | spark-w3m your
words`. An update is `git -C ~/.w3m/spark pull`, then delete the old
spark lines from `~/.w3m/keymap` and append again. The comment block in
`keymap.spark` is the help; M-s is a suggestion -- edit the line to
taste (w3m's own M-s, save buffer, moves aside).

## What leaves this machine

The rendered page text -- 16 kB a part -- and your words, and only to
the brain spark is configured for. w3m's pipe carries no URL and no
file name, so not even that travels. Every run is one call to `spark
read` with the page on stdin; the plugin never speaks HTTP for itself
and never sees a token.

## Contributing

`git config core.hooksPath .githooks` once; the hook keeps the tree free
of private names, ASCII, and the payload keymap-only. `python3
tests/w3m_pty.py` drives a real w3m in a pty against a stub spark (skips
without w3m). Another reader joins spark the same way this one does: one
client of `spark read`, in its own repo.

MIT. Credits in `CREDITS.md`. Built with Claude.

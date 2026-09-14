# spark-w3m -- spark inside w3m

spark (https://spark.forgewright.ai) is your own AI on your own machine;
this plugin puts it under one key in w3m. `M-s` (Esc then s) stashes
the page you are reading and opens the spark page -- a small place
drawn by w3m itself, wearing spark's own S beside the page's card.
Nothing runs until you ask, and `B` always walks back sanely.

    chat> [field]      the conversation: follow-ups ride the thread
                       ("can you translate that?" has a that), the
                       page re-renders as the whole log, and a quote
                       the page does not hold is marked
                       [not in the text], never silenced
    overview           a link: what does this page cover? -- the
                       verdict law: every line quotes the page, or an
                       honest refusal, in a frame
    questions          a link: what does this page NOT answer? -- at
                       most three, and each question is itself a link
                       that asks it in the conversation
    part 1 . part 2    links, on a page past 16 kB: read one part
    q, :q, quit...     said to the field: toward the page -- a quit
                       word never reaches the model
    B                  from an answer, the front room; again, the
                       page itself -- two presses from any depth

While the model works, the bottom row says so: `reading N characters
| 12s` the first time, `thinking | 6s` on the turns after. The card
counts what was asked of this page before (spark's reading ledger).

## Install

You need spark 1.20 or newer on this machine (`spark read -h` and
`spark ask -h` answer), and w3m 0.5.3 or newer (`w3m -version`). Then:

```sh
git clone https://github.com/forgewright-ai/spark-w3m ~/.w3m/spark
ln -s ~/.w3m/spark/spark-w3m ~/.local/bin/spark-w3m
cat ~/.w3m/spark/keymap.spark >> ~/.w3m/keymap
printf 'cgi_bin %s/.w3m/spark\n' "$HOME" >> ~/.w3m/config
```

The spark page is w3m's own local CGI (`spark.cgi` in this clone --
the `cgi_bin` line points w3m at it); `spark-w3m` is the wrapper
behind it, and from a plain shell it reads any text directly:
`w3m -dump URL | spark-w3m your words`. An update is `git -C
~/.w3m/spark pull`, then delete the old spark lines from
`~/.w3m/keymap` and append again. The comment block in `keymap.spark`
is the help; M-s is a suggestion (w3m's own M-s, save buffer, moves
aside) -- edit the line to taste. The keys, and what to ask:
`CHEATSHEET.md`.

The masthead is spark's own banner, read from your local spark
install at runtime (`~/.config/spark/banner`, else the spark clone)
-- the first eight columns, the S. On the Linux console, or when no
banner is found, a plain-ASCII S stands in;
`SPARK_W3M_MASTHEAD=s|word|none` overrides.

## What leaves this machine

The rendered page text -- 16 kB a part, 12 kB to the questions room
-- and your words, and only to the brain spark is configured for. No
URL and no file name travels. The stash, its thread, its title and
its transcript rest on this machine between question and follow-up
(files of yours alone, 0600, your runtime directory; the next M-s
replaces them, logout removes them). Every run is one call to `spark
edit`, `spark read` or `spark ask`; the plugin never speaks HTTP for
itself and never sees a token.

## Contributing

`git config core.hooksPath .githooks` once; the hook keeps the tree free
of private names, ASCII, and the payload keymap-only. `python3
tests/w3m_pty.py` drives a real w3m in a pty against a stub spark (skips
without w3m). Another reader joins spark the same way this one does: one
client of `spark read`, in its own repo.

MIT. Credits in `CREDITS.md`. Built with Claude.

# spark-w3m -- spark inside w3m

spark (https://spark.forgewright.ai) is your own AI on your own machine;
this plugin puts it under one key in w3m. `M-s` (Esc then s) stashes
the page you are reading and opens the spark page -- a page like any
other, drawn by w3m itself: a `spark> ` form field, an `overview`
link, part links when the page is long. Nothing runs until you ask.
The answer says only what the page says -- every line quotes it, and
the quote is checked; a claim the page does not hold never reaches
you. The first client of `spark read`.

    spark> [field]     your question: type, Enter, ask ("does it
                       mention prices"; a leading ? works too)
    overview           a link: what does this page cover?
    part 1 . part 2    links, on a page past 16 kB: read one part
    B                  never mind -- back to the page you were reading

The answer is a page too, the field repeated below it for the
follow-up. When the page does not answer, the reply is one line
showing its own opening words -- never a guess. While the model
reads, the bottom row says so: `spark reads N characters | 12s`.

## Install

You need spark 1.20 or newer on this machine (`spark read -h`
answers), and w3m 0.5.3 or newer (`w3m -version`). Then:

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

## What leaves this machine

The rendered page text -- 16 kB a part -- and your words, and only to
the brain spark is configured for. No URL and no file name travels.
The stashed text rests on this machine between question and follow-up
(one file, 0600, your runtime directory; the next M-s replaces it).
Every run is one call to `spark read`; the plugin never speaks HTTP
for itself and never sees a token.

## Contributing

`git config core.hooksPath .githooks` once; the hook keeps the tree free
of private names, ASCII, and the payload keymap-only. `python3
tests/w3m_pty.py` drives a real w3m in a pty against a stub spark (skips
without w3m). Another reader joins spark the same way this one does: one
client of `spark read`, in its own repo.

MIT. Credits in `CREDITS.md`. Built with Claude.

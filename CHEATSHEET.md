# w3m with spark -- the cheatsheet

w3m browses; spark reads. Section 1 is w3m on its own, section 2 is
the one key that turns the page you are reading into something you
can question.

The key spellings here are w3m's: `M-s` means Meta-s -- hold Alt and
press s, or press Esc and then s; both send the same thing. `Esc b`
is the same idea written out. Keys are case-sensitive: `b` and `B`
do different things.

## 1. w3m, the basics

Going somewhere

    U              open a URL (or edit the current one)
    Enter          follow the link under the cursor
    Tab / Esc Tab  next / previous link
    B              back to the previous page
    s              the open pages -- pick one to return to
    Esc b          bookmarks
    Esc a          bookmark this page

Moving around a page

    Space / b      page down / page up
    h j k l        move the cursor
    g / G          top / bottom of the page
    /words Enter   search -- then n next match, N previous

Reading with care

    u              peek the URL under the cursor before following it
    c              show this page's URL
    v              view the raw HTML (v again to come back)
    R              reload

Tabs

    T              new tab
    { / }          previous / next tab
    Ctrl-q         close this tab

Leaving and help

    q              quit (asks first); Q quits without asking
    H              w3m's full key reference
    o              the options page

## 2. the page, with spark

One key: M-s. The page you are reading is stashed and the spark page
opens -- a page like any other, drawn by w3m itself. Nothing runs
until you ask, and B is always the way back.

    spark> [field]   your question: Tab to the field, Enter to type,
                     Enter again, then Tab to [ask] and Enter
    overview         a link: what does this page cover?
    part 1 . part 2  links, on a page past 16 kB: read one part
    B                never mind, or back from an answer

By example

    an article     M-s, overview
                   what it covers, before you commit to reading it all
    a long read    M-s, spark> does it mention pricing
                   the answer quotes the lines that do
    a manual       M-s -- the part links appear; part 3, then ask away
    a follow-up    the answer page carries the field again: ask right
                   there, B walks back through the exchange

While the model reads, the bottom row counts: `spark reads N
characters | 12s`. Every answer line quotes the page; when the page
does not hold the answer, the reply is one line showing the page's
own opening words -- never a guess.

From a plain shell, the same wrapper reads any text:

    w3m -dump URL | spark-w3m your words

With the plugin installed, M-s belongs to spark; w3m's own M-s (save
source) moves aside -- edit the line in `~/.w3m/keymap` to taste.

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
opens -- a small place drawn by w3m itself, spark's S beside the
page's card. Nothing runs until you ask; B always walks back.

    chat> [field]    the conversation: Tab lands you on it (the
                     cursor starts there), Enter to type, Enter,
                     then [say]. Follow-ups ride the same thread;
                     the page re-renders as the whole log
    overview         a link: what does this page cover? every line
                     quotes the page, or an honest refusal, framed
    questions        a link: what does this page NOT answer? each
                     question is a link that asks itself
    part 1 . 2       links, past 16 kB: read one part
    q, :q, quit      said to the field: a quit word never reaches
                     the model
    B                from an answer, the front room; again, the
                     page itself -- two presses from any depth

By example

    an article     M-s, overview
                   what it covers, before you commit to reading
    a claim        M-s, chat> does it name a source for the numbers
    a critique     M-s, questions -- what the page left unanswered,
                   each one a click from being asked
    a follow-up    the field is on every answer page: just keep
                   talking; "translate that" knows what that is
    a manual       M-s -- part links appear; part 3, then ask away

While the model works the bottom row counts: `reading N characters
| 12s` first, `thinking | 6s` after. The card remembers: "asked
before: N" is spark's reading ledger for this page.

From a plain shell, the same wrapper reads any text:

    w3m -dump URL | spark-w3m your words

The masthead is spark's own banner S, borrowed from your spark
install; a plain-ASCII S stands in on the console
(SPARK_W3M_MASTHEAD=s|word|none overrides). With the plugin
installed, M-s belongs to spark; w3m's own M-s (save source) moves
aside -- edit the line in `~/.w3m/keymap` to taste.

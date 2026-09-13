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

One key: M-s (Esc then s). The page stays put and `spark> ` appears
at the bottom of the screen. What you type there is `spark read`'s
grammar; the answer opens in a new buffer, every line quoting the
page, and B goes back.

    Enter or ?     the overview: what does this page cover?
    your words     your question (a leading ? works too)
    --part 2 words a page past 16 kB answers with its part count;
                   this asks part 2
    Ctrl-C         never mind -- the buffer stays empty, B goes back

By example

    an article     M-s, Enter
                   the overview, before you commit to reading it all
    a long read    M-s, does it mention pricing
                   the answer quotes the lines that do
    a changelog    M-s, what changed in the newest release
    a manual       M-s, Enter answers "part 1 of 3 ..." -- then
                   M-s, --part 3 how do I uninstall

When the page does not hold the answer, the reply is one line showing
the page's own opening words -- never a guess. That is the design:
spark read says only what the page says.

From a plain shell, the same wrapper takes the words directly:

    w3m -dump URL | spark-w3m your words

With the plugin installed, M-s belongs to spark; w3m's own M-s (save
source) moves aside -- edit the line in `~/.w3m/keymap` to taste.

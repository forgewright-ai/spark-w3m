# Changelog

## 2.1.1

- The conversation asks in the reading-discussion posture. spark 1.32
  gained `spark edit ? --source` -- the page is a published source you
  discuss, not a draft you edit -- and the wrapper passes it, guarded,
  so an older spark is unchanged. The verbose about-hint shrinks to "a
  web page"; the overview, parts and questions rooms are untouched
  (they are spark read and spark ask, not the conversation).

## 2.1.0

- The spark page becomes a place. The front room greets with spark's
  own S (the banner's first eight columns, read from your spark
  install at runtime; a plain-ASCII S on the console or without one)
  beside the page's card, hello, and the ways in.
- The conversation: words in the `chat>` field run `spark edit ?`
  with a per-stash thread -- follow-ups ride the earlier turns, the
  transcript is kept beside the stash, and the page re-renders as
  the whole log. An unheld quote is marked where it stands.
- The questions room: `spark ask` on the page -- at most three
  questions the page does not answer, each one a link that asks
  itself in the conversation.
- The verdict stays the verdict: overview and part links run `spark
  read`, the answer framed; a refusal is a first-class verdict. The
  overview and parts record under the page's title in spark's
  reading ledger, and the card says "asked before: N".
- One room, one buffer: an answer page's next request replaces it
  (W3m-control: DELETE_PREVBUF -- probed), so B from an answer is
  the front room and B again is the page: two presses from any
  depth. The cursor lands on the field (NEXT_LINK -- probed).
- The family's quit grammar at the field: q, :q, quit and the rest
  never reach the model.
- The wait speaks: `reading N characters` the first time, `thinking`
  after, spinner and seconds on the bottom row.
- Probed and honestly out: a textarea's $EDITOR handoff hangs w3m
  under a pty (the long-question room is parked); a headers-only
  BACK response does not act; w3m renders no color from HTML.

## 2.0.1

- The form fits an 80-column console: the field is 40 wide, so
  `spark> [ field ] [ask]` stays one line instead of wrapping into a
  shredded bracket row with the overview link pulled through it.

## 2.0.0

- The spark page. M-s stashes the rendered page and opens a page of
  w3m's own: a spark> form field, an overview link, part links past
  16 kB -- quiet, nothing runs unasked. A question answers as a page
  carrying the field again, so the follow-up lives where the answer
  is; B walks back. The 1.x terminal prompt is gone, and with it the
  whole disease it carried: two programs drawing on one screen. The
  install gains one line (cgi_bin in ~/.w3m/config); the stash rests
  0600 in the runtime dir, replaced by the next M-s, and no URL or
  path travels, as ever. The bottom-row pulse stays while the model
  reads.

## 1.2.0

- The wait says what it is, on the one row this wrapper may touch:
  after the question, the bottom row shows `spark reads N characters
  | 12s` -- an ASCII spinner and the seconds, absolute addressing,
  never a newline -- cleared when the answer buffer is ready. w3m
  shows a piped buffer only at its end (measured), so the spinner
  runs the whole wait. The same pulse spark-newsboat wears.

## 1.1.2

- The Enter at the prompt scrolled the screen. The bottom row's echoed
  newline moved everything up one line behind w3m's back, and every
  repaint after was one row off (doubled lines, the answer over the
  page). The prompt now reads keys raw and echoes them itself --
  backspace edits, Ctrl-C still cancels, and the Enter is swallowed:
  no newline ever reaches the tty. From the maintainer's session at
  the box console, photos in hand.

## 1.1.1

- The prompt homes to the screen's last row. w3m leaves the cursor
  anywhere when it runs the pipe command -- on the console, top-left,
  so `spark> ` printed over the page's first line. The wrapper now
  addresses the bottom row and clears it before drawing; the pty test
  asserts the position. From the maintainer's first session at the
  box console.

## 1.1.0

- One key, one grammar. M-a is gone; M-s now opens `spark> ` on the
  screen (the wrapper draws it on the terminal while w3m waits -- w3m
  cannot pre-fill its own prompt): Enter or `?` alone is the overview,
  words are the question (a leading `?` stripped, the editors' habit;
  globs stay literal), `--part 2 words` rides, Ctrl-C cancels into an
  empty buffer (B goes back; w3m stops reading its stream on the same
  SIGINT, so no goodbye line can land there). Nobody types `spark-w3m`
  inside w3m any more. From the maintainer's first real session: the
  two keys read press-after vs press-before, and w3m's bare pipe
  prompt hinted nothing.

## 1.0.2

- The wrapper wraps long lines at spaces (`fold -s`, `SPARK_W3M_WIDTH`,
  default 78): w3m shows piped text as it comes, so an answer used to
  land as one long line to scroll sideways. Found reading a real answer
  under M-s.

## 1.0.1

- The wrapper ships executable. 1.0.0's `spark-w3m` had no execute bit:
  the pty test chmod'd its own copy and so proved a file nobody ships;
  it now symlinks the repo's file as the README installs it, so the bit
  is part of what the test proves. Found on the box, the first real
  install.

## 1.0.0

- The first release: the page under M-s goes to `spark read` (the
  overview), M-a takes a question at w3m's pipe prompt, and the
  `spark-w3m` wrapper folds spark's stderr into the answer so a refusal
  or a part count shows in the buffer. The first client of `spark read`
  (spark 1.20), proven by a pty test against a real w3m on Ubuntu, Arch
  and macOS.

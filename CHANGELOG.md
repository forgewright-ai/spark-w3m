# Changelog

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

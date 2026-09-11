# Changelog

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

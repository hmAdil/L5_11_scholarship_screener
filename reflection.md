# Lab 5 Reflection

## 1. Which issues were easiest and which were hardest to fix?

The easiest were the mechanical ones: unused imports, `== True`, the `printShortlist` name, `%` formatting, missing docstrings and blank-line spacing. Each one has a single obvious correct fix, and the tool tells you exactly where it is.

The hardest was `eval`. Deleting it was easy, but the program has a feature where the user types a custom merit formula, so removing `eval` outright would have removed the feature. I had to write a small AST-based evaluator that only accepts numbers, the names `gpa` and `credits`, and the operators `+ - * /`, then validate any new formula before accepting it. The mutable default `logs=[]` and the `global` statements were in the middle: simple to fix, but they required understanding why they are risky rather than just silencing the warning.

## 2. Did the tools report any false positives or misleading findings?

Mostly no, every finding pointed at something real. A few were indirect or imprecise, though. Pylint's W0613 (unused arguments `gpa` and `credits`) was a side effect of `eval`, since the arguments were only used through a string, so it disappeared once `eval` was gone. Bandit labelled the `eval` finding with CWE-78 (OS command injection), while the more precise description is code injection, but the severity and the advice were still right. Bandit rated the `try/except/pass` as only Low, but it was hiding real errors, so the low severity understated how much it mattered for debugging. Pylint's C0121 suggested `is True` as one option, but plain truthiness (`if record["eligible"]:`) is the better fix.

## 3. What did the tools miss?

Quite a lot of the real behaviour bugs were invisible to all three tools. U003 (GPA 12.5, credits -3, income -1) scored 119 and was shortlisted because nothing validated the input. U004 had no income and was silently treated as zero income. The custom formula was applied halfway through the run, so the shortlist mixed scores from two different formulas. I only found these by running the program and reading the output carefully. Static analysis checks how code is written, not whether it does the right thing, so it complements testing and review and does not replace them.

## 4. How would I use static analysis in a real workflow?

I would run Flake8 and Pylint locally or as a pre-commit hook so style and basic errors never reach review, and run Bandit plus Pylint in CI on every pull request. Bandit findings of Medium severity or above would block a merge, and Pylint would have a minimum score threshold, like the 9.5 target in this lab. That keeps reviewers focused on design and logic instead of spacing and naming. I would also add unit tests for input validation, since the tools cannot catch those.

## 5. What improved after the fixes?

Bandit went from 2 issues (1 Medium, 1 Low) to 0. Pylint went from 26 messages and 4.69/10 to 0 messages and 10.00/10. Flake8 went from 12 findings to 0. Beyond the numbers, the program is safer (typed code at the formula prompt is no longer executed), more robust (invalid applicants are rejected with a reason instead of being shortlisted), easier to follow (no global rebinding, documented functions) and importable without side effects because `main()` is behind an `if __name__ == "__main__":` guard.
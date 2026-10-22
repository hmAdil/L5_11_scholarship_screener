# Lab 5: Static Analysis Issues, Scholarship Screener

## Summary

| Tool | Before | After |
| ---- | ------ | ----- |
| Bandit | 2 issues (1 Medium, 1 Low) | 0 issues |
| Pylint | 4.69/10 | 10.00/10 |
| Flake8 | see reports/before/flake8_report.txt | 0 issues |

## Issue table

| Issue | Type | Line(s) | Description | Fix Approach |
| ----- | ---- | ------- | ----------- | ------------ |
| eval on user-controlled string | Security (Bandit B307, Medium) | 12 | `calculate_merit_score` evals a formula that `main()` reads from `input()`, so typing code at the prompt executes it | Replaced with an AST-based evaluator that only allows numbers, `gpa`, `credits` and `+ - * /`; invalid formulas are rejected and the default is kept |
| try/except/pass with bare except | Security/Bug (Bandit B110, Low; Pylint W0702; Flake8 E722) | 35-38 | Any error while loading results is silently swallowed, including `KeyboardInterrupt` | Catch only `OSError` and `json.JSONDecodeError` and print a message |
| Mutable default argument | Bug (Pylint W0102) | 14 | `logs=[]` is created once and shared across every call | Default to `None` and create a new list inside the function |
| No input validation | Logic bug (no tool flags it) | 14-22, 49 | U003 (GPA 12.5, credits -3, income -1) scored 119 and was shortlisted | Added `validate_scores`, which raises `ValueError` for GPA outside 0-10, negative credits and negative income |
| Missing income treated as zero | Logic bug (no tool flags it) | 17, 50 | U004 has no income and silently counted as zero income | Income is now required; a missing value is rejected |
| Formula changed mid-run | Logic bug (no tool flags it) | 47-54 | U001-U004 were scored with the default formula and U005 with the custom one, so the shortlist mixed two formulas | The formula is requested first, then all applicants are scored together |
| Global statements | Design (Pylint W0603) | 25, 34 | Rebinding module globals makes state hard to follow | Mutate `RESULTS` in place and keep the formula in a `SETTINGS` dict |
| File handling without `with` or encoding | Bug risk (Pylint R1732, W1514) | 29-31, 36 | The handle leaks if the write fails and the encoding depends on the platform | `with open(..., encoding="utf-8")` plus `json.dump` and `json.load` |
| Unused imports | Style (Pylint W0611; Flake8 F401) | 2-3 | `math` and `sys` are never used | Removed |
| Non-snake_case function name | Style (Pylint C0103) | 40 | `printShortlist` | Renamed to `print_shortlist` |
| Comparison to True | Style (Pylint C0121; Flake8 E712) | 43 | `== True` is redundant | `if record["eligible"]:` |
| Old-style string formatting | Style (Pylint C0209) | 21 | `%` formatting | f-string |
| Missing docstrings | Style (Pylint C0114, C0116) | module-wide | No module or function documentation | Added short docstrings |
| Blank-line spacing and `main()` at import | Style (Flake8 E302, E305) | module-wide | Wrong spacing between definitions, and `main()` runs on import | Two blank lines between top-level blocks and an `if __name__ == "__main__":` guard |
| Missing final newline | Style (Pylint C0304; Flake8 W292) | end of file | File did not end in a newline | Added the newline |
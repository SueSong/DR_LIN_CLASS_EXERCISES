# Exercise 3 — Python Scope Checker

This checker finds common, runtime-crashing scope bugs that LLMs often produce:
- EUL001: Possible UnboundLocalError (read before local assignment)
- EUL002: Augmented assignment may read before assignment (use global/nonlocal or assign earlier)
- ENL001: nonlocal without a binding in any enclosing function scope
- ECV001: Class attribute accessed without qualifier inside a method

## Quick start

```bash
cd /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_3
python checker.py examples.py
```

Exit code is nonzero if any issues are found.

## Check a project

```bash
python checker.py /path/to/your/project
```

## Notes
- The checker uses Python's AST. It does not execute code.
- It's conservative and aims to minimize false negatives for the listed patterns.
- You can integrate it into CI by checking the exit code.

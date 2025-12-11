---
name: Bug report
about: Report a bug in sped-parser-br
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description

A clear and concise description of what the bug is.

## To Reproduce

Steps to reproduce the behavior:

```python
from sped_parser_br import EFDContribuicoesParser

parser = EFDContribuicoesParser()
data = parser.parse_file("myfile.txt")
# ... code that reproduces the bug
```

## Expected Behavior

A clear description of what you expected to happen.

## Actual Behavior

What actually happened.

## Error Message

```
Paste the full error traceback here
```

## Environment

- **sped-parser-br version**: (run `pip show sped-parser-br`)
- **Python version**: (run `python --version`)
- **OS**: (e.g., macOS 14.1, Ubuntu 22.04, Windows 11)
- **pandas version**: (run `pip show pandas`)

## Additional Context

Add any other context about the problem here (e.g., file size, specific SPED file type, etc.)

## Sample File (if possible)

If you can share a sample SPED file that reproduces the issue (anonymized/sanitized), please attach it or provide a link.

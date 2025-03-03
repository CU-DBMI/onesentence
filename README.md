# pre-commit-semantic-line-breaks

A [Pre-commit](https://pre-commit.com/) hook for [semantic line breaks](https://sembr.org/) (also called 'one sentence per line').

## Installation

Install this pre-commit hook into your project with a block like the following:

```yaml
repos:
  - repo: https://github.com/d33bs/pre-commit-semantic-line-breaks
    rev: v0.0.1
    hooks:
        - id: sembr-check
```

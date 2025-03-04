# pre-commit-semantic-line-breaks

A [Pre-commit](https://pre-commit.com/) hook for checking 'one sentence per line' documentation practices.

## Installation

Install this pre-commit hook into your project with a block like the following:

```yaml
repos:
  - repo: https://github.com/d33bs/pre-commit-one-sentence
    rev: v0.0.1
    hooks:
        - id: onesentence-check
```

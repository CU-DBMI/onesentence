# `onesentence`

A [Pre-commit](https://pre-commit.com/) hook for checking 'one sentence per line' documentation practices.

## Usage

The `onesentence` tool provides a command-line interface for checking and fixing files to ensure they follow the "one sentence per line" rule.

#### Commands

```bash
  onesentence check <file_path>
```

This command checks if the specified file adheres to the "one sentence per line" rule. It will return a non-zero exit code if any violations are found.

```bash
  onesentence fix <file_path> [<dest_path>]
```

This command corrects the specified file by splitting lines with multiple sentences into separate lines. If a dest_path is provided, the corrected file will be written to that path; otherwise, the original file will be overwritten.

## Pre-commit

Install this pre-commit hook into your project with a block like the following:

```yaml
repos:
  - repo: https://github.com/d33bs/pre-commit-one-sentence
    rev: v0.0.1
    hooks:
        - id: onesentence-check
```

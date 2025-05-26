# `onesentence`

[![Build Status](https://github.com/cu-dbmi/onesentence/actions/workflows/run-tests.yml/badge.svg?branch=main)](https://github.com/cu-dbmi/onesentence/actions/workflows/run-tests.yml?query=branch%3Amain)
![Coverage Status](https://raw.githubusercontent.com/cu-dbmi/onesentence/main/docs/src/_static/coverage-badge.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

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
  - repo: https://github.com/CU-DBMI/onesentence
    rev: v0.0.1
    hooks:
        # run checks
        - id: check
        # run checks and fixes where possible
        - id: fix
```

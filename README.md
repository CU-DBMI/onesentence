# `onesentence`

![PyPI - Version](https://img.shields.io/pypi/v/onesentence)
[![Build Status](https://github.com/cu-dbmi/onesentence/actions/workflows/run-tests.yml/badge.svg?branch=main)](https://github.com/cu-dbmi/onesentence/actions/workflows/run-tests.yml?query=branch%3Amain)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Software DOI badge](https://zenodo.org/badge/DOI/10.5281/zenodo.15521186.svg)](https://doi.org/10.5281/zenodo.15521186)

A [Pre-commit](https://pre-commit.com/) hook for checking 'one sentence per line' documentation practices.

One sentence per line is a practice where developers use only one line per sentence.
This can make it easier to review or provide comments on in version control systems like `git`.
That said, it can sometimes be difficult to remember or "debug" this style preference.
We provide this linting tool to assist with finding and fixing areas of content where the style preference is one sentence per line.

## Installation

Install `onesentence` from [PyPI](https://pypi.org/) or from source.
Also reference the [pre-commit hook](#pre-commit-hook) instructions for use through [pre-commit](https://pre-commit.com/).

```shell
# install from pypi
pip install onesentence

# install directly from source
pip install git+https://github.com/CU-DBMI/onesentence.git
```

## Usage

The `onesentence` tool provides a command-line interface for checking and fixing files to ensure they follow the "one sentence per line" rule.

#### Commands

```bash
  onesentence check <file_path> [<file_path> ...]
```

This command checks whether each given file adheres to the "one sentence per line" rule.
One or more files may be passed (for example, the filenames pre-commit hands to a hook).
It returns a non-zero exit code if any file has a violation.

```bash
  onesentence fix <file_path> [<file_path> ...] [--output <path>]
```

This command corrects each given file by splitting lines with multiple sentences onto separate lines.
By default every file is corrected in place, so processing many files never lets one file overwrite another.
Pass `--output <path>` to write a single corrected file to a separate destination; this is only valid with exactly one input file.
It returns a non-zero exit code if any file required changes.

## Pre-commit hook

Install this pre-commit hook into your project with a block like the following:

```yaml
repos:
  - repo: https://github.com/CU-DBMI/onesentence
    rev: v0.1.1
    hooks:
        # run checks
        - id: check
        # run checks and fixes where possible
        - id: fix
```

### Using onesentence with a Markdown formatter

If you also run a Markdown formatter such as
[`mdformat`](https://github.com/executablebooks/mdformat), configure it to
preserve existing line breaks so it does not undo the one-sentence-per-line
splitting.
For `mdformat` this means using `--wrap=keep` (the default), and notably **not**
`--wrap=no` or a fixed wrap width, either of which would rejoin sentences onto a
single line.

```yaml
  - repo: https://github.com/executablebooks/mdformat
    rev: 0.7.22
    hooks:
        - id: mdformat
          args: ["--wrap=keep"]
```

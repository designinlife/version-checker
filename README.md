# Project version-checker

![GitHub CI](https://github.com/designinlife/version-checker/actions/workflows/ci.yml/badge.svg)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Python](https://img.shields.io/badge/language-python-green.svg)](https://www.python.org/)

## Usage

```bash
curl -sSL --fail https://raw.githubusercontent.com/designinlife/version-checker/main/data/all.json | jq
```

## Add Source

```bash
poetry source add --priority=default PyPi https://pypi.org/simple/
```

## Build wheel

```bash
poetry build -f wheel
```

## Run

```bash
poetry run version-checker inspect
```

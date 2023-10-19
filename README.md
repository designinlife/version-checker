# Project version-checker

![GitHub CI](https://github.com/designinlife/version-checker/actions/workflows/ci.yml/badge.svg)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fdesigninlife%2Fversion-checker%2Fmain%2Fpyproject.toml)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

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

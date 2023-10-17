# Project version-checker

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

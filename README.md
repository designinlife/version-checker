# Project version-checker

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

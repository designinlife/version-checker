.PHONY: debug build tidy release deploy clean tool lint help

.DEFAULT_GOAL=inspect
.ONESHELL:

name := version-checker
version := 1.0.0
date := $(shell date '+%Y-%m-%d %H:%M:%S')

tidy:

inspect: clean tidy
	@rm -f uv.lock
	@uv sync --default-index=https://pypi.org/simple
	@uv run version-checker inspect

lint:

clean:
	@rm -rf dist/*

help:
	@echo "make: compile packages and dependencies"
	@echo "make tool: run specified python tool"
	@echo "make lint: pylint ./..."
	@echo "make clean: remove object files and cached files"
	@echo "make release: release binary."

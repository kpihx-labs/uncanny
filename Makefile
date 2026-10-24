SHELL := /bin/zsh
.DEFAULT_GOAL := help
BACKEND ?= xpu
.PHONY: install test bench bench-json bench-fast clean help check push puhsb uv-build uv-publish uv-link

install:
	uv sync --extra dev

test:
	uv run --extra dev python -m pytest tests/ -v

bench:
	uv run uncanny bench

bench-json:
	uv run uncanny bench --json

bench-fast:
	uv run uncanny bench --analyzers compression

clean:
	rm -rf .pytest_cache __pycache__ src/uncanny/__pycache__ .venv dist build *.egg-info

help:
	@echo "install install-ml test bench bench-json bench-fast clean check push puhsb uv-build uv-publish uv-link uv-link-ml"

.PHONY: install-ml uv-link-ml
install-ml:
	uv sync --extra ml --extra $(BACKEND)

uv-link-ml:
	uv tool install --editable ".[ml,$(BACKEND)]" --force

check: test
	uv run python -m compileall -q src

push:
	@set -e; branch=$$(git branch --show-current); for remote in github gitlab; do git push "$$remote" "$$branch"; done

puhsb: push

uv-build:
	@if [ -d dist ]; then rm dist; fi
	uv build --no-sources

uv-publish: uv-build
	uv publish dist/*

uv-link:
	uv tool install --editable . --force

SHELL := /bin/zsh
.DEFAULT_GOAL := help
.PHONY: install test bench bench-json bench-fast lint clean update-homebrew help check push puhsb uv-build uv-publish uv-link

install:
	uv sync --extra dev

test:
	uv run --extra dev pytest tests/ -v

bench:
	uncanny bench

bench-json:
	uncanny bench --json

bench-fast:
	uncanny bench --analyzers compression

update-homebrew:
	./scripts/update-homebrew.sh $(VERSION)

clean:
	rm -rf .pytest_cache __pycache__ src/uncanny/__pycache__ .venv dist build *.egg-info

help:
	@echo "install test bench bench-json bench-fast clean check push puhsb uv-build uv-publish uv-link"

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

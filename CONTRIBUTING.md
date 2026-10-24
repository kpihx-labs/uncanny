# Contributing to Uncanny

Thanks for your interest in contributing! This document covers the basics.

## Development Setup

```bash
git clone git@github.com:kpihx-labs/uncanny.git
cd uncanny
uv sync --extra dev
```

For optional ML dependencies, choose exactly one hardware profile:

```bash
make install-ml BACKEND=xpu
# Or BACKEND=cpu / BACKEND=cuda. Do not combine hardware extras.
```

## Running Tests

```bash
make test           # run all tests
make bench          # run benchmarks
make bench-fast     # compression-only benchmark
```

## Project Structure

```
src/uncanny/
├── analyzers/       # Detection methods (compression, perplexity, burstiness)
├── bench/           # Benchmark runner, display, competitor comparison
├── output/          # Terminal and JSON output formatters
├── cli.py           # Typer CLI commands
├── ensemble.py      # Weighted score combination
├── tokenizer.py     # Sentence splitting
└── types.py         # Core data types

benchmarks/corpus/   # Labeled test samples (ai/ and human/)
tests/               # Unit and regression tests
```

## Adding a New Analyzer

1. Create `src/uncanny/analyzers/your_analyzer.py`
2. Subclass `Analyzer` from `analyzers/base.py`
3. Implement the `analyze(text: str) -> AnalyzerResult` method
4. Register it in `analyzers/__init__.py` and `cli.py`
5. Add a default weight in `ensemble.py`
6. Add tests and benchmark corpus samples if needed

## Adding Corpus Samples

Put `.txt` files in `benchmarks/corpus/ai/` or `benchmarks/corpus/human/`. Each file should be 100-200 words of representative text. Run `make bench` to verify accuracy doesn't regress.

## Pull Requests

- One feature/fix per PR
- Tests must pass (`make test`)
- Benchmark accuracy must not regress below 70% (enforced by `test_bench.py`)
- Keep commits focused and messages clear

## Code Style

- Python 3.10+ with `from __future__ import annotations`
- No unnecessary abstractions — keep it simple
- Type hints on function signatures
- Tests for new functionality

## Reporting Issues

Open an issue on GitHub with:
- What you expected vs what happened
- Sample text that triggered the issue (if applicable)
- Output of `uncanny version`

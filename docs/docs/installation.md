---
sidebar_position: 2
title: Installation
---

# Installation

## UV tool installation (recommended)

```bash
uv tool install k-uncanny
```

## Project environment

```bash
uv sync --extra dev
```

## Editable isolated installation

```bash
make uv-link
```

## From source

```bash
git clone git@github.com:kpihx-labs/uncanny.git
cd uncanny
make install
```

## Optional: ML Dependencies

For the perplexity analyzer (`--deep` mode), install ML dependencies:

```bash
uv tool install 'k-uncanny[ml,xpu]' --index https://download.pytorch.org/whl/xpu
# For CPU, use [ml,cpu] with https://download.pytorch.org/whl/cpu.
# From a checkout: make uv-link-ml BACKEND=xpu
```

This downloads `torch` and `transformers` (~2GB). The perplexity analyzer uses GPT-2 small (~500MB model, downloaded on first use).

:::tip
The default analyzers (compression + burstiness) require **zero additional downloads** and work instantly. Only install ML deps if you want `--deep` mode.
:::

## Verify Installation

```bash
uncanny --version
# uncanny 0.1.0

uncanny scan --text "Hello world" --format summary
# 0.38 (likely_human)
```

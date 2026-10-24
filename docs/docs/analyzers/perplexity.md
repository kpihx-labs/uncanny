---
sidebar_position: 4
title: Perplexity
---

# Perplexity Analyzer

Measures how "surprised" a language model is by the text. AI-generated text has low perplexity (the model predicted it easily). Human text has high perplexity (surprising word choices).

:::note
This analyzer requires optional ML dependencies and an explicit hardware profile:
`make uv-link-ml BACKEND=xpu` from the checkout (or `BACKEND=cpu`).
:::

## How It Works

1. **Load GPT-2 small** — a ~500MB language model (downloaded on first use)
2. **Compute perplexity** — for each sentence, calculate the exponential of the cross-entropy loss
3. **Score** — map perplexity to a 0-1 scale using a log-scale sigmoid

## Perplexity Explained

Perplexity measures how well a language model predicts the next token. Lower perplexity = more predictable text.

- **AI text**: perplexity ~10-60 (the model "agrees" with itself)
- **Human text**: perplexity ~60-300+ (surprising, creative, or unconventional)

## Installation

```bash
uv tool install 'k-uncanny[ml,xpu]' --index https://download.pytorch.org/whl/xpu
```

This installs:
- `torch` (~800MB)
- `transformers` (~500MB)
- GPT-2 small model (~500MB, downloaded on first use)

## Usage

```bash
# Deep mode enables perplexity
uncanny scan report.md --deep

# Or explicitly
uncanny scan report.md --analyzers compression,burstiness,perplexity
```

## Device Support

The analyzer automatically detects:
- **CUDA** (NVIDIA GPUs)
- **MPS** (Apple Silicon)
- **CPU** (fallback)

The XPU profile selects Intel-compatible wheels; the upstream device resolver
does not currently select XPU, so it may still execute on CPU. Wheel selection
and actual inference-device support are separate checks.

## Strengths

- Strong signal, especially on longer text
- Complements compression well (different detection approach)

## Limitations

- Requires ~2GB of downloads
- Slower (~200ms per sample vs 8ms for default)
- GPT-2 is older — may be less effective at detecting text from newer models
- Memory usage ~1GB at runtime

## Implementation

Source: [`src/uncanny/analyzers/perplexity.py`](https://github.com/dunkinfrunkin/uncanny/blob/main/src/uncanny/analyzers/perplexity.py)

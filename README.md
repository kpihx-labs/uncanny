# Uncanny

## KpihX-Labs distribution

This MIT-licensed adaptation retains Frank Chan's upstream implementation and history.
Upstream: https://github.com/dunkinfrunkin/uncanny.
The PyPI distribution is `k-uncanny`; the executable and Python import remain `uncanny`.
Install with `uv tool install k-uncanny`, or use `make uv-link` from this checkout.
Run `uncanny scan document.txt --format json` for structured output on stdout.
Use `make check`, `make uv-build`, `make uv-publish`, and `make push`.
`make puhsb` is an alias for `make push`, which pushes the current branch to both
`github` and `gitlab`, never to `upstream`.
This detector produces heuristic scores, not calibrated authorship probabilities.
No score proves who wrote a document or whether plagiarism occurred.

The remaining documentation retains the upstream detector description, with
installation examples updated for this KpihX-Labs distribution.

**Detect AI-generated text from your terminal.** Sentence-level scoring, multiple detection strategies, zero API calls. Runs locally, works offline.

```
$ uncanny scan proposal.md

  Uncanny Analysis — proposal.md
  ─────────────────────────────────────────────────

  Overall Score: 0.73 (likely AI-generated)

  ██████████████████████░░░░░░░░  73% AI probability

  Sentence Breakdown:
   0.91 │ The implementation of this feature requires careful
        │ consideration of several architectural patterns.
   0.42 │ I tried like three different approaches before
        │ landing on this one, honestly.
   0.88 │ By leveraging the existing infrastructure, we can
        │ ensure seamless integration with minimal overhead.

  Legend: ■ 0.8+ AI  ■ 0.5-0.8 mixed  ■ <0.5 human
```

## Why Uncanny?

Every other AI detector is a SaaS that sends your text to someone else's server. Uncanny runs **entirely on your machine**. No API keys, no subscriptions, no data leaving your network.

| Tool | Open Source | Offline | Sentence-level | Multi-method | CLI |
|------|:----------:|:-------:|:--------------:|:------------:|:---:|
| GPTZero | | | x | x | |
| Originality.ai | | | x | x | |
| Copyleaks | | | x | x | |
| Sapling | | | x | | |
| Zippy | x | x | | | x |
| **Uncanny** | **x** | **x** | **x** | **x** | **x** |

## Benchmarks

Tested against 36 labeled samples (18 AI-generated, 18 human-written) across diverse genres: academic papers, Slack messages, code reviews, personal essays, Reddit posts, cover letters, tweets, and more.

| Metric | Uncanny | Zippy | Random Baseline |
|--------|:-------:|:-----:|:---------------:|
| **Overall Accuracy** | **91.7%** | 80.6% | 50.0% |
| AI Detected (true positive) | 88.9% | 100% | 100% |
| Human Cleared (true negative) | **94.4%** | 61.1% | 0% |
| **False Accusation Rate** | **5.6%** | 38.9% | 100% |
| Speed (per sample) | 8ms | 1ms | 0ms |

**Uncanny beats Zippy by 11 points on accuracy.** Zippy catches everything but wrongly flags 39% of human text as AI — that means 2 out of 5 human writers get falsely accused. Uncanny's false positive rate is 7x lower.

> Run the benchmarks yourself: `uncanny bench --compare`

### How we test

The corpus includes adversarial cases:

- **Casual AI** — LLM output prompted to sound informal ("Hey! So basically...")
- **Formal humans** — Academic writing, technical docs, polished prose
- **Short text** — 2-3 sentence samples where signal is weakest
- **Edge cases** — LinkedIn posts, PR descriptions, commit messages, debug notes

Accuracy is enforced in CI. Every PR must pass `test_bench.py` which gates on:
- Overall accuracy >= 70%
- False positive rate < 20%
- Score separation > 0.10

## Install

```bash
uv tool install k-uncanny
```

For an editable source installation:

```bash
git clone git@github.com:kpihx-labs/uncanny.git
cd uncanny
make uv-link
```

For ML-based analyzers (perplexity):

```bash
uv tool install 'k-uncanny[ml,xpu]' --index https://download.pytorch.org/whl/xpu
```

## Usage

```bash
# Scan a file
uncanny scan report.md

# Scan from stdin
cat essay.txt | uncanny scan

# Scan a string directly
uncanny scan --text "The implementation of this feature..."

# Output formats
uncanny scan report.md --format json      # structured JSON
uncanny scan report.md --format summary   # just the score

# Speed vs depth
uncanny scan report.md --fast             # compression only (~instant)
uncanny scan report.md --deep             # all analyzers (requires uncanny[ml])
uncanny scan report.md --analyzers compression,burstiness

# CI integration — exit code 1 if score exceeds threshold
uncanny scan report.md --threshold 0.7

# Benchmarks
uncanny bench                             # run accuracy benchmarks
uncanny bench --compare                   # head-to-head vs competitors
uncanny bench --compare --json            # machine-readable output
```

### JSON Output

```json
{
  "source": "proposal.md",
  "score": 0.73,
  "label": "likely_ai",
  "analyzers": {
    "compression": { "score": 0.81, "method": "lzma+zlib" },
    "burstiness": { "score": 0.71, "variance": 0.003 }
  },
  "sentences": [
    {
      "text": "The implementation of this feature requires...",
      "score": 0.91,
      "offset": { "start": 0, "end": 89 }
    }
  ]
}
```

## How It Works

Uncanny combines multiple detection strategies through an **ensemble scorer** with dynamic weighting:

### Compression Analysis (primary signal)
AI text is statistically predictable — it compresses better than human text. Uncanny cross-compresses your text against both an AI-generated prelude and a human-written prelude using LZMA and zlib. If your text shares compression patterns with the AI prelude, it scores higher. This is the fastest method (no model needed) and the most reliable single signal.

### Burstiness Analysis (tiebreaker)
Humans write with natural variation — short sentences mixed with long ones, simple ideas next to complex ones. AI text is uniformly smooth. Uncanny measures the variance in compression ratio and sentence length across a document. Low variance = AI-like uniformity. This signal gets dynamically weighted — it matters most when compression is ambiguous.

### Perplexity Analysis (optional, requires `uncanny[ml]`)
Measures how "surprised" GPT-2 is by each sentence. AI-generated text has low perplexity (the model predicted it easily). Human text has high perplexity (surprising word choices). Requires downloading a ~500MB model.

### Ensemble Scoring
Analyzers are combined with **confidence-aware dynamic weighting**. When compression is decisive (far from 0.5), it dominates. When compression is ambiguous, burstiness gets more influence. This avoids the classic problem of a weak signal overriding a strong one.

## Design Principles

1. **Offline-first** — No API calls. Everything runs locally. Models downloaded once.
2. **Fast by default** — Default mode uses compression + burstiness (~8ms/sample). No model download needed.
3. **Scores, not verdicts** — Uncanny reports probabilities, never binary "AI or human" labels. The tool informs, it doesn't judge.
4. **Sentence-level granularity** — Not just "this doc is AI" — shows exactly which sentences triggered detection.
5. **CI-friendly** — `--threshold` flag with exit codes. JSON output for parsing. Benchmarks in CI.

## Limitations

AI detection is an imperfect science. Be honest about it:

- **No detector is 100% accurate.** False positives and false negatives happen.
- **Short text is unreliable.** Confidence drops below ~250 words.
- **Edited AI text is harder to detect.** A human editing AI output blurs the signal.
- **Newer models are harder to detect.** As LLMs improve, statistical signals narrow.
- **Technical writing may false-positive.** Formal, structured text can look AI-like.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). PRs welcome — especially new analyzers, corpus samples, and accuracy improvements.

## License

MIT

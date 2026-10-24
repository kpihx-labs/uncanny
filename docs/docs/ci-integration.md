---
sidebar_position: 8
title: CI Integration
---

# CI Integration

Uncanny is designed to work in automated pipelines. Use `--threshold` and `--format json` to gate on AI-generated content.

## GitHub Actions

```yaml
name: AI Content Check

on: [pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: astral-sh/setup-uv@v10.3.2

      - name: Install uncanny
        run: uv tool install k-uncanny

      - name: Scan PR description
        run: |
          gh pr view ${{ github.event.number }} --json body -q .body > /tmp/pr-body.txt
          uncanny scan /tmp/pr-body.txt --threshold 0.8 --format summary
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Scan changed docs
        run: |
          git diff --name-only HEAD~1 -- '*.md' | while read f; do
            echo "Scanning $f..."
            uncanny scan "$f" --threshold 0.7 --format summary
          done
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Score is at or below the threshold |
| `1` | Score exceeds the threshold |

```bash
uncanny scan essay.md --threshold 0.7
echo $?  # 0 or 1
```

## JSON Output for Parsing

```bash
uncanny scan report.md --format json | jq '.score'
# 0.73

uncanny scan report.md --format json | jq '.sentences[] | select(.score > 0.8) | .text'
# "The implementation of this feature requires..."
```

## Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: uncanny
        name: AI content check
        entry: uncanny scan --threshold 0.8 --format summary
        language: system
        files: '\.md$'
```

## Choosing a Threshold

| Threshold | Use Case |
|-----------|----------|
| `0.5` | Strict — flag anything suspicious |
| `0.7` | Balanced — catch likely AI content |
| `0.8` | Permissive — only flag high-confidence AI |
| `0.9` | Very permissive — only obvious AI text |

:::tip
Start with `0.7` and adjust based on your false positive tolerance. Run `uncanny bench` on your own content to calibrate.
:::

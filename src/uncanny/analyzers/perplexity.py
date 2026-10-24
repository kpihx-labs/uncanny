"""
Perplexity-based AI detection.

Measures how "surprised" a language model is by the text.
AI-generated text has low perplexity (predictable), human text has high perplexity.

Requires ML dependencies: make install-ml BACKEND=xpu (or BACKEND=cpu).
"""

from __future__ import annotations

import math

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from uncanny.analyzers.base import Analyzer
from uncanny.tokenizer import split_sentences
from uncanny.types import AnalyzerResult, SentenceScore

_DEFAULT_MODEL = "gpt2"


def _compute_perplexity(text: str, model, tokenizer, device: str) -> float:
    """Compute perplexity of text using the given model."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=1024)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs, labels=inputs["input_ids"])

    return math.exp(outputs.loss.item())


def _perplexity_to_score(perplexity: float) -> float:
    """Convert perplexity to AI probability score.

    Based on research:
    - AI text: perplexity typically 10-60
    - Human text: perplexity typically 60-300+

    Uses log scale for smoother mapping.
    """
    # log-scale mapping: log(15) ~ 2.7 -> 1.0, log(200) ~ 5.3 -> 0.0
    log_ppl = math.log(max(perplexity, 1.0))
    low, high = 2.7, 5.3
    score = 1.0 - (log_ppl - low) / (high - low)
    return max(0.0, min(1.0, score))


class PerplexityAnalyzer(Analyzer):
    """Detects AI text using language model perplexity."""

    name = "perplexity"

    def __init__(self, model_name: str = _DEFAULT_MODEL):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Use MPS (Apple Silicon) if available
        if not torch.cuda.is_available() and hasattr(torch.backends, "mps"):
            if torch.backends.mps.is_available():
                self.device = "mps"

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name).to(self.device)
        self.model.eval()

    def analyze(self, text: str) -> AnalyzerResult:
        sentences = split_sentences(text)

        sentence_scores: list[SentenceScore] = []
        perplexities: list[float] = []

        for sent_text, start, end in sentences:
            if len(sent_text.split()) < 5:
                sentence_scores.append(SentenceScore(sent_text, 0.5, start, end))
                continue

            ppl = _compute_perplexity(sent_text, self.model, self.tokenizer, self.device)
            perplexities.append(ppl)
            score = _perplexity_to_score(ppl)
            sentence_scores.append(SentenceScore(sent_text, score, start, end))

        # Overall perplexity on full text
        if text.strip() and len(text.split()) >= 5:
            overall_ppl = _compute_perplexity(
                text, self.model, self.tokenizer, self.device
            )
            overall = _perplexity_to_score(overall_ppl)
        else:
            overall = 0.5

        return AnalyzerResult(
            name=self.name,
            score=overall,
            sentence_scores=sentence_scores,
            metadata={"model": self.model_name},
        )

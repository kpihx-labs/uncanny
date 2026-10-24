"""Uncanny CLI — AI text detection with sentence-level scoring."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from uncanny import __version__
from uncanny.analyzers.base import Analyzer
from uncanny.analyzers.compression import CompressionAnalyzer
from uncanny.analyzers.burstiness import BurstinessAnalyzer
from uncanny import ensemble
from uncanny.output import terminal as term_output
from uncanny.output import json_output

def _version_callback(value: bool):
    if value:
        print(f"uncanny {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="uncanny",
    help="Detect AI-generated text with sentence-level scoring.",
    no_args_is_help=True,
    add_completion=False,
    callback=lambda version: None,
)


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-V", callback=_version_callback, is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """Detect AI-generated text with sentence-level scoring."""
console = Console()


def _get_analyzers(
    fast: bool = False, deep: bool = False, analyzer_names: str | None = None
) -> list[Analyzer]:
    """Build the list of analyzers based on flags."""
    if fast:
        return [CompressionAnalyzer()]

    if analyzer_names:
        names = [n.strip() for n in analyzer_names.split(",")]
    elif deep:
        names = ["compression", "perplexity", "burstiness"]
    else:
        # Default: compression + burstiness (no model download needed)
        names = ["compression", "burstiness"]

    analyzers: list[Analyzer] = []
    for name in names:
        if name == "compression":
            analyzers.append(CompressionAnalyzer())
        elif name == "burstiness":
            analyzers.append(BurstinessAnalyzer())
        elif name == "perplexity":
            try:
                from uncanny.analyzers.perplexity import PerplexityAnalyzer

                analyzers.append(PerplexityAnalyzer())
            except ImportError:
                console.print(
                    "[yellow]Perplexity analyzer requires ML dependencies.[/]\n"
                    "From a checkout: [bold]make uv-link-ml BACKEND=xpu[/] "
                    "(or BACKEND=cpu).",
                    style="yellow",
                )
                raise typer.Exit(1)
        else:
            console.print(f"[red]Unknown analyzer: {name}[/]")
            raise typer.Exit(1)

    return analyzers


def _read_input(
    file: Optional[Path] = None, text: Optional[str] = None
) -> tuple[str, str | None]:
    """Read input text from file, string, or stdin. Returns (text, source_name)."""
    if text:
        return text, None

    if file:
        if file.is_dir():
            console.print("[red]Directory scanning not yet supported. Pass a file.[/]")
            raise typer.Exit(1)
        if not file.exists():
            console.print(f"[red]File not found: {file}[/]")
            raise typer.Exit(1)
        try:
            return file.read_text(encoding="utf-8"), str(file)
        except UnicodeDecodeError:
            console.print(f"[red]Cannot read {file}: not a text file or encoding issue.[/]")
            raise typer.Exit(1)

    # Try stdin
    if not sys.stdin.isatty():
        return sys.stdin.read(), None

    console.print("[red]No input provided. Pass a file, --text, or pipe stdin.[/]")
    raise typer.Exit(1)


@app.command()
def scan(
    file: Optional[Path] = typer.Argument(None, help="File to scan"),
    text: Optional[str] = typer.Option(None, "--text", "-t", help="Text string to scan"),
    format: str = typer.Option(
        "terminal", "--format", "-f", help="Output format: terminal, json, summary"
    ),
    fast: bool = typer.Option(False, "--fast", help="Compression only (instant, no model)"),
    deep: bool = typer.Option(
        False, "--deep", help="All analyzers including perplexity (requires ML deps)"
    ),
    analyzers: Optional[str] = typer.Option(
        None, "--analyzers", "-a", help="Comma-separated analyzer names"
    ),
    threshold: Optional[float] = typer.Option(
        None, "--threshold", help="Exit code 1 if score exceeds threshold (for CI)"
    ),
) -> None:
    """Scan text for AI-generated content."""
    content, source = _read_input(file, text)

    if not content.strip():
        console.print("[yellow]Empty input, nothing to analyze.[/]")
        raise typer.Exit(0)

    analyzer_list = _get_analyzers(fast=fast, deep=deep, analyzer_names=analyzers)

    results = []
    for analyzer in analyzer_list:
        results.append(analyzer.analyze(content))

    result = ensemble.combine(results, source=source)

    if format == "json":
        print(json_output.render(result))
    elif format == "summary":
        console.print(f"{result.score:.2f} ({result.label})")
    else:
        term_output.render(result)

    if threshold is not None and result.score > threshold:
        raise typer.Exit(1)


@app.command()
def bench(
    corpus: Optional[Path] = typer.Option(
        None, "--corpus", "-c", help="Path to corpus directory (default: built-in)"
    ),
    analyzers: Optional[str] = typer.Option(
        None, "--analyzers", "-a", help="Comma-separated analyzer names"
    ),
    threshold: float = typer.Option(
        0.5, "--threshold", help="Score threshold for classification"
    ),
    output_json: bool = typer.Option(
        False, "--json", help="Output results as JSON"
    ),
    compare: bool = typer.Option(
        False, "--compare", help="Include competitor comparison (Zippy, baseline)"
    ),
) -> None:
    """Run accuracy and performance benchmarks against a labeled corpus."""
    from uncanny.bench import runner, display

    analyzer_names = [n.strip() for n in analyzers.split(",")] if analyzers else None

    # Default corpus location: benchmarks/corpus relative to repo root
    if corpus is None:
        repo_root = Path(__file__).resolve().parent.parent.parent
        corpus = repo_root / "benchmarks" / "corpus"

    if not corpus.exists():
        console.print(f"[red]Corpus directory not found: {corpus}[/]")
        console.print("Run from the repo root or pass --corpus.")
        raise typer.Exit(1)

    report = runner.run(
        corpus_dir=corpus,
        analyzer_names=analyzer_names,
        threshold=threshold,
    )

    competitors = []
    if compare:
        competitors = runner.run_competitors(corpus_dir=corpus, threshold=threshold)

    if output_json:
        import json as json_mod
        data = report.to_dict()
        if competitors:
            data["competitors"] = [
                {
                    "name": c.name,
                    "accuracy": round(c.accuracy, 4),
                    "true_positive_rate": round(c.true_positive_rate, 4),
                    "true_negative_rate": round(c.true_negative_rate, 4),
                    "false_positive_rate": round(c.false_positive_rate, 4),
                    "separation": round(c.separation, 4),
                    "avg_ms_per_sample": round(c.avg_ms_per_sample, 1),
                }
                for c in competitors
            ]
        print(json_mod.dumps(data, indent=2))
    else:
        display.render(report)
        if competitors:
            display.render_comparison(report, competitors)


@app.command()
def serve(
    port: int = typer.Option(7272, "--port", "-p", help="Port to serve on"),
    no_open: bool = typer.Option(False, "--no-open", help="Don't auto-open browser"),
) -> None:
    """Launch the web visualizer for interactive analysis."""
    from uncanny.web.server import run_server

    server, url = run_server(port=port, open_browser=not no_open)
    console.print(f"  Uncanny Visualizer running at [bold cyan]{url}[/]")
    console.print("  Press Ctrl+C to stop.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        console.print("\n  Stopped.")
        server.shutdown()


@app.command()
def version() -> None:
    """Show version."""
    console.print(f"uncanny {__version__}")


if __name__ == "__main__":
    app()

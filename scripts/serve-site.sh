#!/usr/bin/env bash
# Serves the full site locally: landing page + docs
# Landing page at http://localhost:8000
# Docs at http://localhost:8000/docs/
set -euo pipefail

PORT="${1:-8000}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
SERVE_DIR=$(mktemp -d)

# Copy landing page
cp "$ROOT/site/index.html" "$SERVE_DIR/index.html"

# Copy built docs
if [ -d "$ROOT/docs/build" ]; then
  cp -r "$ROOT/docs/build" "$SERVE_DIR/docs"
else
  echo "Docs not built yet. Run: cd docs && npm run build"
  exit 1
fi

echo "Serving at http://localhost:$PORT"
echo "  Landing page: http://localhost:$PORT"
echo "  Docs:         http://localhost:$PORT/docs/"
echo "  Press Ctrl+C to stop."
echo ""

cd "$SERVE_DIR"
uv run --no-project python -m http.server "$PORT"

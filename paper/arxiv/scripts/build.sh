#!/usr/bin/env bash
# Reproducible build for the arxiv submission package.
# Inputs:
#   docs/research/paper/v3/full-paper.md  (canonical paper source)
#   arxiv/figures/*.mmd                   (Mermaid figure sources)
#   arxiv/scripts/{preprocess.py,header.tex}
# Outputs:
#   arxiv/main.tex                        (canonical LaTeX, committed to git)
#   arxiv/figures/*.pdf                   (committed)
#   arxiv/build/main.pdf                  (review PDF; build/ is gitignored)
# Re-run from anywhere — uses absolute paths.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ARXIV="$ROOT/arxiv"
SCRIPTS="$ARXIV/scripts"
BUILD="$ARXIV/build"
mkdir -p "$BUILD"
PANDOC="${PANDOC_BIN:-/c/Users/orang/AppData/Local/Microsoft/WinGet/Packages/JohnMacFarlane.Pandoc_Microsoft.Winget.Source_8wekyb3d8bbwe/pandoc-3.9.0.2/pandoc.exe}"

# 1. Preprocess markdown (mermaid -> image refs, structural cleanup).
python "$SCRIPTS/preprocess.py"

# 2. Render Mermaid figures to PDF (skipped if PDFs already exist & up-to-date).
for fig in fig1-architecture fig2-concept-graph fig4-galaxy-routes fig5-kst-mapping; do
  src="$ARXIV/figures/$fig.mmd"
  dst="$ARXIV/figures/$fig.pdf"
  if [[ ! -f "$dst" || "$src" -nt "$dst" ]]; then
    mmdc -i "$src" -o "$dst" -b transparent
  fi
done

# 3. Run pandoc with custom header.
"$PANDOC" \
  --from=gfm \
  --to=latex \
  --standalone \
  --top-level-division=section \
  --wrap=preserve \
  --include-in-header="$SCRIPTS/header.tex" \
  --metadata title="System-Level Validation of a Four-Layer Control Architecture for LLM Mathematics Tutoring" \
  --metadata author="Wataru Kawashima" \
  --metadata date="2026-04-25" \
  "$BUILD/full-paper-preproc.md" \
  -o "$ARXIV/main.tex"

# 4. Patch Unicode characters and longtable column specs in main.tex.
python "$SCRIPTS/preprocess.py" --patch-tex "$ARXIV/main.tex"

# 5. Compile twice with xelatex (longtable needs two passes for stable widths).
cd "$ARXIV"
xelatex -interaction=nonstopmode -enable-installer -output-directory=build main.tex >/dev/null
xelatex -interaction=nonstopmode -enable-installer -output-directory=build main.tex >/dev/null

echo
echo "PDF:           $BUILD/main.pdf"
echo "Pages:         $(grep -oE "[0-9]+ pages" "$BUILD/main.log" | tail -1)"
echo "Overfull boxes: $(grep -c "Overfull" "$BUILD/main.log")"
echo "Missing chars:  $(grep -c "Missing character" "$BUILD/main.log")"

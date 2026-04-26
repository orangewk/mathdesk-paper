"""Preprocess full-paper.md for pandoc:
- Replace each ```mermaid ... ``` fenced block with an image reference
- Strip the dot before the trailing 'Figure N.' caption that follows so pandoc
  picks up the caption naturally via the image alt text.
- Drop the duplicated per-section "References (Section X)" sub-lists (they
  duplicate the unified reference list at the end).
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "docs" / "research" / "paper" / "v3" / "full-paper.md"
BUILD = ROOT / "arxiv" / "build"
BUILD.mkdir(exist_ok=True)
DST = BUILD / "full-paper-preproc.md"

# Order in which mermaid blocks appear -> figure file basenames
FIG_BASENAMES = [
    ("fig1-architecture", "Four-layer control architecture"),
    ("fig2-concept-graph", "Concept graph for the correlation coefficient domain"),
    ("fig4-galaxy-routes", "v0 vs. v1 teaching routes (correlation coefficient)"),
    ("fig5-kst-mapping", "Four-layer architecture mapped to KST-interpretable roles"),
]

text = SRC.read_text(encoding="utf-8")

# ----- structural cleanup -----
# 1. Drop the top-level paper title (handled by main.tex \title{})
text = re.sub(
    r"\A# System-Level Validation of a Four-Layer Control Architecture for LLM Mathematics Tutoring\n+(?:---\n+)?",
    "",
    text,
)
# 2. (Previously: extracted Abstract to build/abstract.tex and stripped it from body;
#    but main.tex never \input'd the result, so the Abstract was missing from the PDF.
#    Now: leave the `# Abstract` section in the body. pandoc will render it as a
#    \section{Abstract} just before Section 1, and the Figure 1 image embedded inside
#    it will appear on page 1. Cleaner than building a custom \abstract macro.)

# 3. Demote `# Section N: Title` to top-level section, drop duplicated `## N. Title`
text = re.sub(r"^# Section \d+: ", r"# ", text, flags=re.MULTILINE)
text = re.sub(r"^## \d+\. .*?\n", "", text, flags=re.MULTILINE)
# 4. Demote appendix headings: `# Appendix A. Glossary of Terms` -> `# Appendix A. ...`
#    (already top-level; nothing to do)


# Replace mermaid fenced blocks
def replace_mermaid(text):
    pattern = re.compile(r"```mermaid\n.*?\n```\n?", re.DOTALL)
    matches = list(pattern.finditer(text))
    assert len(matches) == len(FIG_BASENAMES), (
        f"Expected {len(FIG_BASENAMES)} mermaid blocks, found {len(matches)}"
    )
    pieces = []
    cursor = 0
    for m, (name, alt) in zip(matches, FIG_BASENAMES):
        pieces.append(text[cursor:m.start()])
        pieces.append(f"![{alt}](figures/{name}.pdf)\n\n")
        cursor = m.end()
    pieces.append(text[cursor:])
    return "".join(pieces)

text = replace_mermaid(text)

# Drop per-section "References (Section X)" subsections — they are duplicated
# in the unified reference list at the end of the paper. Keep the unified one.
# These subsections look like:
#   ## References (Section 3)
#   - bullet
#   - bullet
#   ---
text = re.sub(
    r"\n## References \(Section \d+\)\n(?:- .*\n)+(?:\n)?(?:---\n)?",
    "\n",
    text,
)

# Drop the rendered ASCII flowchart in Appendix E.3 — pandoc would emit it
# verbatim and it does not survive LaTeX line-wrapping. Replace with a note.
flow_old = """```\nIdentify the first substantive move\n         ↓\nQ1: Does this move request a concrete operation from the learner?\n    (calculation, diagram, substitution, listing, observation)\n    Yes → EXPERIENCE\n    No  ↓\nQ2: Does this move ask for the learner's existing knowledge,\n    memory, prediction, or intuition?\n    Yes → CONFIRMATION\n    No  ↓\nQ3: Does this move present a concept, procedure, or structure\n    with the tutor as subject?\n    Yes → EXPLANATION\n    No  → UNCLASSIFIABLE — re-identify substantive move\n```"""
# Keep as fenced verbatim — pandoc handles ``` -> verbatim already.

DST.write_text(text, encoding="utf-8")
print(f"Wrote {DST} ({len(text)} chars)")


# ----- post-pandoc: patch body.tex with Unicode->LaTeX substitutions -----
# Run this after `pandoc -o build/main.tex`. Markdown stays untouched; we patch
# the generated tex so pdflatex / xelatex render every glyph without missing-font
# warnings. These are pure typesetting substitutions, no semantic change.
def patch_tex(path: Path):
    if not path.exists():
        return
    raw = path.read_text(encoding="utf-8")
    # Within math mode brackets pandoc already wraps things; only replace the
    # bare characters elsewhere. Safe substitutions (visually identical):
    subs = [
        ("≥", r"$\geq$"),       # ≥
        ("≤", r"$\leq$"),       # ≤
        ("≠", r"$\neq$"),       # ≠
        ("κ", r"$\kappa$"),     # κ
        ("β", r"$\beta$"),      # β
        ("✓", r"\\checkmark"),  # ✓
    ]
    for src_, dst_ in subs:
        raw = raw.replace(src_, dst_)

    # Convert longtable column specs to wrapping columns so wide cells reflow.
    # pandoc default: \begin{longtable}[]{@{}lll@{}}. Replace each literal
    # l/c/r column with a `>{\raggedright\arraybackslash}p{<frac>\linewidth}`
    # column where the fraction is computed from the column count.
    def replace_longtable(match):
        prefix = match.group(1)
        spec = match.group(2)
        # Column letters in the spec (only l/c/r — leave existing p{} alone)
        cols = re.findall(r"[lcr]", spec)
        n = len(cols)
        if n == 0:
            return match.group(0)
        # Available width: \linewidth minus per-column \tabcolsep padding.
        # \tabcolsep is 4pt (from header.tex), so 2*4pt per column ≈ 0.5em.
        # Empirical 0.93 fraction leaves room for borders + final padding.
        width_per = 0.93 / n
        col_def = (
            r">{\raggedright\arraybackslash}p{" + f"{width_per:.3f}" + r"\linewidth}"
        )
        new_spec = "@{}" + (col_def * n) + "@{}"
        return f"{prefix}{{{new_spec}}}"

    raw = re.sub(
        r"(\\begin\{longtable\}\[\])\{@\{\}([lcr]+)@\{\}\}",
        replace_longtable,
        raw,
    )

    path.write_text(raw, encoding="utf-8")
    print(f"Patched {path}")


import sys
if len(sys.argv) > 1 and sys.argv[1] == "--patch-tex":
    patch_tex(Path(sys.argv[2]))


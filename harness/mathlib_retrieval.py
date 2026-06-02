#!/usr/bin/env python3
"""Mathlib-aware lemma retrieval for the proof-repair loop.

Closes greyhaven-ai/pi-autocontext-lean-verify#1. Given the theorem template and
the Lean verifier feedback, this surfaces a ranked list of candidate library
lemmas (fully-qualified name + signature + one-line doc) so the repair model is
shown real declarations instead of guessing names that may have been renamed or
never existed.

Grounding and honesty:
- Candidates come only from a declaration index that is expected to be generated
  from the *pinned* Mathlib revision used by the harness (a JSON list of
  ``{"name", "signature", "doc"}`` records). Because the index is a dump of the
  pinned revision, every suggested name resolves in that revision. Generating the
  dump (and, as a stronger follow-up, validating each candidate live via
  ``#check`` against the lake environment) is left to the index producer.
- Retrieval is advisory only. Lean remains the correctness oracle; nothing here
  asserts that a candidate is applicable or that a proof is correct.
- This is a pure, dependency-free module (stdlib only) so it is unit-testable in
  CI without Lean or Mathlib present. When no index is configured it returns no
  candidates, leaving the default Init-only behaviour untouched.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

# Env var pointing at the declaration index JSON (a dump of the pinned Mathlib
# revision). When unset/missing, retrieval is a no-op.
INDEX_ENV_VAR = "AUTOCONTEXT_MATHLIB_INDEX"

_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_']*")
# Lean verifier phrasings that name a specific missing/used identifier.
_IDENTIFIER_HINT_RE = re.compile(
    r"unknown (?:identifier|constant)\s*'?([A-Za-z_][A-Za-z0-9_.']*)'?",
)


@dataclass(slots=True, frozen=True)
class Declaration:
    """A single library declaration available to the proof author."""

    name: str
    signature: str = ""
    doc: str = ""


def load_index(path: str | os.PathLike[str] | None = None) -> list[Declaration]:
    """Load the declaration index.

    Resolution order: explicit ``path`` argument, then ``$AUTOCONTEXT_MATHLIB_INDEX``.
    Returns an empty list when no index is configured or the file is missing, so
    the caller can treat "no retrieval" as the safe default.
    """
    raw_path = str(path) if path is not None else os.environ.get(INDEX_ENV_VAR, "")
    if not raw_path:
        return []
    index_path = Path(raw_path)
    if not index_path.is_file():
        return []
    data = json.loads(index_path.read_text(encoding="utf-8"))
    records = data["declarations"] if isinstance(data, dict) else data
    declarations: list[Declaration] = []
    for record in records:
        name = str(record.get("name", "")).strip()
        if not name:
            continue
        declarations.append(
            Declaration(
                name=name,
                signature=str(record.get("signature", "")).strip(),
                doc=str(record.get("doc", "")).strip(),
            )
        )
    return declarations


def _tokenize(text: str) -> list[str]:
    """Split identifiers, also breaking dotted/CamelCase names into parts."""
    tokens: list[str] = []
    for raw in _TOKEN_RE.findall(text or ""):
        tokens.append(raw.lower())
        # split Mathlib-style CamelCase so `EuclideanSpace` matches `euclidean`.
        for part in re.findall(r"[A-Z]?[a-z0-9']+|[A-Z]+(?![a-z])", raw):
            if part:
                tokens.append(part.lower())
    return tokens


def derive_query(template: str, feedback: str) -> str:
    """Build a retrieval query from the template and the verifier feedback.

    Identifiers named directly by the verifier ("unknown identifier 'X'") are
    repeated so they dominate the ranking; the rest of the template and feedback
    provide topical context.
    """
    named = _IDENTIFIER_HINT_RE.findall(feedback or "")
    boosted = " ".join(name for name in named for _ in range(4))
    return " ".join(part for part in (boosted, feedback or "", template or "") if part)


def score_declaration(query_terms: list[str], decl: Declaration) -> float:
    """Weighted keyword overlap: name matches count most, then signature, doc."""
    if not query_terms:
        return 0.0
    query = set(query_terms)
    name_terms = set(_tokenize(decl.name))
    sig_terms = set(_tokenize(decl.signature))
    doc_terms = set(_tokenize(decl.doc))
    score = 0.0
    score += 3.0 * len(query & name_terms)
    score += 2.0 * len(query & sig_terms)
    score += 1.0 * len(query & doc_terms)
    return score


def retrieve(
    query: str, index: list[Declaration], *, limit: int = 8
) -> list[Declaration]:
    """Return up to ``limit`` declarations ranked by relevance to ``query``."""
    if not index:
        return []
    query_terms = _tokenize(query)
    scored = [
        (score_declaration(query_terms, decl), idx, decl)
        for idx, decl in enumerate(index)
    ]
    scored = [item for item in scored if item[0] > 0.0]
    # Sort by score desc, then original order for determinism (no Math.random concerns).
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [decl for _, _, decl in scored[: max(0, limit)]]


def format_lemma_block(declarations: list[Declaration]) -> str:
    """Render retrieved candidates as a Markdown block, or "" if there are none."""
    if not declarations:
        return ""
    lines = [
        "Relevant existing library lemmas (advisory candidates; not guaranteed "
        "applicable, verify with Lean):",
    ]
    for decl in declarations:
        head = f"- `{decl.name}`"
        if decl.signature:
            head += f" : {decl.signature}"
        lines.append(head)
        if decl.doc:
            lines.append(f"    {decl.doc}")
    return "\n".join(lines)


def lemma_block_for(
    *,
    template: str,
    feedback: str,
    index: list[Declaration],
    limit: int = 8,
) -> str:
    """Convenience: derive a query, retrieve, and render the block in one call."""
    query = derive_query(template, feedback)
    return format_lemma_block(retrieve(query, index, limit=limit))

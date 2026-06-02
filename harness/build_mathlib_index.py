#!/usr/bin/env python3
"""Build the Mathlib declaration index consumed by harness/mathlib_retrieval.py.

Closes greyhaven-ai/pi-autocontext-lean-verify#4. The retrieval feature (#1, #2)
needs an index of `{name, signature, doc}` records dumped from the *pinned*
Mathlib revision; this tool produces that index.

Approach (source-parse tier): walk a Mathlib source checkout, track the
`namespace`/`section`/`end` stack to produce fully-qualified names, and capture
each `theorem|lemma|def|abbrev|instance` name, its signature (up to `:=`/`where`),
and the immediately-preceding `/-- ... -/` docstring. Names come from the source
at the pinned revision, so they resolve there (modulo `private`, which is
skipped). A Lean-environment-backed dump (fully elaborated signatures via
`ppExpr`, guaranteed resolution, live `#check`) is the stronger follow-up but
requires a full Mathlib build and is out of scope here.

Pure, stdlib-only and unit-testable: the parser and the index shaping run with no
Lean/Mathlib present. `--from-dump` lets the pipeline be exercised from a JSONL
file of `{name, signature, doc}` records without a checkout.

Usage:
    python3 harness/build_mathlib_index.py --mathlib-src /path/to/mathlib --out index.json
    python3 harness/build_mathlib_index.py --from-dump dump.jsonl --out index.json
    export AUTOCONTEXT_MATHLIB_INDEX=$PWD/index.json   # then run the repair loop
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

# Declaration keywords we index. Constructors/recursors/examples are skipped.
_DECL_RE = re.compile(
    r"^\s*(?P<mods>(?:@\[[^\]]*\]\s*|private\s+|protected\s+|noncomputable\s+|scoped\s+|local\s+|partial\s+|unsafe\s+)*)"
    r"(?P<kind>theorem|lemma|def|abbrev|instance)\s+"
    r"(?P<name>[^\s:({\[\]}]+)"
)
_NAMESPACE_RE = re.compile(r"^\s*namespace\s+(\S+)")
_SECTION_RE = re.compile(r"^\s*section(?:\s+(\S+))?\s*$")
_END_RE = re.compile(r"^\s*end(?:\s+(\S+))?\s*$")
_STOP_SIG = re.compile(r":=|\bwhere\b")


@dataclass(slots=True, frozen=True)
class Declaration:
    name: str
    signature: str = ""
    doc: str = ""


class _Scope:
    """Tracks the namespace/section stack to build fully-qualified names."""

    __slots__ = ("stack",)

    def __init__(self) -> None:
        # entries: (kind, name) where kind in {"ns", "sec"}; name may be "" for
        # anonymous sections.
        self.stack: list[tuple[str, str]] = []

    def push_namespace(self, name: str) -> None:
        self.stack.append(("ns", name))

    def push_section(self, name: str) -> None:
        self.stack.append(("sec", name))

    def end(self, name: str | None) -> None:
        # `end X` closes the nearest scope named X; bare `end` closes the nearest
        # anonymous section. Be forgiving if the file is malformed.
        if name:
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][1] == name:
                    del self.stack[i:]
                    return
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == "sec":
                del self.stack[i:]
                return
        if self.stack:
            self.stack.pop()

    def prefix(self) -> str:
        return ".".join(name for kind, name in self.stack if kind == "ns")


def _clean_doc(block: str) -> str:
    text = block.strip()
    if text.startswith("/--"):
        text = text[3:]
    if text.endswith("-/"):
        text = text[:-2]
    # collapse whitespace; docstrings are advisory context, one line is enough.
    return re.sub(r"\s+", " ", text).strip()


def extract_declarations(
    text: str, *, max_signature_lines: int = 40
) -> list[Declaration]:
    """Parse one Lean source file into indexed declarations."""
    lines = text.splitlines()
    scope = _Scope()
    pending_doc: str | None = None
    in_doc = False
    doc_buf: list[str] = []
    out: list[Declaration] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Docstring accumulation (supports single-line and multi-line `/-- -/`).
        if in_doc:
            doc_buf.append(line)
            if "-/" in line:
                pending_doc = _clean_doc("\n".join(doc_buf))
                in_doc = False
                doc_buf = []
            i += 1
            continue
        if stripped.startswith("/--"):
            doc_buf = [line]
            if "-/" in stripped[3:]:
                pending_doc = _clean_doc(stripped)
            else:
                in_doc = True
            i += 1
            continue

        ns = _NAMESPACE_RE.match(line)
        if ns:
            scope.push_namespace(ns.group(1))
            pending_doc = None
            i += 1
            continue
        sec = _SECTION_RE.match(line)
        if sec:
            scope.push_section(sec.group(1) or "")
            pending_doc = None
            i += 1
            continue
        end = _END_RE.match(line)
        if end:
            scope.end(end.group(1))
            pending_doc = None
            i += 1
            continue

        decl = _DECL_RE.match(line)
        if decl:
            mods = decl.group("mods") or ""
            name = decl.group("name")
            if "private" in mods or not name or name == ":":
                pending_doc = None
                i += 1
                continue
            prefix = scope.prefix()
            full = f"{prefix}.{name}" if prefix else name
            # Signature: from after the name across continuation lines up to
            # `:=`/`where`/a new declaration/blank, collapsed to one line.
            sig_parts: list[str] = [line[decl.end("name") :]]
            j = i
            stop = bool(_STOP_SIG.search(sig_parts[0]))
            while not stop and (j + 1) < n and (j - i) < max_signature_lines:
                j += 1
                nxt = lines[j]
                if not nxt.strip():
                    break
                if (
                    _DECL_RE.match(nxt)
                    or _NAMESPACE_RE.match(nxt)
                    or _END_RE.match(nxt)
                ):
                    break
                sig_parts.append(nxt)
                if _STOP_SIG.search(nxt):
                    stop = True
            signature = re.sub(r"\s+", " ", " ".join(sig_parts)).strip()
            signature = re.split(r":=|\bwhere\b", signature)[0].strip()
            out.append(
                Declaration(name=full, signature=signature, doc=pending_doc or "")
            )
            pending_doc = None
            i = j + 1 if j > i else i + 1
            continue

        # Attribute lines (e.g. `@[simp]`) may sit between a docstring and the
        # declaration; keep the pending docstring across them.
        if stripped.startswith("@["):
            i += 1
            continue

        # Any other non-blank line breaks docstring association.
        if stripped:
            pending_doc = None
        i += 1
    return out


def iter_lean_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.lean")):
        # Skip build artifacts and the lake packages dir.
        parts = set(path.parts)
        if ".lake" in parts or "lakefile" in path.name:
            continue
        yield path


def build_index(
    src_root: Path,
    *,
    include_namespaces: list[str] | None = None,
    limit: int | None = None,
) -> list[Declaration]:
    """Walk a Mathlib source checkout and build a deduplicated declaration list."""
    seen: set[str] = set()
    decls: list[Declaration] = []
    for path in iter_lean_files(src_root):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for decl in extract_declarations(text):
            if decl.name in seen:
                continue
            if include_namespaces and not any(
                decl.name == ns or decl.name.startswith(f"{ns}.")
                for ns in include_namespaces
            ):
                continue
            seen.add(decl.name)
            decls.append(decl)
            if limit is not None and len(decls) >= limit:
                return decls
    return decls


def parse_dump(text: str) -> list[Declaration]:
    """Parse a JSONL dump (one `{name, signature, doc}` object per line)."""
    decls: list[Declaration] = []
    for raw in text.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        record = json.loads(raw)
        name = str(record.get("name", "")).strip()
        if not name:
            continue
        decls.append(
            Declaration(
                name=name,
                signature=str(record.get("signature", "")).strip(),
                doc=str(record.get("doc", "")).strip(),
            )
        )
    return decls


def write_index(declarations: list[Declaration], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(decl) for decl in declarations]
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mathlib-src", help="Path to a Mathlib source checkout (pinned revision)."
    )
    parser.add_argument(
        "--from-dump", help="Path to a JSONL dump to convert instead of parsing source."
    )
    parser.add_argument("--out", required=True, help="Output index JSON path.")
    parser.add_argument(
        "--limit", type=int, default=None, help="Cap the number of declarations."
    )
    parser.add_argument(
        "--include-namespace",
        action="append",
        default=None,
        dest="include_namespaces",
        help="Only index declarations under this namespace prefix (repeatable).",
    )
    args = parser.parse_args(argv)

    if bool(args.mathlib_src) == bool(args.from_dump):
        parser.error("provide exactly one of --mathlib-src or --from-dump")

    if args.from_dump:
        declarations = parse_dump(Path(args.from_dump).read_text(encoding="utf-8"))
        if args.include_namespaces:
            declarations = [
                d
                for d in declarations
                if any(
                    d.name == ns or d.name.startswith(f"{ns}.")
                    for ns in args.include_namespaces
                )
            ]
        if args.limit is not None:
            declarations = declarations[: args.limit]
    else:
        declarations = build_index(
            Path(args.mathlib_src),
            include_namespaces=args.include_namespaces,
            limit=args.limit,
        )

    out_path = Path(args.out)
    write_index(declarations, out_path)
    print(json.dumps({"out": str(out_path), "declarations": len(declarations)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

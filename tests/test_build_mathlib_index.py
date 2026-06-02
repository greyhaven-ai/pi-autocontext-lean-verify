#!/usr/bin/env python3
"""Unit tests for harness/build_mathlib_index.py (issue #4).

Pure tests: no Lean, no Mathlib. They cover the source parser (namespace scoping,
docstrings, private skipping, signature capture), the JSONL `--from-dump` path,
and that the produced index round-trips through mathlib_retrieval.load_index.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
HARNESS = PACKAGE / "harness"
sys.path.insert(0, str(HARNESS))

import build_mathlib_index as bmi  # noqa: E402
import mathlib_retrieval as mr  # noqa: E402

SAMPLE = """\
import Mathlib

namespace Nat

/-- Addition on the naturals is commutative. -/
theorem add_comm (n m : ℕ) : n + m = m + n := by
  induction n

private theorem secret_helper : True := trivial

section Ordering

/-- Multi-line
docstring for le_refl. -/
@[simp]
theorem le_refl (n : ℕ) :
    n ≤ n :=
  Nat.le.refl

end Ordering

def double (n : ℕ) : ℕ := n + n

end Nat

theorem standalone (p : Prop) : p → p := fun h => h
"""


class SourceParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.decls = bmi.extract_declarations(SAMPLE)
        self.by_name = {d.name: d for d in self.decls}

    def test_namespace_qualified_names(self) -> None:
        self.assertIn("Nat.add_comm", self.by_name)
        self.assertIn("Nat.le_refl", self.by_name)  # inside namespace + section
        self.assertIn("Nat.double", self.by_name)
        self.assertIn("standalone", self.by_name)  # after `end Nat`, no prefix

    def test_private_is_skipped(self) -> None:
        self.assertNotIn("Nat.secret_helper", self.by_name)

    def test_docstring_attached(self) -> None:
        self.assertIn("commutative", self.by_name["Nat.add_comm"].doc)
        self.assertIn("Multi-line docstring", self.by_name["Nat.le_refl"].doc)
        # double has no docstring
        self.assertEqual(self.by_name["Nat.double"].doc, "")

    def test_signature_capture_strips_body(self) -> None:
        sig = self.by_name["Nat.add_comm"].signature
        self.assertIn("n + m = m + n", sig)
        self.assertNotIn(":=", sig)
        # multi-line signature is joined to one line
        self.assertIn("n ≤ n", self.by_name["Nat.le_refl"].signature)


class FromDumpTests(unittest.TestCase):
    def test_parse_jsonl_dump(self) -> None:
        dump = "\n".join(
            [
                json.dumps({"name": "A.b", "signature": "sig1", "doc": "d1"}),
                "",
                json.dumps({"name": "C.d", "signature": "sig2"}),
                json.dumps({"signature": "no name -> skipped"}),
            ]
        )
        decls = bmi.parse_dump(dump)
        self.assertEqual([d.name for d in decls], ["A.b", "C.d"])
        self.assertEqual(decls[1].doc, "")


class RoundTripTests(unittest.TestCase):
    def test_written_index_loads_via_retrieval(self) -> None:
        decls = bmi.extract_declarations(SAMPLE)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "index.json"
            bmi.write_index(decls, out)
            loaded = mr.load_index(out)
            names = {d.name for d in loaded}
            self.assertIn("Nat.add_comm", names)
            # the produced index is directly usable by retrieval ranking
            block = mr.lemma_block_for(
                template="theorem t : True",
                feedback="error: unknown identifier 'Nat.add_comm'",
                index=loaded,
            )
            self.assertIn("Nat.add_comm", block)


class IncludeNamespaceFilterTests(unittest.TestCase):
    def test_build_index_filters_by_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "F.lean").write_text(SAMPLE, encoding="utf-8")
            decls = bmi.build_index(root, include_namespaces=["Nat"])
            names = {d.name for d in decls}
            self.assertIn("Nat.add_comm", names)
            self.assertNotIn("standalone", names)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Unit tests for harness/mathlib_retrieval.py and its prompt integration (issue #1).

Pure tests: no Lean, no Mathlib, no network. They exercise ranking, the rendered
block, and that the default (Init-only) repair prompt is unchanged when no lemma
block is supplied.
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

import mathlib_retrieval as mr  # noqa: E402

INDEX = [
    mr.Declaration(
        name="Set.indicator_of_notMem",
        signature="a ∉ s → s.indicator f a = 0",
        doc="The indicator of a set is zero outside the set.",
    ),
    mr.Declaration(
        name="Continuous.integrable_of_hasCompactSupport",
        signature="Continuous f → HasCompactSupport f → Integrable f",
        doc="A continuous function with compact support is integrable.",
    ),
    mr.Declaration(
        name="Nat.add_comm",
        signature="∀ (n m : ℕ), n + m = m + n",
        doc="Addition on the naturals is commutative.",
    ),
]


class RetrievalRankingTests(unittest.TestCase):
    def test_named_identifier_in_feedback_ranks_first(self) -> None:
        # The verifier names a renamed lemma; retrieval should float the real one up.
        feedback = "error: unknown identifier 'Set.indicator_of_notMem'"
        block = mr.lemma_block_for(
            template="theorem t : True := by", feedback=feedback, index=INDEX
        )
        self.assertIn("Set.indicator_of_notMem", block)
        # And it should be the first candidate listed.
        first_line = next(line for line in block.splitlines() if line.startswith("- `"))
        self.assertIn("Set.indicator_of_notMem", first_line)

    def test_topical_query_matches_by_signature_and_doc(self) -> None:
        query = "Continuous compact support Integrable"
        results = mr.retrieve(query, INDEX, limit=3)
        self.assertTrue(results)
        self.assertEqual(results[0].name, "Continuous.integrable_of_hasCompactSupport")

    def test_no_match_returns_empty_block(self) -> None:
        block = mr.lemma_block_for(
            template="", feedback="zzzqqq nonsense token", index=INDEX
        )
        self.assertEqual(block, "")

    def test_empty_index_is_noop(self) -> None:
        self.assertEqual(mr.retrieve("anything", [], limit=5), [])
        self.assertEqual(mr.format_lemma_block([]), "")


class IndexLoadingTests(unittest.TestCase):
    def test_missing_path_returns_empty(self) -> None:
        self.assertEqual(mr.load_index(None), [])
        self.assertEqual(mr.load_index("/nonexistent/path/index.json"), [])

    def test_loads_list_and_dict_shapes(self) -> None:
        records = [{"name": "A.b", "signature": "sig", "doc": "d"}]
        with tempfile.TemporaryDirectory() as tmp:
            list_path = Path(tmp) / "list.json"
            list_path.write_text(json.dumps(records), encoding="utf-8")
            dict_path = Path(tmp) / "dict.json"
            dict_path.write_text(
                json.dumps({"declarations": records}), encoding="utf-8"
            )
            for path in (list_path, dict_path):
                with self.subTest(path=path):
                    decls = mr.load_index(path)
                    self.assertEqual(len(decls), 1)
                    self.assertEqual(decls[0].name, "A.b")


class PromptIntegrationTests(unittest.TestCase):
    """Guard the byte-identical default prompt and the opt-in mathlib prompt."""

    def setUp(self) -> None:
        # build_repair_prompt reads the template by fixture name; use a bundled one.
        import prove_with_autocontext as pwa

        self.pwa = pwa
        self.kwargs = dict(
            fixture="add_zero_right",
            proof="rfl",
            verification={"ok": False, "stderr": "error: tactic failed"},
            attempt_index=0,
            history=[],
        )

    def test_default_prompt_is_init_only_and_has_no_lemma_block(self) -> None:
        prompt = self.pwa.build_repair_prompt(**self.kwargs)
        self.assertIn("Use Lean core/Init facts only; no Mathlib imports.", prompt)
        self.assertNotIn("Relevant existing library lemmas", prompt)
        self.assertIn("new imports, or a modified theorem statement.", prompt)

    def test_mathlib_prompt_injects_block_and_relaxes_imports(self) -> None:
        block = mr.format_lemma_block(INDEX[:1])
        prompt = self.pwa.build_repair_prompt(
            **self.kwargs, lemma_block=block, allow_mathlib=True
        )
        self.assertIn("Relevant existing library lemmas", prompt)
        self.assertIn("Set.indicator_of_notMem", prompt)
        self.assertIn("Mathlib is available", prompt)
        self.assertNotIn("no Mathlib imports", prompt)


if __name__ == "__main__":
    unittest.main()

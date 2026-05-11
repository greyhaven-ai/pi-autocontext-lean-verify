#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
HARNESS = PACKAGE / "harness"
FIXTURE_GROUPS = PACKAGE / "fixture_groups.json"
EXTENSION = PACKAGE / "extensions" / "lean-verify.ts"
VALIDATION_DOC = PACKAGE / "docs" / "VALIDATION.md"
README = PACKAGE / "README.md"
SKILL = PACKAGE / "skills" / "lean-verify" / "SKILL.md"
PACKAGE_JSON = PACKAGE / "package.json"
LICENSE = PACKAGE / "LICENSE"
PROVE_WITH_AUTOCONTEXT = HARNESS / "prove_with_autocontext.py"
MANIFEST = HARNESS / "benchmark_manifest.json"
DEFAULT_SEED_PLAYBOOK = HARNESS / "playbooks" / "expanded_mixed_cluster_v1.md"
PUBLISH_WORKFLOW = PACKAGE / ".github" / "workflows" / "publish.yml"

class StandaloneRepoValidationTests(unittest.TestCase):
    def manifest_fixture_ids(self) -> set[str]:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        return {fixture["id"] for fixture in manifest["fixtures"]}

    def fixture_groups(self) -> dict[str, list[str]]:
        return json.loads(FIXTURE_GROUPS.read_text(encoding="utf-8"))["groups"]

    def test_bundled_harness_runtime_exists(self) -> None:
        for path in [
            MANIFEST,
            DEFAULT_SEED_PLAYBOOK,
            HARNESS / "run_playbook_transfer.py",
            HARNESS / "verify_lean_proof.py",
            HARNESS / "fixtures" / "add_zero_right" / "Theorem.template.lean",
        ]:
            with self.subTest(path=path):
                self.assertTrue(path.exists(), f"missing bundled harness path: {path}")

    def test_fixture_groups_match_manifest(self) -> None:
        groups = self.fixture_groups()
        manifest_ids = self.manifest_fixture_ids()
        self.assertEqual(groups["combined"], groups["broader"] + groups["heldout"])
        self.assertEqual(len(groups["negative_controls"]), 6)
        for name, fixtures in groups.items():
            with self.subTest(group=name):
                self.assertTrue(fixtures)
                self.assertEqual(len(fixtures), len(set(fixtures)))
                self.assertTrue(set(fixtures).issubset(manifest_ids))

    def test_extension_defaults_to_bundled_harness_and_runtime_playbook(self) -> None:
        text = EXTENSION.read_text(encoding="utf-8")
        self.assertIn('resolve(packageRoot, "harness")', text)
        self.assertIn("legacyHarnessRoot", text)
        self.assertIn("playbooks/expanded_mixed_cluster_v1.md", text)

    def test_challenge_fixtures_are_verifier_only_without_expected_proofs(self) -> None:
        groups = self.fixture_groups()
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        by_id = {fixture["id"]: fixture for fixture in manifest["fixtures"]}
        for group_name in [
            "challenge_v2_no_helper",
            "challenge_v3_generalization",
            "challenge_transfer",
            "challenge_v4_count",
            "challenge_v5_attribution",
            "challenge_v5_tree_tally",
            "challenge_extended_transfer",
        ]:
            with self.subTest(group=group_name):
                self.assertIn(group_name, groups)
                self.assertTrue(groups[group_name])
        for fixture_id in groups["challenge_extended_transfer"]:
            with self.subTest(fixture=fixture_id):
                fixture_dir = HARNESS / "fixtures" / fixture_id
                self.assertTrue((fixture_dir / "Theorem.template.lean").exists())
                self.assertFalse((fixture_dir / "expected_proof.lean").exists())
                self.assertIs(by_id[fixture_id].get("expected_proof"), False)

    def test_validation_docs_capture_current_evidence(self) -> None:
        text = VALIDATION_DOC.read_text(encoding="utf-8")
        for required in ["52 / 52", "42 / 42", "45 / 45", "6 / 6", "12 / 12", "3 / 3", "1 / 3"]:
            with self.subTest(required=required):
                self.assertIn(required, text)
        combined = README.read_text(encoding="utf-8") + "\n" + SKILL.read_text(encoding="utf-8")
        self.assertIn('"fixtureGroup": "negative_controls"', combined)
        self.assertIn('"maxAttempts": 3', combined)


    def test_pi_dependencies_use_earendil_namespace(self) -> None:
        package_json = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
        dependencies = package_json.get("dependencies", {})
        self.assertIn("@earendil-works/pi-ai", dependencies)
        self.assertIn("@earendil-works/pi-coding-agent", dependencies)
        self.assertIn("typebox", dependencies)
        serialized = json.dumps(package_json) + EXTENSION.read_text(encoding="utf-8")
        self.assertNotIn("@mariozechner", serialized)
        extension_text = EXTENSION.read_text(encoding="utf-8")
        self.assertIn('from "@earendil-works/pi-ai"', extension_text)
        self.assertIn('from "@earendil-works/pi-coding-agent"', extension_text)

    def test_benchmark_defaults_use_short_temp_run_roots(self) -> None:
        extension_text = EXTENSION.read_text(encoding="utf-8")
        transfer_runner = (HARNESS / "run_proof_transfer_benchmark.py").read_text(encoding="utf-8")
        attribution_runner = (HARNESS / "run_attribution_benchmark.py").read_text(encoding="utf-8")
        self.assertIn('from "node:os"', extension_text)
        self.assertIn("defaultShortRunRoot", extension_text)
        self.assertIn("AUTOCONTEXT_LEAN_VERIFY_RESULTS_ROOT", extension_text)
        self.assertIn("tmpdir()", extension_text)
        self.assertIn("tempfile.gettempdir()", transfer_runner)
        self.assertIn("tempfile.gettempdir()", attribution_runner)
        self.assertIn("default_run_root", transfer_runner)
        self.assertIn("default_run_root", attribution_runner)

    def test_autocontext_runtime_dependency_contract_is_explicit(self) -> None:
        proof_runner = PROVE_WITH_AUTOCONTEXT.read_text(encoding="utf-8")
        self.assertIn('"uvx"', proof_runner)
        self.assertIn('"autoctx"', proof_runner)
        self.assertIn('f"autocontext=={package_version}"', proof_runner)
        extension_text = EXTENSION.read_text(encoding="utf-8")
        self.assertIn("autocontextRuntimeCheck", extension_text)
        combined_docs = README.read_text(encoding="utf-8") + "\n" + VALIDATION_DOC.read_text(encoding="utf-8")
        self.assertIn("uvx", combined_docs)
        self.assertIn("autocontext==0.4.8", combined_docs)
        self.assertIn("autoctx improve", combined_docs)


    def test_apache_license_is_declared_and_packaged(self) -> None:
        package_json = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
        self.assertEqual(package_json.get("license"), "Apache-2.0")
        self.assertTrue(LICENSE.exists())
        license_text = LICENSE.read_text(encoding="utf-8")
        self.assertIn("Apache License", license_text)
        self.assertIn("Version 2.0", license_text)
        self.assertIn("Grey Haven AI", license_text)


    def test_npm_trusted_publisher_configuration_is_explicit(self) -> None:
        package_json = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
        publish_config = package_json.get("publishConfig", {})
        self.assertEqual(publish_config.get("access"), "public")
        self.assertTrue(publish_config.get("provenance"))
        self.assertTrue(PUBLISH_WORKFLOW.exists())
        workflow = PUBLISH_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("publish-pi-autocontext-lean-verify", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn("tags:", workflow)
        self.assertIn('"v*"', workflow)
        self.assertIn("actions/setup-node@v6", workflow)
        self.assertIn("npm install -g npm@latest", workflow)
        self.assertIn("NPM_CONFIG_PROVENANCE", workflow)
        self.assertNotIn("ACTIONS_ID_TOKEN_REQUEST_URL", workflow)
        self.assertIn("unset NODE_AUTH_TOKEN NPM_TOKEN", workflow)
        self.assertIn("npm publish --provenance --access public", workflow)
        self.assertIn("Verify release tag matches package version", workflow)
        self.assertNotIn("secrets.NPM_TOKEN", workflow)
        self.assertNotIn("NODE_AUTH_TOKEN: ${{", workflow)

    def test_npm_pack_includes_harness_but_excludes_results_and_tests(self) -> None:
        result = subprocess.run(
            ["npm", "pack", "--dry-run", "--json"],
            cwd=PACKAGE,
            text=True,
            capture_output=True,
            check=True,
        )
        paths = {entry["path"] for entry in json.loads(result.stdout)[0]["files"]}
        required = {
            "LICENSE",
            "README.md",
            "extensions/lean-verify.ts",
            "fixture_groups.json",
            "harness/benchmark_manifest.json",
            "harness/playbooks/expanded_mixed_cluster_v1.md",
            "harness/playbooks/challenge_v2_no_helper_v1.md",
            "harness/playbooks/challenge_v3_generalization_v1.md",
            "harness/playbooks/challenge_v4_count_v1.md",
            "harness/run_playbook_transfer.py",
            "harness/run_direct_baseline_benchmark.py",
            "harness/direct_pi_prove.py",
            "harness/run_proof_transfer_benchmark.py",
            "harness/run_attribution_benchmark.py",
            "harness/fixtures/add_zero_right/Theorem.template.lean",
            "harness/fixtures/challenge_v3_map_rev_append_combined/Theorem.template.lean",
            "harness/fixtures/challenge_v5_tree_tally_mirror/Theorem.template.lean",
        }
        self.assertTrue(required.issubset(paths))
        self.assertFalse(any(path.startswith("harness/results/") for path in paths))
        self.assertFalse(any(path.startswith("tests/") for path in paths))

if __name__ == "__main__":
    unittest.main()

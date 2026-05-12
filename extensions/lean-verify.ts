import { existsSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { StringEnum } from "@earendil-works/pi-ai";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import {
	DEFAULT_MAX_BYTES,
	DEFAULT_MAX_LINES,
	truncateTail,
} from "@earendil-works/pi-coding-agent";
import { type Static, Type } from "typebox";

const packageRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const bundledHarnessRoot = resolve(packageRoot, "harness");
const legacyHarnessRoot = resolve(packageRoot, "..");
const fixtureGroupsPath = resolve(packageRoot, "fixture_groups.json");

const FIXTURE_GROUP_NAMES = [
	"smoke",
	"broader",
	"heldout",
	"combined",
	"negative_controls",
	"challenge_v2_no_helper",
	"challenge_v3_generalization",
	"challenge_transfer",
	"challenge_v4_count",
	"challenge_v5_attribution",
	"challenge_v5_tree_tally",
	"challenge_v6_frontier",
	"challenge_v7_frontier",
	"challenge_v8_diagnostics",
	"challenge_v9_composition_gradient",
	"challenge_v10_stats_reification",
	"challenge_v11_metric_composition",
	"challenge_v12_simultaneous_metrics",
	"challenge_v13_decomposition_order",
	"challenge_v14_metric_order_permutations",
	"challenge_v15_proof_shape_hints",
	"challenge_v16_compact_reassembly_hints",
	"challenge_extended_transfer",
] as const;

type FixtureGroupName = (typeof FIXTURE_GROUP_NAMES)[number];
type FixtureGroupRegistry = { groups: Record<FixtureGroupName, string[]> };

const AUTOCONTEXT_PACKAGE_VERSION = "0.4.8";

const formalProofSchema = Type.Object({
	action: StringEnum(["preflight", "setup", "run", "benchmark", "attribution", "summarize"] as const, {
		description: "Workflow action to execute.",
	}),
	fixtures: Type.Optional(
		Type.Array(Type.String(), {
			description:
				"Fixture ids to run. Defaults to a small smoke set for run actions.",
		}),
	),
	fixtureGroup: Type.Optional(
		StringEnum(FIXTURE_GROUP_NAMES, {
			description:
				"Named fixture group to run when fixtures is omitted. Defaults to broader for run actions, challenge_v3_generalization for benchmark actions, and challenge_v5_attribution for attribution actions. Includes frontier groups through challenge_v16_compact_reassembly_hints.",
		}),
	),
	mode: Type.Optional(
		StringEnum(
			[
				"seeded_pregenerate",
				"pre_repair_hint",
				"post_repair_hint",
				"structured_retry",
			] as const,
			{
				description:
					"Named workflow mode. pre_repair_hint is the current strongest repair-only mode.",
			},
		),
	),
	harnessRoot: Type.Optional(
		Type.String({
			description:
				"Path to formal-proof-lean-pilot harness root. Defaults to AUTOCONTEXT_FORMAL_ROOT, a bundled harness directory, or the parent directory of this local package.",
		}),
	),
	seedPlaybook: Type.Optional(
		Type.String({
			description: "Path to a verified playbook.md used to seed transfer.",
		}),
	),
	runRoot: Type.Optional(
		Type.String({
			description: "Directory for run artifacts or summary lookup.",
		}),
	),
	maxAttempts: Type.Optional(Type.Integer({ minimum: 1, default: 2 })),
	rounds: Type.Optional(Type.Integer({ minimum: 1, default: 2 })),
	timeoutSeconds: Type.Optional(Type.Integer({ minimum: 10, default: 60 })),
});

type FormalProofInput = Static<typeof formalProofSchema>;

function compactTimestamp(): string {
	return new Date().toISOString().replace(/[-:.]/g, "").slice(0, 15);
}

function defaultShortRunRoot(kind: string, group: string): string {
	return resolve(
		process.env.AUTOCONTEXT_LEAN_VERIFY_RESULTS_ROOT ||
			resolve(tmpdir(), "pi-autocontext-lean-verify"),
		`${compactTimestamp()}_${kind}_${group}`,
	);
}

function defaultHarnessRoot(): string {
	return existsSync(bundledHarnessRoot)
		? bundledHarnessRoot
		: legacyHarnessRoot;
}

function harnessRoot(params: FormalProofInput): string {
	return resolve(
		params.harnessRoot ||
			process.env.AUTOCONTEXT_FORMAL_ROOT ||
			defaultHarnessRoot(),
	);
}

function leanBinary(): string {
	return (
		process.env.LEAN ||
		process.env.AUTOCONTEXT_LEAN ||
		"/tmp/autocontext-elan-home/bin/lean"
	);
}

function elanHomeForLean(lean: string): string | undefined {
	if (process.env.ELAN_HOME) return process.env.ELAN_HOME;
	if (lean.endsWith("/bin/lean")) return resolve(dirname(lean), "..");
	return undefined;
}

function fixtureGroupRegistry(): FixtureGroupRegistry {
	return readJson(fixtureGroupsPath) as FixtureGroupRegistry;
}

function fixtureGroupFixtures(group: string | undefined): string[] {
	const groups = fixtureGroupRegistry().groups;
	const groupName = (
		group && group in groups ? group : "broader"
	) as FixtureGroupName;
	return [...groups[groupName]];
}

function selectedFixtures(params: FormalProofInput): string[] {
	return params.fixtures?.length
		? params.fixtures
		: fixtureGroupFixtures(params.fixtureGroup);
}

function defaultSeedPlaybook(root: string): string {
	return resolve(root, "playbooks/expanded_mixed_cluster_v1.md");
}

function modeArgs(mode: string): string[] {
	switch (mode) {
		case "seeded_pregenerate":
			return [
				"--structured-alternate-retry",
				"--structured-hint-candidates",
				"--pre-repair-hint-candidates",
			];
		case "post_repair_hint":
			return [
				"--no-pregenerate",
				"--structured-alternate-retry",
				"--structured-hint-candidates",
			];
		case "structured_retry":
			return ["--no-pregenerate", "--structured-alternate-retry"];
		case "pre_repair_hint":
		default:
			return [
				"--no-pregenerate",
				"--structured-alternate-retry",
				"--structured-hint-candidates",
				"--pre-repair-hint-candidates",
			];
	}
}

function readJson(path: string): unknown {
	return JSON.parse(readFileSync(path, "utf8"));
}

function formatTriggerMetrics(metrics: Record<string, unknown> = {}): string[] {
	return [
		`Pi calls: ${metrics.pi_calls ?? "unknown"}`,
		`Pi elapsed seconds: ${metrics.pi_elapsed_seconds ?? "unknown"}`,
		`Lean verifier attempts: ${metrics.total_lean_verifier_attempts ?? "unknown"}`,
		`Pre-repair hints generated/passed/used: ${metrics.pre_repair_strategy_hint_candidates_generated ?? 0}/${metrics.pre_repair_strategy_hint_candidates_passed ?? 0}/${metrics.pre_repair_strategy_hint_candidates_used ?? 0}`,
		`Primary repair calls: ${metrics.primary_repair_calls ?? 0}`,
		`Alternate Pi fallback calls: ${metrics.alternate_pi_fallback_calls ?? 0}`,
	];
}

function formatMethodComparison(methods: unknown): string[] {
	if (!Array.isArray(methods)) return [];
	return methods.map((method) => {
		const row = method as Record<string, unknown>;
		return `- ${row.method}: ${row.proved_fixture_trials}/${row.fixture_trials} fixture-trials, success=${row.success_rate}, Pi calls/run=${row.pi_calls_per_run}, Lean attempts/run=${row.lean_attempts_per_run ?? "n/a"}`;
	});
}

function summarizeRun(root: string): string {
	const attributionPath = resolve(root, "attribution_benchmark_summary.json");
	const benchmarkPath = resolve(root, "proof_transfer_benchmark_summary.json");
	const transferPath = resolve(root, "transfer_summary.json");
	const variancePath = resolve(root, "variance_summary.json");
	const directPath = resolve(root, "direct_baseline_summary.json");
	if (existsSync(attributionPath)) {
		const summary = readJson(attributionPath) as {
			fixture_group?: string;
			methods?: Record<string, Record<string, unknown> | null>;
		};
		const methods = Object.entries(summary.methods || {}).map(([method, stats]) => {
			if (!stats) return `- ${method}: missing`;
			return `- ${method}: ${stats.proved}/${stats.total} proved, Pi calls=${stats.pi_calls}, Pi elapsed=${stats.pi_elapsed_seconds}s`;
		});
		return [
			`Proof-transfer attribution benchmark: ${summary.fixture_group ?? "unknown group"}`,
			...methods,
		].join("\n");
	}
	if (existsSync(benchmarkPath)) {
		const summary = readJson(benchmarkPath) as {
			fixture_group?: string;
			methods?: Record<string, Record<string, unknown> | null>;
		};
		const methods = Object.entries(summary.methods || {}).map(([method, stats]) => {
			if (!stats) return `- ${method}: missing`;
			return `- ${method}: ${stats.proved}/${stats.total} proved, Pi calls=${stats.pi_calls}, Pi elapsed=${stats.pi_elapsed_seconds}s`;
		});
		return [
			`Proof-transfer benchmark: ${summary.fixture_group ?? "unknown group"}`,
			...methods,
		].join("\n");
	}
	if (existsSync(transferPath)) {
		const summary = readJson(transferPath) as {
			total?: number;
			proved?: number;
			failed?: number;
			rows?: Array<{ fixture: string; proved: boolean }>;
			trigger_cost_metrics?: Record<string, unknown>;
		};
		const failures = (summary.rows || [])
			.filter((row) => !row.proved)
			.map((row) => row.fixture);
		return [
			`Transfer summary: ${summary.proved}/${summary.total} proved, failed=${summary.failed}`,
			`Failures: ${failures.length ? failures.join(", ") : "none"}`,
			...formatTriggerMetrics(summary.trigger_cost_metrics),
		].join("\n");
	}
	if (existsSync(variancePath)) {
		const summary = readJson(variancePath) as {
			aggregate?: Record<string, unknown>;
			method_comparison?: unknown;
		};
		const aggregate = summary.aggregate || {};
		return [
			`Variance summary: ${aggregate.proved_fixture_trials ?? "unknown"}/${aggregate.fixture_trials ?? "unknown"} fixture-trials`,
			`Full-run success: ${aggregate.runs_with_all_fixtures_proved ?? "unknown"}/${aggregate.trials ?? "unknown"}`,
			`Fixture-trial success rate: ${aggregate.fixture_trial_success_rate ?? "unknown"}`,
			"Method comparison:",
			...formatMethodComparison(summary.method_comparison),
		]
			.filter(Boolean)
			.join("\n");
	}
	if (existsSync(directPath)) {
		const summary = readJson(directPath) as {
			by_mode?: Record<
				string,
				{ proved?: number; total?: number; failed?: number }
			>;
		};
		const modes = Object.entries(summary.by_mode || {}).map(
			([mode, stats]) =>
				`- ${mode}: ${stats.proved}/${stats.total} proved, failed=${stats.failed}`,
		);
		return ["Direct baseline summary:", ...modes].join("\n");
	}
	throw new Error(`No known summary file found under ${root}`);
}

async function autocontextRuntimeCheck(
	pi: ExtensionAPI,
	signal?: AbortSignal,
): Promise<string[]> {
	const checks: string[] = [];
	try {
		const uvxVersion = await pi.exec("uvx", ["--version"], {
			signal,
			timeout: 10_000,
		});
		checks.push(
			`uvx: ${(uvxVersion.stdout || uvxVersion.stderr).trim() || `exit ${uvxVersion.code}`}`,
		);
	} catch (error) {
		checks.push(`uvx: missing (${String(error)})`);
		return checks;
	}

	try {
		const autoctxHelp = await pi.exec(
			"/usr/bin/env",
			[
				"-u",
				"UV_EXCLUDE_NEWER",
				"uvx",
				"--python",
				"3.12",
				"--from",
				`autocontext==${AUTOCONTEXT_PACKAGE_VERSION}`,
				"autoctx",
				"improve",
				"--help",
			],
			{ signal, timeout: 120_000 },
		);
		const ok = autoctxHelp.code === 0;
		checks.push(
			`Autocontext runtime: autocontext==${AUTOCONTEXT_PACKAGE_VERSION} via uvx autoctx improve (${ok ? "ok" : `exit ${autoctxHelp.code}`})`,
		);
	} catch (error) {
		checks.push(
			`Autocontext runtime: autocontext==${AUTOCONTEXT_PACKAGE_VERSION} via uvx autoctx improve missing (${String(error)})`,
		);
	}
	return checks;
}

async function preflight(
	pi: ExtensionAPI,
	params: FormalProofInput,
	signal?: AbortSignal,
) {
	const root = harnessRoot(params);
	const lean = leanBinary();
	const manifest = resolve(root, "benchmark_manifest.json");
	const runner = resolve(root, "run_playbook_transfer.py");
	const seed = params.seedPlaybook || defaultSeedPlaybook(root);
	const checks: string[] = [];
	checks.push(`Harness root: ${root} (${existsSync(root) ? "ok" : "missing"})`);
	checks.push(
		`Manifest: ${manifest} (${existsSync(manifest) ? "ok" : "missing"})`,
	);
	checks.push(`Runner: ${runner} (${existsSync(runner) ? "ok" : "missing"})`);
	checks.push(
		`Seed playbook: ${seed} (${existsSync(seed) ? "ok" : "missing"})`,
	);
	checks.push(`Lean binary: ${lean} (${existsSync(lean) ? "ok" : "missing"})`);

	const elanHome = elanHomeForLean(lean);
	if (elanHome) {
		checks.push(`ELAN_HOME for Lean: ${elanHome}`);
	}
	const leanVersion = existsSync(lean)
		? await pi.exec(
				"/usr/bin/env",
				[...(elanHome ? [`ELAN_HOME=${elanHome}`] : []), lean, "--version"],
				{ signal, timeout: 10_000 },
			)
		: undefined;
	const pythonVersion = await pi.exec("python3", ["--version"], {
		signal,
		timeout: 10_000,
	});
	if (leanVersion) {
		checks.push(
			`Lean version: ${(leanVersion.stdout || leanVersion.stderr).trim()}`,
		);
	}
	checks.push(
		`Python: ${(pythonVersion.stdout || pythonVersion.stderr).trim()}`,
	);
	checks.push(...(await autocontextRuntimeCheck(pi, signal)));

	if (existsSync(manifest)) {
		const parsed = readJson(manifest) as { fixtures?: unknown[] };
		checks.push(`Fixture count: ${parsed.fixtures?.length ?? "unknown"}`);
	}
	const fixtureGroups = fixtureGroupRegistry().groups;
	checks.push(
		`Fixture groups: ${FIXTURE_GROUP_NAMES.map((name) => `${name}=${fixtureGroups[name].length}`).join(", ")}`,
	);
	return checks.join("\n");
}

async function runHarness(
	pi: ExtensionAPI,
	params: FormalProofInput,
	signal: AbortSignal | undefined,
	root: string,
) {
	const fixtures = selectedFixtures(params);
	const mode = params.mode || "pre_repair_hint";
	const runRoot =
		params.runRoot ||
		`results/pi_package_${mode}_${new Date().toISOString().replace(/[-:.]/g, "").slice(0, 15)}`;
	const args = [
		"run_playbook_transfer.py",
		"--fixtures",
		...fixtures,
		"--seed-playbook",
		params.seedPlaybook || defaultSeedPlaybook(root),
		...modeArgs(mode),
		"--max-attempts",
		String(params.maxAttempts ?? 2),
		"--rounds",
		String(params.rounds ?? 2),
		"--timeout",
		String(params.timeoutSeconds ?? 60),
		"--run-root",
		runRoot,
	];
	const timeoutMs = Math.max(
		120_000,
		(params.timeoutSeconds ?? 60) * Math.max(fixtures.length, 1) * 3_000,
	);
	const result = await pi.exec("python3", args, {
		cwd: root,
		signal,
		timeout: timeoutMs,
	});
	const update = await pi.exec("python3", ["update_results_index.py"], {
		cwd: root,
		signal,
		timeout: 120_000,
	});
	const output = [
		`Run root: ${resolve(root, runRoot)}`,
		`Exit code: ${result.code}`,
		summarizeRun(resolve(root, runRoot)),
		"",
		"Runner stdout/stderr tail:",
		result.stdout,
		result.stderr,
		"",
		"Index update:",
		update.stdout,
		update.stderr,
	].join("\n");
	const truncated = truncateTail(output, {
		maxBytes: DEFAULT_MAX_BYTES,
		maxLines: DEFAULT_MAX_LINES,
	});
	return {
		content: [{ type: "text", text: truncated.content }],
		details: {
			root,
			runRoot: resolve(root, runRoot),
			mode,
			fixtures,
			exitCode: result.code,
			truncated: truncated.truncated,
		},
	};
}

async function runBenchmark(
	pi: ExtensionAPI,
	params: FormalProofInput,
	signal: AbortSignal | undefined,
	root: string,
) {
	const group = params.fixtureGroup || "challenge_v3_generalization";
	const fixtures = params.fixtures?.length
		? params.fixtures
		: fixtureGroupFixtures(group);
	const runRoot = params.runRoot || defaultShortRunRoot("benchmark", group);
	const args = [
		"run_proof_transfer_benchmark.py",
		"--fixture-group",
		group,
		"--fixtures",
		...fixtures,
		"--max-attempts",
		String(params.maxAttempts ?? 2),
		"--rounds",
		String(params.rounds ?? 2),
		"--timeout",
		String(params.timeoutSeconds ?? 120),
		"--run-root",
		runRoot,
	];
	if (params.seedPlaybook) {
		args.push("--seed-playbook", params.seedPlaybook);
	}
	const timeoutMs = Math.max(
		600_000,
		(params.timeoutSeconds ?? 120) * Math.max(fixtures.length, 1) * Math.max(params.maxAttempts ?? 2, 1) * 3_000,
	);
	const result = await pi.exec("python3", args, {
		cwd: root,
		signal,
		timeout: timeoutMs,
	});
	const output = [
		`Benchmark root: ${resolve(root, runRoot)}`,
		`Exit code: ${result.code}`,
		summarizeRun(resolve(root, runRoot)),
		"",
		"Benchmark stdout/stderr tail:",
		result.stdout,
		result.stderr,
	].join("\n");
	const truncated = truncateTail(output, {
		maxBytes: DEFAULT_MAX_BYTES,
		maxLines: DEFAULT_MAX_LINES,
	});
	return {
		content: [{ type: "text", text: truncated.content }],
		details: {
			root,
			runRoot: resolve(root, runRoot),
			fixtureGroup: group,
			fixtures,
			exitCode: result.code,
			truncated: truncated.truncated,
		},
	};
}

async function runAttributionBenchmark(
	pi: ExtensionAPI,
	params: FormalProofInput,
	signal: AbortSignal | undefined,
	root: string,
) {
	const group = params.fixtureGroup || "challenge_v5_attribution";
	const fixtures = params.fixtures?.length
		? params.fixtures
		: fixtureGroupFixtures(group);
	const runRoot = params.runRoot || defaultShortRunRoot("attribution", group);
	const args = [
		"run_attribution_benchmark.py",
		"--fixture-group",
		group,
		"--fixtures",
		...fixtures,
		"--max-attempts",
		String(params.maxAttempts ?? 2),
		"--rounds",
		String(params.rounds ?? 2),
		"--timeout",
		String(params.timeoutSeconds ?? 120),
		"--run-root",
		runRoot,
	];
	if (params.seedPlaybook) {
		args.push("--seed-playbook", params.seedPlaybook);
	}
	const perFixtureCommandTimeoutMs = Math.max(
		1_800_000,
		(params.timeoutSeconds ?? 120) * Math.max(params.maxAttempts ?? 2, 1) * 8_000 + 600_000,
	);
	const aggregateCommandTimeoutMs = Math.max(
		perFixtureCommandTimeoutMs * Math.max(fixtures.length, 1),
		3_600_000,
	);
	const timeoutMs =
		aggregateCommandTimeoutMs * 2 +
		perFixtureCommandTimeoutMs * Math.max(fixtures.length, 1) +
		600_000;
	const result = await pi.exec("python3", args, {
		cwd: root,
		signal,
		timeout: timeoutMs,
	});
	const output = [
		`Attribution benchmark root: ${resolve(root, runRoot)}`,
		`Exit code: ${result.code}`,
		summarizeRun(resolve(root, runRoot)),
		"",
		"Attribution stdout/stderr tail:",
		result.stdout,
		result.stderr,
	].join("\n");
	const truncated = truncateTail(output, {
		maxBytes: DEFAULT_MAX_BYTES,
		maxLines: DEFAULT_MAX_LINES,
	});
	return {
		content: [{ type: "text", text: truncated.content }],
		details: {
			root,
			runRoot: resolve(root, runRoot),
			fixtureGroup: group,
			fixtures,
			exitCode: result.code,
			truncated: truncated.truncated,
		},
	};
}

export default function formalProofExtension(pi: ExtensionAPI) {
	pi.registerTool({
		name: "autocontext_lean_verify",
		label: "Autocontext Lean Verify",
		description:
			"Run the experimental verifier-backed Lean proof repair harness using autocontext/Pi and Lean as the correctness oracle.",
		promptSnippet:
			"Run or summarize verifier-backed Lean proof repair experiments via autocontext_lean_verify.",
		promptGuidelines: [
			"Use autocontext_lean_verify only for the external Lean proof harness; Lean verification is the correctness oracle.",
			"Do not treat an LLM proof as successful unless autocontext_lean_verify reports Lean-verified success.",
			"Prefer autocontext_lean_verify action=preflight before long proof runs or when setting up the package.",
		],
		parameters: formalProofSchema,
		async execute(_toolCallId, params: FormalProofInput, signal) {
			const root = harnessRoot(params);
			if (params.action === "preflight") {
				return {
					content: [
						{ type: "text", text: await preflight(pi, params, signal) },
					],
					details: { root },
				};
			}

			if (params.action === "setup") {
				const setupRunRoot =
					params.runRoot ||
					`results/pi_package_setup_${new Date().toISOString().replace(/[-:.]/g, "").slice(0, 15)}`;
				const setupParams: FormalProofInput = {
					...params,
					action: "run",
					fixtures: ["add_zero_right"],
					fixtureGroup: undefined,
					mode: "pre_repair_hint",
					runRoot: setupRunRoot,
				};
				const preflightText = await preflight(pi, params, signal);
				const runResult = await runHarness(pi, setupParams, signal, root);
				return {
					content: [
						{
							type: "text",
							text: [
								"Setup preflight:",
								preflightText,
								"",
								"Smoke proof run:",
								runResult.content[0]?.text || "",
							].join("\n"),
						},
					],
					details: runResult.details,
				};
			}

			if (params.action === "benchmark") {
				return runBenchmark(pi, params, signal, root);
			}

			if (params.action === "attribution") {
				return runAttributionBenchmark(pi, params, signal, root);
			}

			if (params.action === "summarize") {
				const target = resolve(
					root,
					params.runRoot ||
						"results/20260506T_broader_fixture_baseline_comparison",
				);
				return {
					content: [{ type: "text", text: summarizeRun(target) }],
					details: { target },
				};
			}

			return runHarness(pi, params, signal, root);
		},
	});
}

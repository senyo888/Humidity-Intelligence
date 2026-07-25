import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import {
  LIMITS,
  parseDiagnosticsText,
} from "../site/inspector/parser.mjs";
import {
  createInspectionSession,
  readTextForInspection,
} from "../site/inspector/inspection-session.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const FIXTURES = path.join(ROOT, "tests 2", "fixtures", "hi_inspector");

const fixtureText = (name) =>
  fs.readFileSync(path.join(FIXTURES, name), "utf8");
const fixture = (name) => JSON.parse(fixtureText(name));
const parseObject = (value) => parseDiagnosticsText(JSON.stringify(value));

test("replacement and clear tokens suppress stale asynchronous file reads", async () => {
  let resolveFirst;
  const firstFile = {
    text: () =>
      new Promise((resolve) => {
        resolveFirst = resolve;
      }),
  };
  const session = createInspectionSession();
  const firstToken = session.begin();
  const pendingFirst = readTextForInspection(firstFile, session, firstToken);

  const replacementToken = session.begin();
  resolveFirst('{"stale":true}');
  assert.deepEqual(await pendingFirst, { status: "stale" });

  const pendingReplacement = readTextForInspection(
    { text: async () => '{"current":true}' },
    session,
    replacementToken,
  );
  assert.deepEqual(await pendingReplacement, {
    status: "ready",
    text: '{"current":true}',
  });

  let rejectAfterClear;
  const clearToken = session.begin();
  const pendingClear = readTextForInspection(
    {
      text: () =>
        new Promise((_resolve, reject) => {
          rejectAfterClear = reject;
        }),
    },
    session,
    clearToken,
  );
  session.invalidate();
  rejectAfterClear(new Error("stale read failure"));
  assert.deepEqual(await pendingClear, { status: "stale" });
});

test("current file read failures remain controlled errors", async () => {
  const session = createInspectionSession();
  const token = session.begin();
  const result = await readTextForInspection(
    {
      text: async () => {
        throw new Error("fixture read failure");
      },
    },
    session,
    token,
  );
  assert.deepEqual(result, { status: "error" });
});

test("native schema 1 exposes only allowlisted backend facts", () => {
  const text = fixtureText("native_schema1.json");
  const result = parseDiagnosticsText(text, Buffer.byteLength(text));

  assert.equal(result.ok, true);
  assert.equal(result.report.source.kind, "native-ha-diagnostics");
  assert.equal(result.report.integration.integrationVersion, "2.0.9-beta.1");
  assert.equal(result.report.integration.homeAssistantVersion, "2026.5.2");
  assert.equal(result.report.integration.schema, "1");
  assert.equal(result.report.runtime.activeLane, "alert");
  assert.equal(result.report.runtime.reasonAvailable, "Yes");
  assert.equal(result.report.runtime.reasonTruncated, "No");
  assert.deepEqual(result.report.generatedUi.cachedLayouts, [
    "v2_mobile",
    "v2_tablet",
  ]);
  assert.deepEqual(result.report.warnings.categories, [
    { category: "Entity availability", count: 2 },
  ]);

  const rendered = JSON.stringify(result.report);
  assert.doesNotMatch(rendered, /Humidity danger in|Kitchen|person\.alice/i);
  assert.doesNotMatch(rendered, /reason bodies|repair_steps/i);
});

test("Home Assistant diagnostics envelope adapts to the same native report", () => {
  const envelopeFixture = fixture("native_schema1_envelope.json");
  assert.deepEqual(envelopeFixture.issues, []);
  const direct = parseDiagnosticsText(fixtureText("native_schema1.json"));
  const enveloped = parseDiagnosticsText(
    fixtureText("native_schema1_envelope.json"),
  );

  assert.equal(enveloped.ok, true);
  assert.deepEqual(enveloped.report, direct.report);
});

test("dump summary cannot invent runtime or version truth", () => {
  const result = parseDiagnosticsText(fixtureText("dump_summary.json"));

  assert.equal(result.ok, true);
  assert.equal(result.report.source.kind, "dump-diagnostics-summary");
  assert.equal(result.report.integration.integrationVersion, "Not reported");
  assert.equal(result.report.integration.homeAssistantVersion, "Not reported");
  assert.equal(result.report.integration.schema, "Not reported");
  assert.equal(result.report.runtime.activeLane, "Not reported");
  assert.equal(result.report.runtime.reasonAvailable, "Not reported");
  assert.equal(result.report.runtime.gates.timeGate, "Not reported");
  assert.deepEqual(result.report.generatedUi.cachedLayouts, [
    "v2_mobile",
    "v2_tablet",
  ]);
});

test("privacy review reports categories without retaining matched values", () => {
  const payload = fixture("native_schema1.json");
  const privateUrl =
    "https://private.example.invalid/path?token=VeryPrivateToken_123456";
  payload.privacy.secret = "VeryPrivateToken_123456";
  payload.privacy.support_url = privateUrl;
  payload.privacy.owner_email = "fixture-owner@example.invalid";

  const result = parseObject(payload);
  assert.equal(result.ok, true);
  assert.ok(result.report.privacy.total >= 3);
  const categories = result.report.privacy.categories.map(
    (row) => row.category,
  );
  assert.ok(categories.includes("Secret-like field"));
  assert.ok(categories.includes("URL"));
  assert.ok(categories.includes("Email address"));

  const rendered = JSON.stringify(result.report);
  assert.doesNotMatch(rendered, /VeryPrivateToken_123456/);
  assert.doesNotMatch(rendered, /private\.example\.invalid/);
  assert.doesNotMatch(rendered, /fixture-owner@example\.invalid/);
});

test("unrecognized lane is withheld rather than normalized or inferred", () => {
  const payload = fixture("native_schema1.json");
  payload.runtime.active_lane = "future_parallel_engine";
  payload.runtime.current_state.runtime_mode = "future_parallel_engine";
  const result = parseObject(payload);

  assert.equal(result.ok, true);
  assert.equal(
    result.report.runtime.activeLane,
    "Withheld (unrecognized value)",
  );
});

test("every current backend runtime mode remains recognizable", () => {
  for (const mode of [
    "normal",
    "alert",
    "cooking",
    "bathroom",
    "zone",
    "air_quality",
    "global_gate",
    "telemetry_unavailable",
    "co_emergency",
  ]) {
    const payload = fixture("native_schema1.json");
    payload.runtime.active_lane = mode;
    payload.runtime.current_state.runtime_mode = mode;
    const result = parseObject(payload);
    assert.equal(result.ok, true, mode);
    assert.equal(result.report.runtime.activeLane, mode);
  }
});

test("malformed, mixed, expanded, contradictory and wrong-domain input fails closed", () => {
  assert.equal(parseDiagnosticsText("{not json").code, "malformed-json");
  assert.equal(parseDiagnosticsText("[]").code, "wrong-root");

  const wrongDomain = fixture("native_schema1.json");
  wrongDomain.integration.domain = "different_integration";
  assert.equal(parseObject(wrongDomain).code, "wrong-native-domain");

  const futureSchema = fixture("native_schema1.json");
  futureSchema.integration.diagnostics_schema = 2;
  assert.equal(parseObject(futureSchema).code, "unsupported-schema");

  const expanded = fixture("native_schema1.json");
  expanded.future_section = {};
  assert.equal(parseObject(expanded).code, "unsupported-native-shape");

  const envelope = fixture("native_schema1_envelope.json");
  envelope.extra = {};
  assert.equal(parseObject(envelope).code, "unsupported-envelope");

  const malformedEnvelope = fixture("native_schema1_envelope.json");
  malformedEnvelope.issues = {};
  assert.equal(
    parseObject(malformedEnvelope).code,
    "unsupported-envelope",
  );

  const contradictoryEnvelope = fixture("native_schema1_envelope.json");
  contradictoryEnvelope.home_assistant.version = "2026.6.0";
  assert.equal(
    parseObject(contradictoryEnvelope).code,
    "contradictory-envelope",
  );

  const contradictory = fixture("native_schema1.json");
  contradictory.integration.runtime_control_changed_by_diagnostics = true;
  assert.equal(
    parseObject(contradictory).code,
    "unsupported-native-contract",
  );

  const inconsistentLane = fixture("native_schema1.json");
  inconsistentLane.runtime.current_state.runtime_mode = "normal";
  assert.equal(
    parseObject(inconsistentLane).code,
    "unsupported-native-shape",
  );

  const malformedControlSwitch = fixture("native_schema1.json");
  malformedControlSwitch.runtime.gate_states.control_switches.control = {
    entity_present: true,
    is_on: "yes",
  };
  assert.equal(
    parseObject(malformedControlSwitch).code,
    "unsupported-native-shape",
  );

  const malformedPauseTimer = fixture("native_schema1.json");
  malformedPauseTimer.runtime.gate_states.pause_timers.pause = {
    entity_present: true,
    state: { unexpected: true },
  };
  assert.equal(
    parseObject(malformedPauseTimer).code,
    "unsupported-native-shape",
  );

  const mixed = fixture("native_schema1.json");
  mixed.data = fixture("native_schema1.json");
  assert.equal(parseObject(mixed).code, "unsupported-envelope");
});

test("dump adapter requires one exact, internally consistent summary", () => {
  const dump = fixture("dump_summary.json");
  const entryId = Object.keys(dump)[0];

  const expanded = structuredClone(dump);
  expanded[entryId].raw_diagnostics = {};
  assert.equal(parseObject(expanded).code, "unsupported-dump-shape");

  const inconsistent = structuredClone(dump);
  inconsistent[entryId].state_summary.count += 1;
  assert.equal(parseObject(inconsistent).code, "unsupported-dump-shape");

  const multiple = structuredClone(dump);
  multiple.abcdefabcdefabcdefabcdefabcdefab = structuredClone(dump[entryId]);
  assert.equal(parseObject(multiple).code, "unsupported-dump-shape");

  const named = { entry123: dump[entryId] };
  assert.equal(parseObject(named).code, "unsupported-dump-shape");
});

test("canonical layout and version allowlists suppress unfamiliar strings", () => {
  const payload = fixture("native_schema1.json");
  payload.integration.integration_version = "private custom build";
  payload.integration.home_assistant_version = "future";
  payload.generated_ui.cached_layouts.push(
    "private_layout",
    "v1_mobile",
    "view_cards_button",
  );
  const result = parseObject(payload);

  assert.equal(result.ok, true);
  assert.equal(result.report.integration.integrationVersion, "Not reported");
  assert.equal(result.report.integration.homeAssistantVersion, "Not reported");
  assert.deepEqual(result.report.generatedUi.cachedLayouts, [
    "v1_mobile",
    "v2_mobile",
    "v2_tablet",
    "view_cards_button",
  ]);
  assert.doesNotMatch(JSON.stringify(result.report), /private_layout/);
});

test("byte and iterative traversal limits reject resource-exhausting input", () => {
  assert.equal(
    parseDiagnosticsText("{}", LIMITS.maxBytes + 1).code,
    "file-too-large",
  );
  assert.equal(
    parseDiagnosticsText("x".repeat(LIMITS.maxBytes + 1), 0).code,
    "file-too-large",
  );

  let deep = "value";
  for (let index = 0; index <= LIMITS.maxDepth; index += 1) {
    deep = { child: deep };
  }
  assert.equal(parseObject(deep).code, "resource-limit");

  const wideArray = Array.from(
    { length: LIMITS.maxArrayLength + 1 },
    () => null,
  );
  assert.equal(parseObject({ values: wideArray }).code, "resource-limit");

  const longString = "x".repeat(LIMITS.maxStringLength + 1);
  assert.equal(parseObject({ value: longString }).code, "resource-limit");

  const manyKeys = {};
  for (let index = 0; index <= LIMITS.maxKeys; index += 1) {
    manyKeys[`key_${index}`] = null;
  }
  assert.equal(parseObject(manyKeys).code, "resource-limit");
});

test("unsafe integer counts fail closed", () => {
  const native = fixture("native_schema1.json");
  native.configuration.summary.telemetry_count =
    Number.MAX_SAFE_INTEGER + 1;
  assert.equal(parseObject(native).code, "unsupported-native-shape");

  const dump = fixture("dump_summary.json");
  const entryId = Object.keys(dump)[0];
  dump[entryId].entity_map_summary.mapped_entity_count =
    Number.MAX_SAFE_INTEGER + 1;
  dump[entryId].state_summary.count = Number.MAX_SAFE_INTEGER + 1;
  assert.equal(parseObject(dump).code, "unsupported-dump-shape");
});

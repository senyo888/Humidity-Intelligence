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
  settleRevisionBoundEffect,
} from "../site/inspector/inspection-session.mjs";
import {
  createSupportHandoff,
  HANDOFF_CONTRACT,
  HANDOFF_END,
  INSPECTOR_VERSION,
  MAX_HANDOFF_LENGTH,
  MAX_HANDOFF_LINE_LENGTH,
  PRIVACY_CATEGORIES,
  PRIVACY_CATEGORY_CODES,
  WARNING_CATEGORIES,
  WARNING_CATEGORY_CODES,
} from "../site/inspector/handoff.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const FIXTURES = path.join(ROOT, "tests 2", "fixtures", "hi_inspector");
const INTEGRATION_VERSION_PATTERN =
  /^\d{1,3}\.\d{1,3}\.\d{1,3}(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?(?:\+[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?$/;

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

test("stale clipboard success cannot update a replacement result", async () => {
  let resolveWrite;
  const session = createInspectionSession();
  const copyToken = session.begin();
  const pending = settleRevisionBoundEffect(
    () =>
      new Promise((resolve) => {
        resolveWrite = resolve;
      }),
    session,
    copyToken,
  );

  session.begin();
  resolveWrite();

  assert.deepEqual(await pending, { status: "stale" });
});

test("stale clipboard failure cannot select a replacement handoff", async () => {
  let rejectWrite;
  const session = createInspectionSession();
  const copyToken = session.begin();
  const pending = settleRevisionBoundEffect(
    () =>
      new Promise((_resolve, reject) => {
        rejectWrite = reject;
      }),
    session,
    copyToken,
  );

  session.invalidate();
  rejectWrite(new Error("clipboard permission changed"));

  assert.deepEqual(await pending, { status: "stale" });
});

test("native report produces the exact bounded handoff contract", () => {
  const parsed = parseDiagnosticsText(fixtureText("native_schema1.json"));
  assert.equal(parsed.ok, true);
  const handoff = createSupportHandoff(parsed.report);
  assert.equal(handoff.ok, true);
  const lines = handoff.text.split("\n");

  assert.equal(lines.length, 16);
  assert.equal(lines[0], HANDOFF_CONTRACT);
  assert.equal(lines.at(-1), HANDOFF_END);
  assert.equal(
    lines[2],
    `Inspector version: ${INSPECTOR_VERSION}`,
  );
  assert.equal(
    lines[3],
    "Recognized input format: native-ha-diagnostics",
  );
  assert.equal(lines[4], "Backend diagnostics schema: 1");
  assert.equal(
    lines[10],
    "Configuration counts: zones=1; aq-lanes=0; humidifier-lanes=0; alert-rules=1",
  );
  assert.ok(handoff.text.length <= MAX_HANDOFF_LENGTH);
  assert.ok(lines.every((line) => line.length <= MAX_HANDOFF_LINE_LENGTH));
  assert.doesNotMatch(handoff.text, /telemetry/i);
  assert.doesNotMatch(handoff.text, /active lane|reason available/i);
});

test("dump handoff preserves source distinction and not-reported schema", () => {
  const parsed = parseDiagnosticsText(fixtureText("dump_summary.json"));
  assert.equal(parsed.ok, true);
  const handoff = createSupportHandoff(parsed.report);

  assert.equal(handoff.ok, true);
  assert.match(
    handoff.text,
    /^Recognized input format: dump-diagnostics-summary$/m,
  );
  assert.match(
    handoff.text,
    /^Backend diagnostics schema: not-reported$/m,
  );
  assert.match(
    handoff.text,
    /^Privacy finding categories: entity=4; token=1; private=1$/m,
  );
});

test("every allowlisted category fits the handoff line and block bounds", () => {
  const parsed = parseDiagnosticsText(fixtureText("native_schema1.json"));
  assert.equal(parsed.ok, true);
  const report = structuredClone(parsed.report);
  report.warnings.categories = WARNING_CATEGORIES.map((category) => ({
    category,
    count: 1_000_000,
  }));
  report.privacy.categories = PRIVACY_CATEGORIES.map((category) => ({
    category,
    count: 1_000_000,
  }));

  const handoff = createSupportHandoff(report);
  assert.equal(handoff.ok, true);
  const lines = handoff.text.split("\n");
  assert.ok(handoff.text.length <= MAX_HANDOFF_LENGTH);
  assert.ok(lines.every((line) => line.length <= MAX_HANDOFF_LINE_LENGTH));
  for (const [, code] of [
    ...WARNING_CATEGORY_CODES,
    ...PRIVACY_CATEGORY_CODES,
  ]) {
    assert.match(
      handoff.text,
      new RegExp(`(?:categories: |; )${code}=1000000(?:;|$)`, "m"),
    );
  }
});

test("handoff ignores arbitrary report strings and disallowed categories", () => {
  const parsed = parseDiagnosticsText(fixtureText("native_schema1.json"));
  assert.equal(parsed.ok, true);
  const report = structuredClone(parsed.report);
  const sentinels = [
    "private-file-name.json",
    "sensor.private_room",
    "https://private.example.invalid/path",
    "/Users/private/path",
    "raw warning body",
    "raw reason body",
    "Kitchen",
  ];
  report.source.label = sentinels[0];
  report.runtime.activeLane = sentinels[1];
  report.runtime.reasonBody = sentinels[5];
  report.arbitrary = sentinels;
  report.warnings.categories.push({
    category: sentinels[4],
    count: 1,
  });
  report.privacy.categories.push({
    category: sentinels[2],
    count: 1,
  });
  const handoff = createSupportHandoff(report);

  assert.equal(handoff.ok, true);
  for (const sentinel of sentinels) {
    assert.doesNotMatch(
      handoff.text,
      new RegExp(
        sentinel.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"),
        "i",
      ),
    );
  }
});

test("handoff fails closed for unknown source or native schema", () => {
  const parsed = parseDiagnosticsText(fixtureText("native_schema1.json"));
  assert.equal(parsed.ok, true);

  const unknownSource = structuredClone(parsed.report);
  unknownSource.source.kind = "future-source";
  assert.equal(createSupportHandoff(unknownSource).ok, false);

  const unknownSchema = structuredClone(parsed.report);
  unknownSchema.integration.schema = "2";
  assert.equal(createSupportHandoff(unknownSchema).ok, false);
});

test("native schema 1 exposes only allowlisted backend facts", () => {
  const text = fixtureText("native_schema1.json");
  const nativeFixture = JSON.parse(text);
  const result = parseDiagnosticsText(text, Buffer.byteLength(text));

  assert.equal(result.ok, true);
  assert.equal(result.report.source.kind, "native-ha-diagnostics");
  assert.match(
    nativeFixture.integration.integration_version,
    INTEGRATION_VERSION_PATTERN,
  );
  assert.equal(
    result.report.integration.integrationVersion,
    nativeFixture.integration.integration_version,
  );
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

test("legacy native mapped rows are aggregated without retaining mapping keys", () => {
  const payload = fixture("native_schema1.json");
  payload.runtime.mapped_runtime_entities = {
    "sensor.private_source": { configured: true, status: "available" },
    "fan.private_output": { configured: true, status: "unavailable" },
  };

  const parsed = parseDiagnosticsText(JSON.stringify(payload));
  assert.equal(parsed.ok, true);
  assert.deepEqual(parsed.report.runtime.mappedEntities, {
    total: 2,
    available: 1,
    missing: 0,
    unknown: 0,
    unavailable: 1,
    other: 0,
  });

  const reportText = JSON.stringify(parsed.report);
  const handoff = createSupportHandoff(parsed.report);
  assert.equal(handoff.ok, true);
  assert.doesNotMatch(reportText, /sensor\.private_source|fan\.private_output/);
  assert.doesNotMatch(handoff.text, /sensor\.private_source|fan\.private_output/);
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
  const secretSentinel = "FIXTURE_PLACEHOLDER_VALUE_1";
  const privateUrl = `https://private.example.invalid/path?token=${secretSentinel}`;
  payload.privacy.secret_like_field = secretSentinel;
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
  assert.doesNotMatch(rendered, /FIXTURE_PLACEHOLDER_VALUE_1/);
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

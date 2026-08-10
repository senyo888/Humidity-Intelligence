export const LIMITS = Object.freeze({
  maxBytes: 1024 * 1024,
  maxDepth: 24,
  maxNodes: 20000,
  maxKeys: 10000,
  maxArrayLength: 2000,
  maxStringLength: 8192,
  maxKeyLength: 256,
});

const REQUIRED_NATIVE_SECTIONS = Object.freeze([
  "integration",
  "configuration",
  "runtime",
  "generated_ui",
  "diagnostics_summary",
  "privacy",
]);
const OPTIONAL_NATIVE_SECTIONS = new Set(["config_entry", "frontend"]);
const NATIVE_ROOT_KEYS = new Set([
  ...REQUIRED_NATIVE_SECTIONS,
  ...OPTIONAL_NATIVE_SECTIONS,
]);
const ENVELOPE_KEYS = new Set([
  "home_assistant",
  "custom_components",
  "integration_manifest",
  "setup_times",
  "issues",
  "data",
]);
const REQUIRED_DUMP_SECTIONS = Object.freeze([
  "cards",
  "configuration_summary",
  "diagnostics_summary",
  "entity_map_summary",
  "state_summary",
]);
const STATUS_BUCKETS = Object.freeze([
  "available",
  "missing",
  "unknown",
  "unavailable",
]);
const UNAVAILABLE_BUCKETS = Object.freeze([
  "missing",
  "unknown",
  "unavailable",
]);
const CANONICAL_LAYOUTS = new Set([
  "v1_mobile",
  "v2_mobile",
  "v2_tablet",
  "view_cards_button",
]);
const CANONICAL_RUNTIME_MODES = new Set([
  "air_quality",
  "alert",
  "bathroom",
  "co_emergency",
  "cooking",
  "global_gate",
  "normal",
  "telemetry_unavailable",
  "zone",
]);
const FEATURE_LABELS = Object.freeze({
  telemetry: "Telemetry",
  zone_control: "Zone control",
  air_quality: "Air quality",
  humidifiers: "Humidifiers",
  alert_handling: "Alert handling",
  visual_alerts: "Visual alerts",
  temperature_slope: "Temperature slope",
  generated_ui: "Generated UI",
  alert_only_mode: "Alert-only mode",
});
const SUMMARY_LABELS = Object.freeze({
  telemetry_count: "Telemetry sources",
  zone_count: "Enabled zones",
  aq_lane_count: "Air-quality lanes",
  humidifier_lane_count: "Humidifier lanes",
  alert_rule_count: "Alert rules",
  alert_only_mode: "Alert-only mode",
});
const INTEGRATION_FIELDS = new Set([
  "domain",
  "integration_version",
  "home_assistant_version",
  "diagnostics_schema",
  "native_home_assistant_diagnostics",
  "runtime_control_changed_by_diagnostics",
]);
const INTEGRATION_VERSION_PATTERN =
  /^\d{1,3}\.\d{1,3}\.\d{1,3}(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?(?:\+[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?$/;
const HOME_ASSISTANT_VERSION_PATTERN =
  /^\d{4}\.(?:[1-9]|1[0-2])\.\d{1,3}(?:(?:b|dev|rc)\d+)?$/i;
const SECRET_KEY_PATTERN =
  /(?:^|_)(?:access_?token|address|api_?key|authorization|bearer|credential|credentials|device_?id|email(?:_address)?|entry_?id|full_?name|host|latitude|longitude|mac(?:_address)?|mobile_?(?:number|phone)|password|phone(?:_number)?|postal_?code|postcode|private_?key|secret|ssid|street|telephone|token|unique_?id|user_?name|username|webhook(?:_url)?)(?:$|_)/i;
const URL_PATTERN = /\b(?:https?|wss?|mqtt):\/\/[^\s"'<>]+/i;
const EMAIL_PATTERN = /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/i;
const IPV4_PATTERN =
  /\b(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}\b/;
const MAC_PATTERN = /\b(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}\b/i;
const BEARER_PATTERN = /\bbearer\s+[a-z0-9._~+/=-]{8,}\b/i;
const LOCAL_PATH_PATTERN =
  /(?:^|[\s"'(])(?:\/(?:Users|home|var|config|mnt|srv)\/|[A-Za-z]:\\Users\\)/;
const ENTITY_ID_PATTERN =
  /(?:^|[^a-z0-9_-])[a-z_][a-z0-9_]{1,31}\.[a-z_][a-z0-9_]{2,127}(?=$|[^a-z0-9_-])/i;

export function parseDiagnosticsText(text, suppliedByteLength) {
  if (typeof text !== "string") {
    return failure(
      "invalid-input",
      "The selected input could not be read as text. No result was created.",
    );
  }

  const actualByteLength = byteLengthOf(text);
  const byteLength =
    suppliedByteLength === undefined
      ? actualByteLength
      : Math.max(actualByteLength, suppliedByteLength);
  if (
    !Number.isInteger(byteLength) ||
    byteLength < 0 ||
    byteLength > LIMITS.maxBytes
  ) {
    return failure(
      "file-too-large",
      "The file exceeds the 1 MiB Inspector limit. No result was created.",
    );
  }

  let payload;
  try {
    payload = JSON.parse(text);
  } catch {
    return failure(
      "malformed-json",
      "The file is not valid JSON. No result was created.",
    );
  }

  if (!isRecord(payload)) {
    return failure(
      "wrong-root",
      "The JSON root must be an object. No result was created.",
    );
  }

  const inspection = inspectBoundedTree(payload);
  if (!inspection.ok) return inspection;

  const adapted = adaptPayload(payload);
  if (!adapted.ok) return adapted;

  const report =
    adapted.kind === "dump-diagnostics-summary"
      ? summarizeDump(adapted.payload, inspection.privacy)
      : summarizeNative(adapted.payload, inspection.privacy);
  report.source = {
    kind: adapted.kind,
    label: adapted.label,
  };
  return { ok: true, report };
}

function inspectBoundedTree(root) {
  const stack = [{ value: root, depth: 0, parentKey: "" }];
  const privacyCounts = new Map();
  let nodes = 0;
  let keys = 0;

  const addPrivacy = (category) => {
    privacyCounts.set(category, (privacyCounts.get(category) ?? 0) + 1);
  };

  while (stack.length > 0) {
    const current = stack.pop();
    nodes += 1;
    if (nodes > LIMITS.maxNodes) {
      return resourceFailure("node-count");
    }
    if (current.depth > LIMITS.maxDepth) {
      return resourceFailure("nesting-depth");
    }

    const value = current.value;
    if (Array.isArray(value)) {
      if (value.length > LIMITS.maxArrayLength) {
        return resourceFailure("array-length");
      }
      for (let index = value.length - 1; index >= 0; index -= 1) {
        stack.push({
          value: value[index],
          depth: current.depth + 1,
          parentKey: current.parentKey,
        });
      }
      continue;
    }

    if (isRecord(value)) {
      const entries = Object.entries(value);
      keys += entries.length;
      if (keys > LIMITS.maxKeys) {
        return resourceFailure("key-count");
      }
      for (let index = entries.length - 1; index >= 0; index -= 1) {
        const [key, child] = entries[index];
        if (key.length > LIMITS.maxKeyLength) {
          return resourceFailure("key-length");
        }
        if (looksLikeConfigEntryKey(key)) {
          addPrivacy("Private identifier");
        }
        if (SECRET_KEY_PATTERN.test(key) && !/_present$/i.test(key)) {
          addPrivacy(secretKeyCategory(key));
        }
        stack.push({
          value: child,
          depth: current.depth + 1,
          parentKey: key,
        });
      }
      continue;
    }

    if (typeof value !== "string") continue;
    if (value.length > LIMITS.maxStringLength) {
      return resourceFailure("string-length");
    }
    if (BEARER_PATTERN.test(value)) addPrivacy("Bearer credential");
    if (URL_PATTERN.test(value)) addPrivacy("URL");
    if (EMAIL_PATTERN.test(value)) addPrivacy("Email address");
    if (IPV4_PATTERN.test(value)) addPrivacy("IP address");
    if (MAC_PATTERN.test(value)) addPrivacy("MAC address");
    if (LOCAL_PATH_PATTERN.test(value)) addPrivacy("Local filesystem path");
    if (ENTITY_ID_PATTERN.test(value)) addPrivacy("Entity identifier");
    if (looksLikeOpaqueToken(value)) addPrivacy("Opaque token-like value");
    if (
      /^(?:latitude|longitude|coordinates?|location)$/i.test(current.parentKey) &&
      value.trim()
    ) {
      addPrivacy("Coordinates or location");
    }
  }

  const categories = [...privacyCounts.entries()]
    .map(([category, count]) => ({ category, count }))
    .sort((left, right) => left.category.localeCompare(right.category));
  return {
    ok: true,
    privacy: {
      total: categories.reduce((total, item) => total + item.count, 0),
      categories,
    },
  };
}

function adaptPayload(payload) {
  if ("integration_manifest" in payload || "data" in payload) {
    return adaptEnvelope(payload);
  }
  if ("integration" in payload) {
    const error = validateNativePayload(payload);
    if (error) return error;
    return {
      ok: true,
      kind: "native-ha-diagnostics",
      label: "Native HA schema 1",
      payload,
    };
  }
  return adaptDump(payload);
}

function adaptEnvelope(payload) {
  if (!hasOnlyKeys(payload, ENVELOPE_KEYS)) {
    return failure(
      "unsupported-envelope",
      "The Home Assistant diagnostics envelope contains unsupported sections.",
    );
  }
  if (
    !isRecord(payload.home_assistant) ||
    !isRecord(payload.custom_components) ||
    !isRecord(payload.integration_manifest) ||
    !isRecord(payload.setup_times) ||
    !Array.isArray(payload.issues)
  ) {
    return failure(
      "unsupported-envelope",
      "The Home Assistant diagnostics envelope is incomplete or malformed.",
    );
  }
  if (payload.integration_manifest.domain !== "humidity_intelligence") {
    return failure(
      "wrong-envelope-domain",
      "The Home Assistant diagnostics envelope is not for Humidity Intelligence.",
    );
  }
  if (!isRecord(payload.data)) {
    return failure(
      "missing-envelope-data",
      "The Home Assistant diagnostics envelope has no supported data object.",
    );
  }
  const error = validateNativePayload(payload.data);
  if (error) return error;
  const component = payload.custom_components.humidity_intelligence;
  if (!isRecord(component)) {
    return failure(
      "unsupported-envelope",
      "The Home Assistant diagnostics envelope has no Humidity Intelligence component record.",
    );
  }
  const nativeIntegration = payload.data.integration;
  const versionPairs = [
    [
      payload.home_assistant.version,
      nativeIntegration.home_assistant_version,
    ],
    [component.version, nativeIntegration.integration_version],
    [
      payload.integration_manifest.version,
      nativeIntegration.integration_version,
    ],
  ];
  if (
    versionPairs.some(
      ([envelopeVersion, nativeVersion]) =>
        envelopeVersion !== undefined &&
        envelopeVersion !== null &&
        envelopeVersion !== nativeVersion,
    )
  ) {
    return failure(
      "contradictory-envelope",
      "The Home Assistant diagnostics envelope reports contradictory versions.",
    );
  }
  return {
    ok: true,
    kind: "native-ha-diagnostics",
    label: "Native HA schema 1",
    payload: payload.data,
  };
}

function validateNativePayload(payload) {
  if (!hasOnlyKeys(payload, NATIVE_ROOT_KEYS)) {
    return failure(
      "unsupported-native-shape",
      "The native diagnostics payload contains unsupported sections.",
    );
  }
  const missingSection = REQUIRED_NATIVE_SECTIONS.find(
    (section) => !isRecord(payload[section]),
  );
  if (missingSection) {
    return failure(
      "missing-native-section",
      "The native diagnostics payload is incomplete.",
    );
  }

  const integration = payload.integration;
  if (
    !hasOnlyKeys(integration, INTEGRATION_FIELDS) ||
    integration.domain !== "humidity_intelligence"
  ) {
    return failure(
      "wrong-native-domain",
      "The native diagnostics payload is not for Humidity Intelligence.",
    );
  }
  if (integration.diagnostics_schema !== 1) {
    return failure(
      "unsupported-schema",
      "This Inspector supports native Humidity Intelligence diagnostics schema 1 only.",
    );
  }
  if (
    integration.native_home_assistant_diagnostics !== true ||
    integration.runtime_control_changed_by_diagnostics !== false
  ) {
    return failure(
      "unsupported-native-contract",
      "The native diagnostics safety contract is not supported.",
    );
  }

  if (!validateNativeSummaryShapes(payload)) {
    return failure(
      "unsupported-native-shape",
      "The native diagnostics summary is malformed or contradictory.",
    );
  }
  return null;
}

function validateNativeSummaryShapes(payload) {
  const configuration = payload.configuration;
  const summary = configuration.summary;
  const features = configuration.enabled_feature_areas;
  const runtime = payload.runtime;
  const currentState = runtime.current_state;
  const generatedUi = payload.generated_ui;
  const diagnosticsSummary = payload.diagnostics_summary;

  if (
    !isRecord(summary) ||
    ![
      "telemetry_count",
      "zone_count",
      "aq_lane_count",
      "humidifier_lane_count",
      "alert_rule_count",
    ].every((key) => isNonNegativeInteger(summary[key])) ||
    typeof summary.alert_only_mode !== "boolean" ||
    !isRecord(features) ||
    !Object.keys(FEATURE_LABELS).every(
      (key) => typeof features[key] === "boolean",
    ) ||
    !isRecord(currentState) ||
    typeof currentState.reason_available !== "boolean" ||
    typeof currentState.reason_truncated !== "boolean" ||
    !isNullableString(runtime.active_lane) ||
    !isNullableString(currentState.runtime_mode) ||
    runtime.active_lane !== currentState.runtime_mode ||
    !isRecord(runtime.gate_states) ||
    !isRecord(runtime.output_states) ||
    !isValidMappedRuntimeEntities(runtime.mapped_runtime_entities) ||
    !isValidStatusSummary(
      runtime.unavailable_or_unknown_entities,
      UNAVAILABLE_BUCKETS,
    ) ||
    !Array.isArray(diagnosticsSummary.warnings) ||
    !diagnosticsSummary.warnings.every(
      (warning) => typeof warning === "string",
    ) ||
    !Array.isArray(generatedUi.configured_layouts) ||
    !generatedUi.configured_layouts.every(
      (layout) => typeof layout === "string",
    ) ||
    !Array.isArray(generatedUi.cached_layouts) ||
    !generatedUi.cached_layouts.every((layout) => typeof layout === "string") ||
    !isNonNegativeInteger(generatedUi.unresolved_placeholders_count) ||
    !isNonNegativeInteger(
      generatedUi.unresolved_placeholders_by_card_count,
    )
  ) {
    return false;
  }

  for (const outputName of [
    "fan_outputs",
    "humidifier_outputs",
    "visual_alert_outputs",
  ]) {
    if (!isValidStatusSummary(runtime.output_states[outputName], STATUS_BUCKETS)) {
      return false;
    }
  }

  const presenceGate = asRecord(runtime.gate_states.presence_gate);
  if (
    !isRecord(runtime.gate_states.time_gate) ||
    typeof runtime.gate_states.time_gate.enabled !== "boolean" ||
    typeof presenceGate.enabled !== "boolean" ||
    !isValidStatusSummary(presenceGate.entity_status, STATUS_BUCKETS) ||
    !isRecord(runtime.gate_states.control_switches) ||
    !isRecord(runtime.gate_states.pause_timers) ||
    !Object.values(runtime.gate_states.control_switches).every(
      (row) =>
        isRecord(row) &&
        typeof row.entity_present === "boolean" &&
        typeof row.is_on === "boolean",
    ) ||
    !Object.values(runtime.gate_states.pause_timers).every(
      (row) =>
        isRecord(row) &&
        typeof row.entity_present === "boolean" &&
        isBackendTimerState(row.state),
    )
  ) {
    return false;
  }

  return true;
}

function adaptDump(payload) {
  const entries = Object.entries(payload);
  if (
    entries.length !== 1 ||
    !looksLikeConfigEntryKey(entries[0][0]) ||
    !isRecord(entries[0][1])
  ) {
    return dumpFailure();
  }
  const dump = entries[0][1];
  if (
    !hasExactKeys(dump, REQUIRED_DUMP_SECTIONS) ||
    !Array.isArray(dump.cards) ||
    !dump.cards.every((card) => typeof card === "string") ||
    !isRecord(dump.configuration_summary) ||
    !isRecord(dump.diagnostics_summary) ||
    !isRecord(dump.entity_map_summary) ||
    !isRecord(dump.state_summary) ||
    !isValidDumpConfigurationSummary(dump.configuration_summary) ||
    !isValidDumpDiagnosticsSummary(dump.diagnostics_summary) ||
    !isValidDumpEntityMapSummary(dump.entity_map_summary) ||
    !isValidStatusSummary(dump.state_summary, STATUS_BUCKETS) ||
    dump.entity_map_summary.mapped_entity_count !== dump.state_summary.count
  ) {
    return dumpFailure();
  }
  return {
    ok: true,
    kind: "dump-diagnostics-summary",
    label: "HI dump_diagnostics summary",
    payload: dump,
  };
}

function isValidDumpConfigurationSummary(value) {
  return [
    "telemetry_count",
    "zone_count",
    "aq_lane_count",
    "humidifier_lane_count",
    "alert_rule_count",
  ].every((key) => isNonNegativeInteger(value[key]));
}

function isValidDumpDiagnosticsSummary(value) {
  return (
    Array.isArray(value.warnings) &&
    value.warnings.every((warning) => typeof warning === "string") &&
    isValidStatusSummary(
      value.unavailable_or_unknown_entities,
      UNAVAILABLE_BUCKETS,
    )
  );
}

function isValidDumpEntityMapSummary(value) {
  return (
    isNonNegativeInteger(value.mapped_entity_count) &&
    (value.mapped_keys === undefined ||
      (Array.isArray(value.mapped_keys) &&
        value.mapped_keys.every((key) => typeof key === "string")))
  );
}

function isValidStatusSummary(value, buckets) {
  if (
    !isRecord(value) ||
    !isNonNegativeInteger(value.count) ||
    !isRecord(value.by_status) ||
    Object.keys(value.by_status).length !== buckets.length ||
    Object.keys(value.by_status).some((bucket) => !buckets.includes(bucket)) ||
    !buckets.every((bucket) => isNonNegativeInteger(value.by_status[bucket]))
  ) {
    return false;
  }
  return (
    buckets.reduce((total, bucket) => total + value.by_status[bucket], 0) ===
    value.count
  );
}

function isValidMappedRuntimeEntities(value) {
  if (isValidStatusSummary(value, STATUS_BUCKETS)) return true;
  if (!isRecord(value)) return false;
  return Object.values(value).every(
    (row) =>
      isRecord(row) &&
      typeof row.configured === "boolean" &&
      STATUS_BUCKETS.includes(row.status),
  );
}

function summarizeNative(payload, privacy) {
  const integration = payload.integration;
  const configuration = payload.configuration;
  const runtime = payload.runtime;
  const currentState = runtime.current_state;
  const generatedUi = payload.generated_ui;
  const diagnosticsSummary = payload.diagnostics_summary;

  return {
    integration: {
      integrationVersion: safeVersion(
        integration.integration_version,
        INTEGRATION_VERSION_PATTERN,
      ),
      homeAssistantVersion: safeVersion(
        integration.home_assistant_version,
        HOME_ASSISTANT_VERSION_PATTERN,
      ),
      schema: "1",
    },
    configuration: {
      summary: summarizeConfiguration(configuration.summary),
      features: summarizeFeatures(configuration.enabled_feature_areas),
    },
    runtime: {
      activeLane: safeLane(runtime.active_lane),
      reasonAvailable: reportedBoolean(currentState.reason_available),
      reasonTruncated: reportedBoolean(currentState.reason_truncated),
      availability: statusSummary(
        runtime.unavailable_or_unknown_entities,
        UNAVAILABLE_BUCKETS,
      ),
      mappedEntities: mappedStatusSummary(runtime.mapped_runtime_entities),
      gates: summarizeGates(runtime.gate_states),
      outputs: summarizeOutputs(runtime.output_states),
    },
    generatedUi: {
      configuredLayouts: safeLayoutNames(generatedUi.configured_layouts),
      cachedLayouts: safeLayoutNames(generatedUi.cached_layouts),
      unresolvedPlaceholders: generatedUi.unresolved_placeholders_count,
      unresolvedCards: generatedUi.unresolved_placeholders_by_card_count,
    },
    warnings: categorizeWarnings(diagnosticsSummary.warnings),
    privacy,
  };
}

function summarizeDump(payload, privacy) {
  const diagnosticsSummary = payload.diagnostics_summary;
  const stateSummary = payload.state_summary;
  return {
    integration: {
      integrationVersion: "Not reported",
      homeAssistantVersion: "Not reported",
      schema: "Not reported",
    },
    configuration: {
      summary: summarizeConfiguration(payload.configuration_summary),
      features: summarizeFeatures({}),
    },
    runtime: {
      activeLane: "Not reported",
      reasonAvailable: "Not reported",
      reasonTruncated: "Not reported",
      availability: statusSummary(
        diagnosticsSummary.unavailable_or_unknown_entities,
        UNAVAILABLE_BUCKETS,
      ),
      mappedEntities: {
        total: payload.entity_map_summary.mapped_entity_count,
        available: stateSummary.by_status.available,
        missing: stateSummary.by_status.missing,
        unknown: stateSummary.by_status.unknown,
        unavailable: stateSummary.by_status.unavailable,
        other: "Not reported",
      },
      gates: notReportedGates(),
      outputs: notReportedOutputs(),
    },
    generatedUi: {
      configuredLayouts: null,
      cachedLayouts: safeLayoutNames(payload.cards),
      unresolvedPlaceholders: "Not reported",
      unresolvedCards: "Not reported",
    },
    warnings: categorizeWarnings(diagnosticsSummary.warnings),
    privacy,
  };
}

function summarizeConfiguration(summaryValue) {
  const summary = asRecord(summaryValue);
  return Object.entries(SUMMARY_LABELS).map(([key, label]) => ({
    key,
    label,
    value:
      typeof summary[key] === "boolean"
        ? summary[key]
          ? "Enabled"
          : "Disabled"
        : isNonNegativeInteger(summary[key])
          ? summary[key]
          : "Not reported",
  }));
}

function summarizeFeatures(featuresValue) {
  const features = asRecord(featuresValue);
  return Object.entries(FEATURE_LABELS).map(([key, label]) => ({
    key,
    label,
    value:
      typeof features[key] === "boolean" ? features[key] : "Not reported",
  }));
}

function summarizeGates(gatesValue) {
  const gates = asRecord(gatesValue);
  const controlSwitches = Object.values(
    asRecord(gates.control_switches),
  ).filter(isRecord);
  const pauseTimers = Object.values(asRecord(gates.pause_timers)).filter(
    isRecord,
  );
  return {
    timeGate: reportedBoolean(asRecord(gates.time_gate).enabled),
    presenceGate: reportedBoolean(asRecord(gates.presence_gate).enabled),
    controlSwitchCount: controlSwitches.length,
    controlSwitchesOn: controlSwitches.filter((row) => row.is_on === true).length,
    pauseTimerCount: pauseTimers.length,
  };
}

function notReportedGates() {
  return {
    timeGate: "Not reported",
    presenceGate: "Not reported",
    controlSwitchCount: "Not reported",
    controlSwitchesOn: "Not reported",
    pauseTimerCount: "Not reported",
  };
}

function summarizeOutputs(outputsValue) {
  const outputs = asRecord(outputsValue);
  return [
    ["Fan outputs", outputs.fan_outputs],
    ["Humidifier outputs", outputs.humidifier_outputs],
    ["Visual alert outputs", outputs.visual_alert_outputs],
  ].map(([label, value]) => ({
    label,
    ...statusSummary(value, STATUS_BUCKETS),
  }));
}

function notReportedOutputs() {
  return ["Fan outputs", "Humidifier outputs", "Visual alert outputs"].map(
    (label) => ({
      label,
      total: "Not reported",
      available: "Not reported",
      missing: "Not reported",
      unknown: "Not reported",
      unavailable: "Not reported",
    }),
  );
}

function mappedStatusSummary(value) {
  if (!isValidStatusSummary(value, STATUS_BUCKETS)) {
    const rows = Object.values(asRecord(value)).filter(isRecord);
    const counts = {
      available: 0,
      missing: 0,
      unknown: 0,
      unavailable: 0,
      other: 0,
    };
    for (const row of rows) {
      if (STATUS_BUCKETS.includes(row.status)) counts[row.status] += 1;
      else counts.other += 1;
    }
    return { total: rows.length, ...counts };
  }
  return {
    ...statusSummary(value, STATUS_BUCKETS),
    other: 0,
  };
}

function statusSummary(value, buckets) {
  const summary = asRecord(value);
  const byStatus = asRecord(summary.by_status);
  return {
    total: summary.count,
    available: buckets.includes("available")
      ? byStatus.available
      : "Not reported",
    missing: byStatus.missing,
    unknown: byStatus.unknown,
    unavailable: byStatus.unavailable,
  };
}

function categorizeWarnings(warnings) {
  const categories = new Map();
  for (const warning of warnings) {
    const text = warning.toLowerCase();
    let category = "Other backend warning";
    if (/missing|unknown|unavailable/.test(text)) {
      category = "Entity availability";
    } else if (/duplicate|mapping/.test(text)) {
      category = "Mapping";
    } else if (/telemetry|zone|configur/.test(text)) {
      category = "Configuration";
    } else if (/drift/.test(text)) {
      category = "Humidity drift";
    } else if (/setup|assist/.test(text)) {
      category = "Setup assistance";
    } else if (/normaliz/.test(text)) {
      category = "Entity normalization";
    } else if (/frontend|dependency/.test(text)) {
      category = "Optional dependency";
    }
    categories.set(category, (categories.get(category) ?? 0) + 1);
  }
  return {
    total: warnings.length,
    categories: [...categories.entries()]
      .map(([category, count]) => ({ category, count }))
      .sort((left, right) => left.category.localeCompare(right.category)),
  };
}

function safeLayoutNames(value) {
  if (!Array.isArray(value)) return null;
  return [
    ...new Set(value.filter((item) => CANONICAL_LAYOUTS.has(item))),
  ].sort();
}

function safeLane(value) {
  if (value === undefined || value === null || value === "") {
    return "Not reported";
  }
  return CANONICAL_RUNTIME_MODES.has(value)
    ? value
    : "Withheld (unrecognized value)";
}

function safeVersion(value, pattern) {
  return typeof value === "string" &&
    value.length <= 48 &&
    pattern.test(value)
    ? value
    : "Not reported";
}

function reportedBoolean(value) {
  if (value === true) return "Yes";
  if (value === false) return "No";
  return "Not reported";
}

function secretKeyCategory(key) {
  if (/latitude|longitude|location/i.test(key)) {
    return "Coordinates or location";
  }
  if (/mac/i.test(key)) return "MAC address field";
  if (/device_?id|entry_?id|unique_?id/i.test(key)) {
    return "Private identifier";
  }
  if (/host|ssid/i.test(key)) return "Network identifier";
  return "Secret-like field";
}

function looksLikeOpaqueToken(value) {
  const text = value.trim();
  if (text.length < 24 || text.length > 256 || /\s/.test(text)) return false;
  if (/^[a-f0-9]{32,}$/i.test(text)) return true;
  if (!/^[A-Za-z0-9_-]+={0,2}$/.test(text)) return false;
  const classes = [
    /[a-z]/.test(text),
    /[A-Z]/.test(text),
    /\d/.test(text),
    /[_-]/.test(text),
  ].filter(Boolean).length;
  return classes >= 3 && new Set(text).size >= 12;
}

function looksLikeConfigEntryKey(value) {
  return (
    /^[0-9a-f]{32}$/i.test(value) ||
    /^[0-9A-HJKMNP-TV-Z]{26}$/i.test(value)
  );
}

function hasOnlyKeys(value, allowed) {
  return isRecord(value) && Object.keys(value).every((key) => allowed.has(key));
}

function hasExactKeys(value, expected) {
  return (
    isRecord(value) &&
    Object.keys(value).length === expected.length &&
    expected.every((key) => key in value)
  );
}

function byteLengthOf(text) {
  return new TextEncoder().encode(text).byteLength;
}

function isNonNegativeInteger(value) {
  return Number.isSafeInteger(value) && value >= 0;
}

function isNullableString(value) {
  return value === null || typeof value === "string";
}

function isBackendTimerState(value) {
  return value === null || typeof value === "string";
}

function asRecord(value) {
  return isRecord(value) ? value : {};
}

function isRecord(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function resourceFailure(bound) {
  return failure(
    "resource-limit",
    `The file exceeds the Inspector ${bound} limit. No result was created.`,
  );
}

function dumpFailure() {
  return failure(
    "unsupported-dump-shape",
    "The file is not a supported single-entry HI dump_diagnostics summary.",
  );
}

function failure(code, message) {
  return { ok: false, code, message };
}

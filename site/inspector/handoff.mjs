export const HANDOFF_CONTRACT = "HI-SUPPORT-HANDOFF/1";
export const HANDOFF_END = "HI-SUPPORT-HANDOFF-END/1";
export const INSPECTOR_VERSION = "0.3.0-beta.1";
export const MAX_HANDOFF_LENGTH = 4096;

const MAX_COUNT = 1_000_000;
const SOURCE_FORMATS = new Set([
  "native-ha-diagnostics",
  "dump-diagnostics-summary",
]);
const CONFIGURATION_KEYS = Object.freeze([
  ["zone_count", "zones"],
  ["aq_lane_count", "aq-lanes"],
  ["humidifier_lane_count", "humidifier-lanes"],
  ["alert_rule_count", "alert-rules"],
]);
export const WARNING_CATEGORY_CODES = Object.freeze([
  ["Configuration", "cfg"],
  ["Entity availability", "ent-avail"],
  ["Entity normalization", "ent-norm"],
  ["Humidity drift", "drift"],
  ["Mapping", "map"],
  ["Optional dependency", "opt-dep"],
  ["Other backend warning", "other"],
  ["Setup assistance", "setup"],
]);
export const PRIVACY_CATEGORY_CODES = Object.freeze([
  ["Bearer credential", "bearer"],
  ["Coordinates or location", "location"],
  ["Email address", "email"],
  ["Entity identifier", "entity"],
  ["IP address", "ip"],
  ["Local filesystem path", "path"],
  ["MAC address", "mac"],
  ["MAC address field", "mac-field"],
  ["Network identifier", "network"],
  ["Opaque token-like value", "token"],
  ["Private identifier", "private"],
  ["Secret-like field", "secret"],
  ["URL", "url"],
]);
export const WARNING_CATEGORIES = Object.freeze(
  WARNING_CATEGORY_CODES.map(([category]) => category),
);
export const PRIVACY_CATEGORIES = Object.freeze(
  PRIVACY_CATEGORY_CODES.map(([category]) => category),
);

export function createSupportHandoff(report) {
  if (!isRecord(report) || !isRecord(report.source)) {
    return unavailable();
  }
  const source = report.source.kind;
  if (!SOURCE_FORMATS.has(source)) return unavailable();

  const schema =
    source === "native-ha-diagnostics"
      ? report.integration?.schema === "1"
        ? "1"
        : null
      : "not-reported";
  if (schema === null) return unavailable();

  const configuration = new Map(
    Array.isArray(report.configuration?.summary)
      ? report.configuration.summary
          .filter((row) => isRecord(row) && typeof row.key === "string")
          .map((row) => [row.key, row.value])
      : [],
  );
  const configurationCounts = CONFIGURATION_KEYS.map(
    ([key, label]) => `${label}=${formatCount(configuration.get(key))}`,
  ).join("; ");
  const availability = isRecord(report.runtime?.availability)
    ? report.runtime.availability
    : {};
  const mapped = isRecord(report.runtime?.mappedEntities)
    ? report.runtime.mappedEntities
    : {};

  const lines = [
    HANDOFF_CONTRACT,
    "Product: HI Support Bundle Inspector",
    `Inspector version: ${INSPECTOR_VERSION}`,
    `Recognized input format: ${source}`,
    `Backend diagnostics schema: ${schema}`,
    "Evidence class: user-supplied unsigned snapshot; advisory only; not live",
    "Diagnostic attachment: no",
    "Anonymity or correctness proof: no",
    "Home Assistant and HI runtime change: none",
    "Interpretation: does not diagnose HI, authenticate the source, infer a reason, or recommend a lane",
    `Configuration counts: ${configurationCounts}`,
    `Unavailable or unknown counts: total=${formatCount(availability.total)}; missing=${formatCount(availability.missing)}; unknown=${formatCount(availability.unknown)}; unavailable=${formatCount(availability.unavailable)}`,
    `Mapped entity status counts: total=${formatCount(mapped.total)}; available=${formatCount(mapped.available)}; missing=${formatCount(mapped.missing)}; unknown=${formatCount(mapped.unknown)}; unavailable=${formatCount(mapped.unavailable)}`,
    `Backend warning categories: ${formatCategories(report.warnings?.categories, WARNING_CATEGORY_CODES)}`,
    `Privacy finding categories: ${formatCategories(report.privacy?.categories, PRIVACY_CATEGORY_CODES)}`,
    HANDOFF_END,
  ];
  const text = lines.join("\n");
  if (
    text.length > MAX_HANDOFF_LENGTH ||
    lines.some((line) => line.length > 240)
  ) {
    return unavailable();
  }
  return { ok: true, text };
}

function formatCount(value) {
  return Number.isSafeInteger(value) && value >= 0 && value <= MAX_COUNT
    ? String(value)
    : "not-reported";
}

function formatCategories(value, categoryCodes) {
  const rows = Array.isArray(value) ? value : [];
  const byCategory = new Map(
    rows
      .filter(
        (row) =>
          isRecord(row) &&
          typeof row.category === "string" &&
          Number.isSafeInteger(row.count) &&
          row.count > 0 &&
          row.count <= MAX_COUNT,
      )
      .map((row) => [row.category, row.count]),
  );
  const categories = categoryCodes
    .filter(([category]) => byCategory.has(category))
    .map(([category, code]) => `${code}=${byCategory.get(category)}`);
  return categories.length > 0 ? categories.join("; ") : "none";
}

function unavailable() {
  return {
    ok: false,
    error:
      "The allowlisted support handoff could not be created from this result.",
  };
}

function isRecord(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

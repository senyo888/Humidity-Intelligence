import { LIMITS, parseDiagnosticsText } from "./parser.mjs";
import {
  createInspectionSession,
  readTextForInspection,
  settleRevisionBoundEffect,
} from "./inspection-session.mjs";
import { createSupportHandoff } from "./handoff.mjs";

const inspectionSession = createInspectionSession();
let currentHandoffText = "";
let currentHandoffToken = null;
const fileInput = document.querySelector("#diagnostics-file");
const dropZone = document.querySelector("#drop-zone");
const clearButton = document.querySelector("#clear-button");
const emptyState = document.querySelector("#empty-state");
const readingState = document.querySelector("#reading-state");
const errorState = document.querySelector("#error-state");
const errorMessage = document.querySelector("#error-message");
const results = document.querySelector("#results");
const handoffText = document.querySelector("#handoff-text");
const copyHandoffButton = document.querySelector("#copy-handoff");
const copyStatus = document.querySelector("#copy-status");

const byId = (id) => document.getElementById(id);
const showOnly = (visible) => {
  for (const section of [emptyState, readingState, errorState, results]) {
    section.hidden = section !== visible;
  }
};

const setText = (id, value) => {
  byId(id).textContent = String(value ?? "Not reported");
};

const clearChildren = (element) => {
  while (element.firstChild) element.removeChild(element.firstChild);
};

const renderCategories = (id, categories, emptyText) => {
  const list = byId(id);
  clearChildren(list);
  if (categories.length === 0) {
    const item = document.createElement("li");
    item.textContent = emptyText;
    list.appendChild(item);
    return;
  }
  for (const row of categories) {
    const item = document.createElement("li");
    item.textContent = `${row.category}: ${row.count}`;
    list.appendChild(item);
  }
};

const renderLayouts = (id, layouts) => {
  const list = byId(id);
  clearChildren(list);
  const values =
    layouts === null
      ? ["Not reported"]
      : layouts.length === 0
        ? ["None reported"]
        : layouts;
  for (const value of values) {
    const item = document.createElement("li");
    item.textContent = value;
    list.appendChild(item);
  }
};

const renderConfiguration = (configuration) => {
  const metrics = byId("configuration-metrics");
  clearChildren(metrics);
  for (const row of configuration.summary) {
    const wrapper = document.createElement("div");
    const term = document.createElement("dt");
    const value = document.createElement("dd");
    term.textContent = row.label;
    value.textContent = String(row.value);
    wrapper.append(term, value);
    metrics.appendChild(wrapper);
  }

  const features = byId("configuration-features");
  clearChildren(features);
  for (const row of configuration.features) {
    const item = document.createElement("li");
    const reported =
      row.value === "Not reported"
        ? "Not reported"
        : row.value
          ? "Enabled"
          : "Disabled";
    item.textContent = `${row.label}: ${reported}`;
    if (row.value === true) item.classList.add("is-on");
    features.appendChild(item);
  }
};

const renderAvailability = (runtime) => {
  const body = byId("availability-rows");
  clearChildren(body);
  const rows = [
    ["Unavailable or unknown", runtime.availability],
    ["Mapped entities", runtime.mappedEntities],
    ...runtime.outputs.map((output) => [output.label, output]),
  ];
  for (const [label, values] of rows) {
    const row = document.createElement("tr");
    const heading = document.createElement("th");
    heading.scope = "row";
    heading.textContent = label;
    row.appendChild(heading);
    for (const key of [
      "total",
      "available",
      "missing",
      "unknown",
      "unavailable",
    ]) {
      const cell = document.createElement("td");
      cell.textContent = String(values[key] ?? "Not reported");
      row.appendChild(cell);
    }
    body.appendChild(row);
  }
};

const resetRenderedReport = () => {
  currentHandoffText = "";
  currentHandoffToken = null;
  handoffText.value = "";
  copyHandoffButton.disabled = true;
  copyStatus.textContent = "";
  for (const id of [
    "source-badge",
    "source-summary",
    "privacy-summary",
    "privacy-mark",
    "active-lane",
    "reason-available",
    "reason-truncated",
    "integration-version",
    "ha-version",
    "schema-version",
    "time-gate",
    "presence-gate",
    "control-switches",
    "pause-timers",
    "unresolved-placeholders",
    "unresolved-cards",
    "warning-summary",
    "sharing-guidance",
  ]) {
    setText(id, "Not reported");
  }
  for (const id of [
    "privacy-categories",
    "configuration-metrics",
    "configuration-features",
    "availability-rows",
    "configured-layouts",
    "cached-layouts",
    "warning-categories",
  ]) {
    clearChildren(byId(id));
  }
  document.querySelector(".privacy-result").classList.remove("has-risk");
};

const renderReport = (report) => {
  setText("source-badge", report.source.label);
  setText(
    "source-summary",
    `Recognized ${report.source.label}; only allowlisted support facts are shown.`,
  );

  const privacyResult = document.querySelector(".privacy-result");
  const hasPrivacyRisk = report.privacy.total > 0;
  privacyResult.classList.toggle("has-risk", hasPrivacyRisk);
  setText("privacy-mark", hasPrivacyRisk ? "!" : "✓");
  setText(
    "privacy-summary",
    hasPrivacyRisk
      ? `${report.privacy.total} common risky pattern${report.privacy.total === 1 ? "" : "s"} detected. Review the original locally; matching values stay excluded from the Inspector result.`
      : "Common risky patterns detected: 0. Anonymity assessment remains with the user.",
  );
  renderCategories(
    "privacy-categories",
    report.privacy.categories,
    "No common risky pattern detected",
  );

  setText("active-lane", report.runtime.activeLane);
  setText("reason-available", report.runtime.reasonAvailable);
  setText("reason-truncated", report.runtime.reasonTruncated);
  setText("integration-version", report.integration.integrationVersion);
  setText("ha-version", report.integration.homeAssistantVersion);
  setText("schema-version", report.integration.schema);
  renderConfiguration(report.configuration);
  renderAvailability(report.runtime);

  const gates = report.runtime.gates;
  setText("time-gate", gates.timeGate);
  setText("presence-gate", gates.presenceGate);
  setText(
    "control-switches",
    Number.isSafeInteger(gates.controlSwitchCount) &&
      Number.isSafeInteger(gates.controlSwitchesOn)
      ? `${gates.controlSwitchesOn}/${gates.controlSwitchCount} on`
      : "Not reported",
  );
  setText(
    "pause-timers",
    Number.isSafeInteger(gates.pauseTimerCount)
      ? gates.pauseTimerCount
      : "Not reported",
  );

  renderLayouts(
    "configured-layouts",
    report.generatedUi.configuredLayouts,
  );
  renderLayouts("cached-layouts", report.generatedUi.cachedLayouts);
  setText(
    "unresolved-placeholders",
    report.generatedUi.unresolvedPlaceholders,
  );
  setText("unresolved-cards", report.generatedUi.unresolvedCards);

  setText(
    "warning-summary",
    report.warnings.total === 0
      ? "Backend warnings reported: 0."
      : `${report.warnings.total} backend warning${report.warnings.total === 1 ? "" : "s"} grouped with warning bodies excluded.`,
  );
  renderCategories(
    "warning-categories",
    report.warnings.categories,
    "No backend warning reported",
  );

  setText(
    "sharing-guidance",
    report.source.kind === "native-ha-diagnostics"
      ? "Native Home Assistant diagnostics are the preferred support attachment. Review the original file yourself and attach it only when you are comfortable; correctness and anonymity remain separate user assessments."
      : "Keep the original dump_diagnostics export local unless a maintainer explicitly asks for it. Support attachment, live evidence, correctness and anonymity remain separate from this unsigned result.",
  );
};

const showError = (message) => {
  errorMessage.textContent = message;
  clearButton.disabled = false;
  showOnly(errorState);
  errorState.focus();
};

const inspectFile = async (file) => {
  const inspectionToken = inspectionSession.begin();
  if (!(file instanceof File)) {
    if (inspectionSession.isCurrent(inspectionToken)) {
      showError("No readable file was selected. No result was created.");
    }
    return;
  }
  clearButton.disabled = false;
  resetRenderedReport();
  showOnly(readingState);

  if (file.size > LIMITS.maxBytes) {
    if (inspectionSession.isCurrent(inspectionToken)) {
      showError(
        "The file exceeds the 1 MiB Inspector limit. No result was created.",
      );
    }
    return;
  }

  const readResult = await readTextForInspection(
    file,
    inspectionSession,
    inspectionToken,
  );
  if (!inspectionSession.isCurrent(inspectionToken)) return;
  if (readResult.status === "error") {
    if (!inspectionSession.isCurrent(inspectionToken)) return;
    showError(
      "The selected file could not be read locally. No result was created.",
    );
    return;
  }
  if (readResult.status !== "ready") return;

  let text = readResult.text;
  const parsed = parseDiagnosticsText(text, file.size);
  text = "";
  if (!inspectionSession.isCurrent(inspectionToken)) return;
  if (!parsed.ok) {
    if (!inspectionSession.isCurrent(inspectionToken)) return;
    showError(parsed.message);
    return;
  }

  const handoff = createSupportHandoff(parsed.report);
  if (!inspectionSession.isCurrent(inspectionToken)) return;
  if (handoff.ok) {
    currentHandoffText = handoff.text;
    currentHandoffToken = inspectionToken;
    handoffText.value = currentHandoffText;
    copyHandoffButton.disabled = false;
  } else {
    copyStatus.textContent =
      "The optional support handoff is unavailable for this result. The Inspector result remains valid.";
  }
  renderReport(parsed.report);
  showOnly(results);
  results.focus();
};

const clearResult = () => {
  inspectionSession.invalidate();
  fileInput.value = "";
  clearButton.disabled = true;
  dropZone.classList.remove("is-dragging");
  resetRenderedReport();
  showOnly(emptyState);
  dropZone.focus();
};

const selectHandoffForManualCopy = (copyText, copyToken) => {
  if (
    !inspectionSession.isCurrent(copyToken) ||
    currentHandoffToken !== copyToken ||
    currentHandoffText !== copyText
  ) {
    return;
  }
  handoffText.focus();
  handoffText.select();
  handoffText.setSelectionRange(0, copyText.length);
  copyStatus.textContent =
    "Clipboard copy is unavailable. The handoff is selected; press Ctrl+C or Cmd+C.";
};

const copyHandoff = async () => {
  const copyText = currentHandoffText;
  const copyToken = currentHandoffToken;
  if (!copyText || !copyToken || copyHandoffButton.disabled) return;
  const clipboard = navigator.clipboard;
  if (!clipboard || typeof clipboard.writeText !== "function") {
    selectHandoffForManualCopy(copyText, copyToken);
    return;
  }
  const result = await settleRevisionBoundEffect(
    () => clipboard.writeText(copyText),
    inspectionSession,
    copyToken,
  );
  if (result.status === "success") {
    copyStatus.textContent =
      "Allowlisted handoff copied. Pasting it into GitHub creates normal GitHub retention.";
  } else if (result.status === "error") {
    selectHandoffForManualCopy(copyText, copyToken);
  }
};

fileInput.addEventListener("change", () => {
  const file = fileInput.files?.[0];
  if (file) void inspectFile(file);
});

dropZone.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    fileInput.click();
  }
});

for (const eventName of ["dragenter", "dragover"]) {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add("is-dragging");
  });
}

for (const eventName of ["dragleave", "drop"]) {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove("is-dragging");
  });
}

dropZone.addEventListener("drop", (event) => {
  const file = event.dataTransfer?.files?.[0];
  if (file) void inspectFile(file);
});

clearButton.addEventListener("click", clearResult);
copyHandoffButton.addEventListener("click", () => {
  void copyHandoff();
});

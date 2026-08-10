import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SURFACES = [
  'custom_components/humidity_intelligence/ui/cards/v2_mobile.yaml',
  'custom_components/humidity_intelligence/ui/cards/v2_tablet.yaml',
  'ui-gallery/default-v2-mobile-aq/card.yaml',
  'ui-gallery/default-v2-tablet-zone-1-cooking/card.yaml',
];

function gaugeBody(relativePath) {
  const source = fs.readFileSync(path.join(ROOT, relativePath), 'utf8');
  const cardStart = source.indexOf('          name: Stability Score\n');
  assert.notEqual(cardStart, -1, `${relativePath}: Stability Score card missing`);
  const gaugeStart = source.indexOf('            gauge: |\n', cardStart);
  const tapAction = source.indexOf('          tap_action:\n', gaugeStart);
  assert.notEqual(gaugeStart, -1, `${relativePath}: Stability gauge missing`);
  assert.notEqual(tapAction, -1, `${relativePath}: Stability gauge boundary missing`);

  const lines = source.slice(gaugeStart, tapAction).split('\n');
  const open = lines.indexOf('              [[[');
  const close = lines.lastIndexOf('              ]]]');
  assert.ok(open >= 0 && close > open, `${relativePath}: gauge wrapper missing`);
  return lines
    .slice(open + 1, close)
    .map((line) => (line.startsWith('                ') ? line.slice(16) : line))
    .join('\n');
}

const BODIES = SURFACES.map(gaugeBody);
const RENDERERS = BODIES.map((body) => new Function('entity', body));

function renderAll(attributes = {}) {
  return RENDERERS.map((render) => render({ state: 'ok', attributes }));
}

function assertIdentical(outputs) {
  assert.equal(new Set(outputs).size, 1, 'all four Stability surfaces must render identically');
  return outputs[0];
}

test('all four public surfaces carry one identical Stability renderer', () => {
  assert.equal(new Set(BODIES).size, 1);
});

test('absent v2.1 diagnostics render an intentional preview rather than a completed score', () => {
  const output = assertIdentical(renderAll({ diagnostics_summary: {} }));
  assert.match(output, /--hi-stability-color:#f8fafc/);
  assert.match(output, /hi-stability-gauge hi-stability-gauge-preview/);
  assert.match(output, /<span>2\.1<\/span><small>PREVIEW<\/small>/);
  assert.match(output, /aria-label="Stability Score preview for v2\.1\."/);
  assert.doesNotMatch(output, /hi-stability-gauge-white/);
  assert.doesNotMatch(output, />future</i);
});

test('explicit incomplete nested contracts degrade to no score rather than preview', () => {
  for (const stabilityScore of [{}, null, 'malformed', []]) {
    const output = assertIdentical(renderAll({
      diagnostics_summary: { stability_score: stabilityScore },
    }));
    assert.match(output, /--hi-stability-color:#94a3b8/);
    assert.match(output, /<span>—<\/span><small>NO SCORE<\/small>/);
    assert.match(output, /aria-label="Stability Score is not available\."/);
    assert.doesNotMatch(output, /hi-stability-gauge-preview/);
    assert.doesNotMatch(output, /<small>PREVIEW<\/small>/);
  }
});

test('backend score and classification still drive the live badge', () => {
  const output = assertIdentical(renderAll({
    diagnostics_summary: {
      stability_score: {
        score: { display_score: 82, display_classification: 'good' },
      },
    },
  }));
  assert.match(output, /--hi-stability-color:#4ade80/);
  assert.match(output, /<span>82<\/span><small>score<\/small>/);
  assert.match(output, /aria-label="Stability Score 82, good\."/);
  assert.doesNotMatch(output, /hi-stability-gauge-preview/);
  assert.doesNotMatch(output, /hi-stability-gauge-white/);
});

test('completed backend score alone receives completed white styling', () => {
  const output = assertIdentical(renderAll({
    diagnostics_summary: {
      stability_score: {
        score: { display_score: 99, display_classification: 'excellent' },
      },
    },
  }));
  assert.match(output, /--hi-stability-color:#f8fafc/);
  assert.match(output, /hi-stability-gauge hi-stability-gauge-white/);
  assert.doesNotMatch(output, /hi-stability-gauge-preview/);
  assert.match(output, /<span>99<\/span><small>score<\/small>/);
});

test('future collecting and unavailable states remain explicit without inventing a score', () => {
  const collecting = assertIdentical(renderAll({
    diagnostics_summary: {
      stability_score: {
        availability: 'insufficient_coverage',
        score: { suppression_reason: 'coverage_below_threshold' },
      },
    },
  }));
  assert.match(collecting, /--hi-stability-color:#38bdf8/);
  assert.match(collecting, /<span>—<\/span><small>COLLECTING<\/small>/);
  assert.doesNotMatch(collecting, /hi-stability-gauge-white/);

  const unavailable = assertIdentical(renderAll({
    diagnostics_summary: {
      stability_score: {
        availability: 'unavailable',
        score: { suppression_reason: 'current_telemetry_unavailable' },
      },
    },
  }));
  assert.match(unavailable, /--hi-stability-color:#94a3b8/);
  assert.match(unavailable, /<span>—<\/span><small>NO DATA<\/small>/);
  assert.doesNotMatch(unavailable, /hi-stability-gauge-white/);
});

test('flattened future states remain contract-backed collecting and unavailable truth', () => {
  const collecting = assertIdentical(renderAll({
    diagnostics_summary: {},
    stability_score_availability: 'insufficient_coverage',
    stability_score_suppression_reason: 'coverage_below_threshold',
  }));
  assert.match(collecting, /--hi-stability-color:#38bdf8/);
  assert.match(collecting, /<span>—<\/span><small>COLLECTING<\/small>/);
  assert.doesNotMatch(collecting, /<small>PREVIEW<\/small>/);

  const unavailable = assertIdentical(renderAll({
    diagnostics_summary: {},
    stability_score_availability: 'unavailable',
    stability_score_suppression_reason: 'current_telemetry_unavailable',
  }));
  assert.match(unavailable, /--hi-stability-color:#94a3b8/);
  assert.match(unavailable, /<span>—<\/span><small>NO DATA<\/small>/);
  assert.doesNotMatch(unavailable, /<small>PREVIEW<\/small>/);
});

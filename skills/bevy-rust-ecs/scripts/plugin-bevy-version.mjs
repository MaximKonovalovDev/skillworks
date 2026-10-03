#!/usr/bin/env node
// plugin-bevy-version.mjs: does a third-party Bevy plugin crate match our Bevy?
//
//   node plugin-bevy-version.mjs [--bevy 0.19.1] <owner/repo[:subdir]> [more ...]
//   node plugin-bevy-version.mjs [--bevy 0.19.1] --file <Cargo.toml> [--readme <README.md>]
//
// For each repo it reads Cargo.toml (through `gh api`, no token is printed) at the
// default branch AND at the latest release tag, prints the `bevy` requirement of
// each, whether it accepts our Bevy version, and the README rows of any
// compatibility table that mention our minor version. The release tag decides:
// the default branch usually already targets the next Bevy.
//
// `--file` / `--readme` read local files instead of the network (used by tests).
// Pure functions exported: readBevyRequirements, matchesBevy, readCompatTable.

import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { bevyDeps, parseManifest } from './check-sim-outside-bevy.mjs';

const DEFAULT_BEVY = '0.19.1';

// The engine crates of Bevy 0.19.1 (the directories of crates/ at the tag). Plugin crates often have
// bevy-named siblings (for example bevy-inspector-egui-derive); those are not Bevy and must not count.
const ENGINE_CRATES = new Set(
  `
  bevy_a11y bevy_android bevy_animation bevy_anti_alias bevy_app bevy_asset bevy_audio
  bevy_camera bevy_camera_controller bevy_clipboard bevy_color bevy_core_pipeline bevy_derive
  bevy_dev_tools bevy_diagnostic bevy_dylib bevy_ecs bevy_encase_derive bevy_feathers
  bevy_gilrs bevy_gizmos bevy_gizmos_render bevy_gltf bevy_image bevy_input bevy_input_focus
  bevy_internal bevy_light bevy_log bevy_macro_utils bevy_material bevy_math bevy_mesh bevy_pbr
  bevy_picking bevy_platform bevy_post_process bevy_ptr bevy_reflect bevy_remote bevy_render
  bevy_scene bevy_settings bevy_shader bevy_solari bevy_sprite bevy_sprite_render bevy_state
  bevy_tasks bevy_text bevy_time bevy_transform bevy_ui bevy_ui_render bevy_ui_widgets
  bevy_utils bevy_window bevy_winit bevy_world_serialization
  `
    .split(/\s+/)
    .filter(Boolean),
);
const isEngineCrate = (n) => n === 'bevy' || ENGINE_CRATES.has(String(n).replace(/-/g, '_'));


// ---------- pure functions ----------

// Every Bevy dependency of a Cargo.toml text:
// [{ name, package, req, label }] where req is the version requirement text,
// "git <url>" or "path <dir>".
export function readBevyRequirements(tomlText, wsDeps = new Map()) {
  return bevyDeps(tomlText, wsDeps).map((d) => ({
    name: d.name,
    package: d.package,
    label: d.label,
    req: d.version || (d.git ? `git ${d.git}` : d.path ? `path ${d.path}` : '(no version)'),
  }));
}

function parseVer(v) {
  const m = String(v).trim().match(/^(\d+|\*|x)(?:\.(\d+|\*|x))?(?:\.(\d+|\*|x))?(?:-([0-9A-Za-z.-]+))?(?:\+.*)?$/);
  if (!m) return null;
  const num = (s) => (s === undefined || s === '*' || s === 'x' ? null : Number(s));
  return { parts: [num(m[1]), num(m[2]), num(m[3])], pre: m[4] || null };
}

function cmp(a, b) {
  for (let i = 0; i < 3; i++) {
    const x = a[i] ?? 0;
    const y = b[i] ?? 0;
    if (x !== y) return x < y ? -1 : 1;
  }
  return 0;
}

function matchOne(op, ver, target) {
  const p = ver.parts;
  if (p[0] === null) return true; // `*`
  const full = [p[0] ?? 0, p[1] ?? 0, p[2] ?? 0];
  const given = p.filter((x) => x !== null).length;
  if (op === '=') return p.every((x, i) => x === null || x === target[i]);
  if (op === '>=') return cmp(target, full) >= 0;
  if (op === '>') return cmp(target, upper(p, given)) >= 0;
  if (op === '<=') return cmp(target, upper(p, given)) < 0;
  if (op === '<') return cmp(target, full) < 0;
  if (cmp(target, full) < 0) return false;
  if (op === '~') {
    // ~1.2.3 and ~1.2 stop before 1.3.0; ~1 stops before 2.0.0
    return cmp(target, given >= 2 ? [p[0], p[1] + 1, 0] : [p[0] + 1, 0, 0]) < 0;
  }
  // caret (the default): the left-most non-zero part may not change
  let up;
  if (p[0] > 0 || given === 1) up = [p[0] + 1, 0, 0];
  else if (p[1] > 0 || given === 2) up = [0, p[1] + 1, 0];
  else up = [0, 0, (p[2] ?? 0) + 1];
  return cmp(target, up) < 0;
}

// first version above everything that a partial version `p` covers
function upper(p, given) {
  if (given === 1) return [p[0] + 1, 0, 0];
  if (given === 2) return [p[0], p[1] + 1, 0];
  return [p[0], p[1], p[2] + 1];
}

// Does the Cargo version requirement `req` accept `version`?  true / false / null (cannot tell)
export function matchesBevy(req, version = DEFAULT_BEVY) {
  const t = parseVer(version);
  if (!t) return null;
  const target = t.parts.map((x) => x ?? 0);
  const text = String(req).trim();
  if (!text || text.startsWith('git ') || text.startsWith('path ') || text.startsWith('(')) return null;
  for (const raw of text.split(',')) {
    const m = raw.trim().match(/^(>=|<=|>|<|=|~|\^)?\s*(.+)$/);
    if (!m) return null;
    const ver = parseVer(m[2]);
    if (!ver) return null;
    const op = m[1] || '^';
    if (!matchOne(op === '^' ? '^' : op, ver, target)) return false;
  }
  return true;
}

// Markdown tables whose header row mentions "bevy". Returns [{ header, rows }] where
// header and rows are arrays of cell strings.
export function readCompatTable(readme) {
  const lines = String(readme).replace(/\r\n?/g, '\n').split('\n');
  const tables = [];
  for (let i = 0; i < lines.length - 1; i++) {
    const isRow = (s) => s.trim().startsWith('|') && s.trim().endsWith('|');
    if (!isRow(lines[i]) || !/^\s*\|[\s:|-]+\|\s*$/.test(lines[i + 1])) continue;
    const cells = (s) => s.trim().slice(1, -1).split('|').map((c) => c.trim());
    const header = cells(lines[i]);
    let j = i + 2;
    const rows = [];
    while (j < lines.length && isRow(lines[j])) rows.push(cells(lines[j++]));
    if (header.some((h) => /bevy/i.test(h))) tables.push({ header, rows });
    i = j - 1;
  }
  return tables;
}

// ---------- gh access ----------

function gh(args) {
  const r = spawnSync('gh', ['api', ...args], { encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 });
  if (r.error) return { ok: false, err: r.error.code === 'ENOENT' ? 'gh is not installed or not on PATH' : String(r.error.message) };
  if (r.status !== 0) return { ok: false, err: (r.stderr || '').split('\n')[0].trim() || `gh exited ${r.status}` };
  return { ok: true, out: r.stdout };
}

function rawFile(repo, file, ref) {
  const q = ref ? `?ref=${encodeURIComponent(ref)}` : '';
  return gh(['-H', 'Accept: application/vnd.github.raw', `repos/${repo}/contents/${file}${q}`]);
}

function latestTag(repo) {
  let r = gh([`repos/${repo}/releases/latest`, '--jq', '.tag_name']);
  if (r.ok && r.out.trim()) return { tag: r.out.trim(), from: 'release' };
  r = gh([`repos/${repo}/tags?per_page=1`, '--jq', '.[0].name']);
  if (r.ok && r.out.trim() && r.out.trim() !== 'null') return { tag: r.out.trim(), from: 'tag (no GitHub release)' };
  return null;
}

// ---------- report ----------

function describe(text, bevy, wsFallback) {
  const reqs = readBevyRequirements(text, wsFallback);
  if (!reqs.length) return { reqs, verdict: null };
  const real = reqs.filter((r) => isEngineCrate(r.package || r.name));
  const results = real.map((r) => matchesBevy(r.req, bevy));
  let verdict = 'OK';
  if (results.some((x) => x === false)) verdict = 'MISMATCH';
  else if (results.some((x) => x === null)) verdict = 'UNKNOWN';
  return { reqs: real, verdict };
}

function printReqs(label, d, bevy, out) {
  if (!d.reqs.length) {
    out.push(`${label}: no bevy dependency found in this Cargo.toml`);
    return;
  }
  out.push(`${label}: ${d.verdict} with bevy ${bevy}`);
  for (const r of d.reqs.slice(0, 8)) out.push(`    ${r.label} ${r.name}${r.package && r.package !== r.name ? ` (package ${r.package})` : ''} = ${r.req}`);
  if (d.reqs.length > 8) out.push(`    ... and ${d.reqs.length - 8} more`);
}

function printCompat(readme, bevy, out) {
  const minor = bevy.split('.').slice(0, 2).join('.');
  const tables = readCompatTable(readme);
  if (!tables.length) {
    out.push('README: no compatibility table with a "bevy" column found');
    return null;
  }
  let first = null;
  for (const t of tables.slice(0, 2)) {
    // the column that holds the Bevy version: a header that is just "bevy", else the first that mentions it
    let col = t.header.findIndex((h) => /^`?bevy`?$/i.test(h.trim()));
    if (col < 0) col = t.header.findIndex((h) => /bevy/i.test(h));
    const hit = t.rows.filter((row) => (row[col] || '').includes(minor));
    out.push(`README table [${t.header.join(' | ')}]: ${hit.length ? `${hit.length} row(s) mention ${minor}` : `no row mentions ${minor}`}`);
    for (const row of hit.slice(0, 5)) out.push(`    ${row.join(' | ')}`);
    if (hit.length && !first) first = hit[0].join(' | ');
  }
  return first;
}

function checkRepo(spec, bevy) {
  const [repo, sub] = spec.split(':');
  const dir = sub ? `${sub.replace(/\/$/, '')}/` : '';
  const out = [`== ${spec}`];
  const meta = gh([`repos/${repo}`, '--jq', '.default_branch']);
  if (!meta.ok) {
    out.push(`ERROR cannot read ${repo}: ${meta.err}`);
    return { text: out.join('\n'), code: 2 };
  }
  const branch = meta.out.trim();
  let code = 0;
  const main = rawFile(repo, `${dir}Cargo.toml`, branch);
  let mainD = null;
  if (main.ok) {
    mainD = describe(main.out, bevy);
    printReqs(`default branch ${branch}`, mainD, bevy, out);
    if (!mainD.reqs.length) {
      const m = parseManifest(main.out);
      if (m.members.length) out.push(`    workspace members: ${m.members.slice(0, 8).join(', ')}  (try owner/repo:<member dir>)`);
    }
  } else {
    out.push(`default branch ${branch}: cannot read ${dir}Cargo.toml (${main.err})`);
    code = 2;
  }
  const rel = latestTag(repo);
  let relD = null;
  if (rel) {
    const t = rawFile(repo, `${dir}Cargo.toml`, rel.tag);
    if (t.ok) {
      relD = describe(t.out, bevy);
      printReqs(`latest ${rel.from} ${rel.tag}`, relD, bevy, out);
    } else {
      out.push(`latest ${rel.from} ${rel.tag}: cannot read ${dir}Cargo.toml (${t.err})`);
    }
  } else {
    out.push('latest release: none found (no releases and no tags)');
  }
  const readme = gh(['-H', 'Accept: application/vnd.github.raw', `repos/${repo}/readme`]);
  const compat = readme.ok ? printCompat(readme.out, bevy, out) : null;
  // verdict: the release tag decides
  if (relD && relD.verdict === 'OK') out.push(`VERDICT: OK. Release ${rel.tag} accepts bevy ${bevy}. Pin the crate version that matches this tag (check crates.io).`);
  else if (relD && relD.verdict === 'MISMATCH') {
    out.push(`VERDICT: NO. Release ${rel.tag} does not accept bevy ${bevy}.${mainD && mainD.verdict === 'OK' ? ' Only the default branch matches (a git dependency: ask the owner first).' : ''}${compat ? ` The README lists [${compat}] for bevy ${bevy.split('.').slice(0, 2).join('.')}: confirm that release is on crates.io.` : ''}`);
  } else out.push('VERDICT: UNKNOWN. Read the crate README and Cargo.toml by hand.');
  return { text: out.join('\n'), code };
}

function main(argv) {
  let bevy = DEFAULT_BEVY;
  let file = null;
  let readme = null;
  const repos = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--bevy') bevy = argv[++i];
    else if (a === '--file') file = argv[++i];
    else if (a === '--readme') readme = argv[++i];
    else if (a === '-h' || a === '--help') { repos.length = 0; file = null; break; }
    else repos.push(a);
  }
  if (!file && repos.length === 0) {
    console.error('usage: node plugin-bevy-version.mjs [--bevy 0.19.1] <owner/repo[:subdir]> [...]\n       node plugin-bevy-version.mjs [--bevy 0.19.1] --file <Cargo.toml> [--readme <README.md>]');
    return 2;
  }
  if (file) {
    const out = [`== ${file}`];
    printReqs('Cargo.toml', describe(fs.readFileSync(file, 'utf8'), bevy), bevy, out);
    if (readme) printCompat(fs.readFileSync(readme, 'utf8'), bevy, out);
    console.log(out.join('\n'));
    return 0;
  }
  let code = 0;
  for (const spec of repos) {
    const r = checkRepo(spec, bevy);
    console.log(r.text);
    code = Math.max(code, r.code);
  }
  return code;
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(fileURLToPath(import.meta.url))) {
  process.exitCode = main(process.argv.slice(2));
}

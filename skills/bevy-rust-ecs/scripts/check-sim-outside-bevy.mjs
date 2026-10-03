#!/usr/bin/env node
// check-sim-outside-bevy.mjs: fail when a crate depends on Bevy.
//
//   node check-sim-outside-bevy.mjs <crate-dir | path/to/Cargo.toml> [more ...]
//
// Reads each Cargo.toml as text (no TOML library, no network). It looks at
// [dependencies], [dev-dependencies], [build-dependencies], their
// [target.<cfg>.*] forms, the dotted forms ([dependencies.bevy] and
// `bevy.version = ".."`), inline tables, `package = ".."` renames and
// `workspace = true` inheritance (the name is looked up in the nearest
// [workspace.dependencies]). A dependency counts as Bevy when its key or its
// real package name is `bevy`, or starts with `bevy_` or `bevy-`.
//
// A directory whose Cargo.toml has [workspace] members but no [package] is
// expanded to its members (`dir/*` and plain paths), so a workspace root
// cannot pass by accident.
//
// Exit codes: 0 no Bevy dependency anywhere; 1 at least one found; 2 usage
// error or an unreadable Cargo.toml (and nothing found).

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DEP_TABLES = new Set(['dependencies', 'dev-dependencies', 'build-dependencies', 'dev_dependencies', 'build_dependencies']);

export function isBevyName(name) {
  const n = String(name || '').toLowerCase();
  return n === 'bevy' || n.startsWith('bevy_') || n.startsWith('bevy-');
}

// Split the text into statements: one header or one `key = value`, with
// comments removed and multi-line arrays, inline tables and strings joined.
export function statements(text) {
  text = text.replace(/\r\n?/g, '\n');
  const out = [];
  let cur = '';
  let depth = 0;
  let line = 1;
  let start = 1;
  let mode = null; // null | '"' | "'" | '"""' | "'''"
  const n = text.length;
  const push = () => {
    if (cur.trim()) out.push({ text: cur.trim(), line: start });
    cur = '';
    depth = 0;
  };
  let i = 0;
  while (i < n) {
    const c = text[i];
    if (mode === null) {
      if (c === '#') {
        while (i < n && text[i] !== '\n') i++;
        continue;
      }
      if (text.startsWith('"""', i)) { mode = '"""'; cur += '"""'; i += 3; continue; }
      if (text.startsWith("'''", i)) { mode = "'''"; cur += "'''"; i += 3; continue; }
      if (c === '"' || c === "'") { mode = c; cur += c; i++; continue; }
      if (c === '[' || c === '{') depth++;
      else if (c === ']' || c === '}') depth--;
      if (c === '\n') {
        line++;
        i++;
        if (depth <= 0) { push(); start = line; } else cur += ' ';
        continue;
      }
      if (!cur.trim()) start = line;
      cur += c;
      i++;
      continue;
    }
    if (mode === '"' || mode === "'") {
      if (mode === '"' && c === '\\') { cur += c + (text[i + 1] ?? ''); i += 2; continue; }
      if (c === mode || c === '\n') mode = null;
      if (c === '\n') line++;
      cur += c;
      i++;
      continue;
    }
    if (mode === '"""' && c === '\\') { cur += c + (text[i + 1] ?? ''); i += 2; continue; }
    if (text.startsWith(mode, i)) { cur += mode; i += 3; mode = null; continue; }
    if (c === '\n') line++;
    cur += c;
    i++;
  }
  push();
  return out;
}

// "a.'b.c'.\"d\"" -> ["a", "b.c", "d"]
export function splitDotted(s) {
  const parts = [];
  let cur = '';
  let q = null;
  let had = false;
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (q) {
      if (c === q) q = null;
      else cur += c;
      continue;
    }
    if (c === '"' || c === "'") { q = c; had = true; continue; }
    if (c === '.') { parts.push(cur.trim()); cur = ''; had = false; continue; }
    cur += c;
  }
  if (cur.trim() || had || parts.length) parts.push(cur.trim());
  return parts;
}

// index of the first `=` that is outside quotes, or -1
function eqIndex(s) {
  let q = null;
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (q) { if (c === q) q = null; continue; }
    if (c === '"' || c === "'") { q = c; continue; }
    if (c === '=') return i;
  }
  return -1;
}

// Top-level `key = value` pairs of an inline table text like `{ a = 1, b = "x" }`.
export function parseInline(v) {
  v = v.trim();
  if (!v.startsWith('{')) return null;
  v = v.slice(1, v.lastIndexOf('}'));
  const pairs = [];
  let cur = '';
  let depth = 0;
  let q = null;
  for (const c of v) {
    if (q) { cur += c; if (c === q) q = null; continue; }
    if (c === '"' || c === "'") { q = c; cur += c; continue; }
    if (c === '[' || c === '{') depth++;
    if (c === ']' || c === '}') depth--;
    if (c === ',' && depth === 0) { pairs.push(cur); cur = ''; continue; }
    cur += c;
  }
  if (cur.trim()) pairs.push(cur);
  const out = {};
  for (const p of pairs) {
    const e = eqIndex(p);
    if (e < 0) continue;
    out[splitDotted(p.slice(0, e).trim()).join('.')] = p.slice(e + 1).trim();
  }
  return out;
}

const unquote = (v) => {
  v = String(v).trim();
  const m = v.match(/^("([^"]*)"|'([^']*)')$/);
  return m ? (m[2] ?? m[3]) : v;
};

function classify(full) {
  if (full[0] === 'workspace' && full[1] === 'dependencies') {
    return { kind: 'ws', label: '[workspace.dependencies]', name: full[2], rest: full.slice(3) };
  }
  let base = 0;
  if (full[0] === 'target') base = 2;
  if (full.length > base && DEP_TABLES.has(full[base])) {
    const label = base ? `[target.${full[1]}.${full[base]}]` : `[${full[base]}]`;
    return { kind: 'dep', label, name: full[base + 1], rest: full.slice(base + 2) };
  }
  return null;
}

// Returns { hasPackage, hasWorkspace, deps, wsDeps, members }.
export function parseManifest(text) {
  const deps = new Map();
  const wsDeps = new Map();
  let section = [];
  let hasPackage = false;
  let hasWorkspace = false;
  let members = [];
  const note = (info, rest, valueText, line) => {
    if (!info.name) return;
    const map = info.kind === 'ws' ? wsDeps : deps;
    const key = `${info.label}|${info.name}`;
    const d = map.get(key) || { label: info.label, name: info.name, package: null, workspace: false, version: null, git: null, path: null, line };
    map.set(key, d);
    if (valueText === undefined) return;
    if (rest.length === 0) {
      const inline = parseInline(valueText);
      if (inline) {
        if (inline.package) d.package = unquote(inline.package);
        if (inline.workspace === 'true') d.workspace = true;
        for (const f of ['version', 'git', 'path']) if (inline[f]) d[f] = unquote(inline[f]);
      } else {
        d.version = unquote(valueText); // `name = "0.19"`
      }
    } else if (rest[0] === 'package') {
      d.package = unquote(valueText);
    } else if (rest[0] === 'workspace') {
      d.workspace = unquote(valueText) === 'true';
    } else if (['version', 'git', 'path'].includes(rest[0])) {
      d[rest[0]] = unquote(valueText);
    }
  };
  for (const st of statements(text)) {
    const t = st.text;
    if (t.startsWith('[')) {
      const arr = t.startsWith('[[');
      const inner = t.slice(arr ? 2 : 1, t.lastIndexOf(']') - (arr ? 1 : 0));
      section = splitDotted(inner);
      if (!arr && section[0] === 'package' && section.length === 1) hasPackage = true;
      if (!arr && section[0] === 'workspace') hasWorkspace = true;
      const info = classify(section);
      if (info) note(info, info.rest, undefined, st.line);
      continue;
    }
    const e = eqIndex(t);
    if (e < 0) continue;
    const keyPath = splitDotted(t.slice(0, e).trim());
    const value = t.slice(e + 1).trim();
    const full = [...section, ...keyPath];
    if (full[0] === 'package' && full.length >= 2) hasPackage = true;
    if (full[0] === 'workspace') hasWorkspace = true;
    if (full.length === 2 && full[0] === 'workspace' && full[1] === 'members') {
      members = [...value.matchAll(/"([^"]*)"|'([^']*)'/g)].map((m) => m[1] ?? m[2]);
    }
    const info = classify(full);
    if (info) note(info, info.rest, value, st.line);
  }
  return { hasPackage, hasWorkspace, deps: [...deps.values()], wsDeps, members };
}

// Bevy dependencies found in one manifest text. `wsDeps` is the nearest
// [workspace.dependencies] map (key -> entry) used to resolve `workspace = true`.
export function bevyDeps(text, wsDeps = new Map()) {
  const m = parseManifest(text);
  const own = new Map([...m.wsDeps.values()].map((d) => [d.name, d]));
  const lookup = (name) => own.get(name) || [...wsDeps.values()].find((d) => d.name === name);
  const found = [];
  for (const d of m.deps) {
    const ws = d.workspace ? lookup(d.name) : null;
    const pkg = d.package || ws?.package || null;
    if (isBevyName(d.name) || isBevyName(pkg)) {
      found.push({
        label: d.label,
        name: d.name,
        package: pkg,
        version: d.version || ws?.version || null,
        git: d.git || ws?.git || null,
        path: d.path || ws?.path || null,
        line: d.line,
      });
    }
  }
  return found;
}

function readText(file) {
  try {
    return fs.readFileSync(file, 'utf8');
  } catch {
    return null;
  }
}

// nearest [workspace.dependencies] at or above `dir`
function workspaceDeps(dir) {
  let d = path.resolve(dir);
  for (;;) {
    const t = readText(path.join(d, 'Cargo.toml'));
    if (t !== null) {
      const m = parseManifest(t);
      if (m.hasWorkspace) return m.wsDeps;
    }
    const up = path.dirname(d);
    if (up === d) return new Map();
    d = up;
  }
}

function expandMembers(dir, members) {
  const out = [];
  for (const m of members) {
    if (m.endsWith('/*') || m.endsWith('\\*')) {
      const base = path.join(dir, m.slice(0, -2));
      let names = [];
      try { names = fs.readdirSync(base); } catch { /* missing dir: nothing to check */ }
      for (const n of names.sort()) {
        const p = path.join(base, n);
        if (fs.existsSync(path.join(p, 'Cargo.toml'))) out.push(p);
      }
    } else if (!m.includes('*')) {
      out.push(path.join(dir, m));
    }
  }
  return out;
}

// Returns { failed, errors, lines }.
export function checkTargets(targets, seen = new Set()) {
  const res = { failed: 0, errors: 0, lines: [] };
  for (const t of targets) {
    const file = t.toLowerCase().endsWith('cargo.toml') ? path.resolve(t) : path.join(path.resolve(t), 'Cargo.toml');
    if (seen.has(file)) continue;
    seen.add(file);
    const text = readText(file);
    if (text === null) {
      res.errors++;
      res.lines.push(`ERROR cannot read ${file}`);
      continue;
    }
    const dir = path.dirname(file);
    const m = parseManifest(text);
    if (!m.hasPackage && m.members.length) {
      res.lines.push(`NOTE ${file} is a workspace root without a package: checking its members`);
      const sub = checkTargets(expandMembers(dir, m.members), seen);
      res.failed += sub.failed;
      res.errors += sub.errors;
      res.lines.push(...sub.lines);
      continue;
    }
    const found = bevyDeps(text, workspaceDeps(dir));
    const shown = path.relative(process.cwd(), file) || file;
    if (found.length) {
      res.failed++;
      res.lines.push(`FAIL ${shown}`);
      for (const f of found) {
        const via = f.package && f.package !== f.name ? ` (package "${f.package}")` : '';
        res.lines.push(`  ${f.label} "${f.name}"${via} line ${f.line}`);
      }
    } else {
      res.lines.push(`OK   ${shown}: no bevy dependency`);
    }
  }
  return res;
}

function main(argv) {
  if (argv.length === 0 || argv.includes('-h') || argv.includes('--help')) {
    console.error('usage: node check-sim-outside-bevy.mjs <crate-dir> [<crate-dir> ...]');
    return 2;
  }
  const r = checkTargets(argv);
  console.log(r.lines.join('\n'));
  if (r.failed) {
    console.log(`${r.failed} crate(s) depend on bevy: the sim must stay outside Bevy`);
    return 1;
  }
  return r.errors ? 2 : 0;
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(fileURLToPath(import.meta.url))) {
  process.exitCode = main(process.argv.slice(2));
}

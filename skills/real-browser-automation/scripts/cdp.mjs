#!/usr/bin/env node
// cdp.mjs - drive the INSTALLED Edge or Chrome, headless, over the Chrome DevTools
// Protocol (CDP). Zero dependencies: Node 22+ built-in WebSocket and fetch only.
// Library and small CLI in one file. Original code, MIT (scaffold).
//
//   import { launch } from './cdp.mjs';
//   const browser = await launch();                 // Edge first, then Chrome
//   const page = await browser.newPage();
//   await page.goto('http://127.0.0.1:8080/');      // loopback only, else it throws
//   console.log(await page.evaluate('navigator.webdriver'));
//   await page.click('#go'); await page.type('#name', 'Ada');
//   await page.screenshot('out.png');
//   await browser.close();                          // Browser.close, never a kill
//
//   node scripts/cdp.mjs --url http://127.0.0.1:8080/ --eval "navigator.webdriver" --screenshot out.png
//   node scripts/cdp.mjs --check-url http://example.com/      (prints REFUSE or ALLOW)
//
// SAFETY: the browser only talks to 127.0.0.1, localhost, [::1] and *.localhost.
// Three layers: assertLocal() on every goto, a Fetch.enable guard on every request
// the page makes (blocked ones are counted in browser.blocked), and a browser
// flag that sends all other traffic to a dead local proxy. Nothing here kills a process.

import { spawn, execFile } from 'node:child_process';
import { mkdtempSync, existsSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

// ---------------------------------------------------------------- loopback guard

export class LocalOnlyError extends Error {
  constructor(message, url) { super(message); this.name = 'LocalOnlyError'; this.url = String(url); }
}

const NET_SCHEMES = new Set(['http:', 'https:', 'ws:', 'wss:']);
const IN_PAGE_SCHEMES = new Set(['data:', 'blob:', 'about:']); // cannot leave the machine

/** True for 127.0.0.1, localhost, [::1] and *.localhost (hostname as the WHATWG URL parser gives it). */
export function isLocalHost(hostname) {
  const h = String(hostname).toLowerCase();
  return h === '127.0.0.1' || h === 'localhost' || h === '[::1]' ||
    (h.endsWith('.localhost') && h.length > '.localhost'.length);
}

/**
 * Throws LocalOnlyError unless url is http(s)/ws(s) on a loopback host.
 * data:, file:, about:, chrome: and every other scheme are refused unless the caller
 * lists the scheme (or the exact URL) in `allow`, e.g. { allow: ['data:'] }. Entries for http, https, ws, wss are ignored.
 * Returns the normalized URL string.
 */
export function assertLocal(url, { allow = [] } = {}) {
  let u;
  try { u = new URL(String(url)); } catch { throw new LocalOnlyError(`refused: not an absolute URL: ${String(url).slice(0, 80)}`, url); }
  // `allow` can open data:, file:, about:blank and the like. It can never admit a network scheme, so a host is never whitelisted.
  if (!NET_SCHEMES.has(u.protocol) && (allow.includes(u.protocol) || allow.includes(u.href))) return u.href;
  if (!NET_SCHEMES.has(u.protocol)) throw new LocalOnlyError(`refused: scheme ${u.protocol} is not allowed (only http, https, ws, wss on loopback)`, url);
  if (!isLocalHost(u.hostname)) throw new LocalOnlyError(`refused: host ${u.hostname} is not 127.0.0.1, localhost, [::1] or *.localhost`, url);
  return u.href;
}

export function isLocalUrl(url, opts) {
  try { assertLocal(url, opts); return true; } catch { return false; }
}

/** Verdict for a request the PAGE makes (Fetch guard). data:, blob: and about: stay inside the browser. */
export function requestAllowed(url, { allow = [] } = {}) {
  let u;
  try { u = new URL(String(url)); } catch { return false; }
  if (IN_PAGE_SCHEMES.has(u.protocol)) return true;
  return isLocalUrl(url, { allow });
}

// ---------------------------------------------------------------- finding the browser

export function browserCandidates() {
  const e = process.env;
  const roots = [e.ProgramFiles, e['ProgramFiles(x86)'], e.LOCALAPPDATA].filter(Boolean);
  const edge = roots.map(r => join(r, 'Microsoft', 'Edge', 'Application', 'msedge.exe'));
  const chrome = roots.map(r => join(r, 'Google', 'Chrome', 'Application', 'chrome.exe'));
  edge.push('/usr/bin/microsoft-edge', '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge');
  chrome.push('/usr/bin/google-chrome', '/usr/bin/chromium', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome');
  return { edge, chrome };
}

/** prefer: 'auto' (Edge, then Chrome) | 'edge' | 'chrome' | a path to an executable. Env CDP_BROWSER overrides 'auto'. */
export function findBrowser(prefer = 'auto') {
  const named = prefer === 'auto' || prefer === 'edge' || prefer === 'chrome';
  const asPath = named ? (prefer === 'auto' ? process.env.CDP_BROWSER : null) : prefer;
  if (asPath) {
    if (!existsSync(asPath)) throw new Error(`browser not found: ${asPath}`);
    return { name: 'custom', path: asPath };
  }
  const c = browserCandidates();
  const order = prefer === 'chrome' ? [['chrome', c.chrome]] : prefer === 'edge' ? [['edge', c.edge]] : [['edge', c.edge], ['chrome', c.chrome]];
  for (const [name, list] of order) {
    const hit = list.find(p => existsSync(p));
    if (hit) return { name, path: hit };
  }
  return null;
}

// ---------------------------------------------------------------- small helpers

const sleep = ms => new Promise(r => setTimeout(r, ms));

function withTimeout(promise, ms, what) {
  let t;
  const timer = new Promise((_, rej) => { t = setTimeout(() => rej(new Error(`timeout after ${ms} ms: ${what}`)), ms); });
  return Promise.race([promise, timer]).finally(() => clearTimeout(t));
}

function run(file, args) {
  return new Promise(res => execFile(file, args, { windowsHide: true }, (err, stdout) => res({ err, stdout: String(stdout || '') })));
}

/** True while a process with this pid exists. tasklist / ps only look; they never touch the process. */
async function pidAlive(pid) {
  if (process.platform === 'win32') {
    const { stdout } = await run('tasklist', ['/FI', `PID eq ${pid}`, '/NH', '/FO', 'CSV']);
    return stdout.includes(`"${pid}"`);
  }
  const { err } = await run('ps', ['-p', String(pid), '-o', 'pid=']);
  return !err;
}

// ---------------------------------------------------------------- the CDP connection

class Connection {
  constructor(ws) {
    this.ws = ws; this.nextId = 1; this.pending = new Map(); this.listeners = new Set(); this.closed = false;
    ws.addEventListener('message', ev => this._message(ev.data));
    ws.addEventListener('close', () => this._closed());
    ws.addEventListener('error', () => {});
  }
  static open(url, timeout = 10000) {
    return withTimeout(new Promise((resolve, reject) => {
      const ws = new WebSocket(url);
      ws.addEventListener('open', () => resolve(new Connection(ws)), { once: true });
      ws.addEventListener('error', () => reject(new Error(`WebSocket connect failed: ${url}`)), { once: true });
    }), timeout, `connect ${url}`);
  }
  _message(data) {
    const m = JSON.parse(typeof data === 'string' ? data : Buffer.from(data).toString('utf8'));
    if (m.id !== undefined) {
      const p = this.pending.get(m.id);
      if (!p) return;
      this.pending.delete(m.id);
      if (m.error) p.reject(new Error(`${p.method}: ${m.error.message} (code ${m.error.code})`));
      else p.resolve(m.result || {});
    } else {
      for (const fn of [...this.listeners]) { try { fn(m.method, m.params || {}, m.sessionId); } catch { /* a bad listener must not break the pump */ } }
    }
  }
  _closed() {
    this.closed = true;
    for (const p of this.pending.values()) p.reject(new Error(`connection closed during ${p.method}`));
    this.pending.clear();
    for (const fn of [...this.listeners]) { try { fn('connection.closed', {}, undefined); } catch { /* ignore */ } }
  }
  send(method, params = {}, sessionId, timeout = 30000) {
    if (this.closed) return Promise.reject(new Error(`connection closed, cannot send ${method}`));
    const id = this.nextId++;
    const msg = { id, method, params };
    if (sessionId) msg.sessionId = sessionId;
    const p = new Promise((resolve, reject) => { this.pending.set(id, { resolve, reject, method }); });
    this.ws.send(JSON.stringify(msg));
    return withTimeout(p, timeout, method).catch(e => { this.pending.delete(id); throw e; });
  }
  onEvent(fn) { this.listeners.add(fn); return () => this.listeners.delete(fn); }
}

class Session {
  constructor(conn, id, info) { this.conn = conn; this.id = id; this.type = info.type; this.targetId = info.targetId; }
  send(method, params, timeout) { return this.conn.send(method, params, this.id, timeout); }
  /** Resolves with the event params; subscribe BEFORE the action that causes the event. */
  waitEvent(method, timeout = 15000, test = () => true) {
    let off, stop;
    const p = withTimeout(new Promise((resolve, reject) => {
      off = this.conn.onEvent((m, params, sid) => { if (m === method && sid === this.id && test(params)) resolve(params); });
      stop = () => reject(new Error('cancelled'));
    }), timeout, `event ${method}`).finally(() => off && off());
    p.catch(() => {}); // an unused waiter must not crash node
    p.cancel = stop;
    return p;
  }
}

// ---------------------------------------------------------------- keyboard tables

const NAMED_KEYS = {
  Enter: { key: 'Enter', code: 'Enter', vk: 13, text: '\r' },
  Tab: { key: 'Tab', code: 'Tab', vk: 9 }, Backspace: { key: 'Backspace', code: 'Backspace', vk: 8 },
  Delete: { key: 'Delete', code: 'Delete', vk: 46 }, Escape: { key: 'Escape', code: 'Escape', vk: 27 },
  ArrowLeft: { key: 'ArrowLeft', code: 'ArrowLeft', vk: 37 }, ArrowUp: { key: 'ArrowUp', code: 'ArrowUp', vk: 38 },
  ArrowRight: { key: 'ArrowRight', code: 'ArrowRight', vk: 39 }, ArrowDown: { key: 'ArrowDown', code: 'ArrowDown', vk: 40 },
  Home: { key: 'Home', code: 'Home', vk: 36 }, End: { key: 'End', code: 'End', vk: 35 },
  PageUp: { key: 'PageUp', code: 'PageUp', vk: 33 }, PageDown: { key: 'PageDown', code: 'PageDown', vk: 34 },
};
const BASE_KEYS = {
  ' ': ['Space', 32], ';': ['Semicolon', 186], '=': ['Equal', 187], ',': ['Comma', 188], '-': ['Minus', 189],
  '.': ['Period', 190], '/': ['Slash', 191], '`': ['Backquote', 192], '[': ['BracketLeft', 219],
  '\\': ['Backslash', 220], ']': ['BracketRight', 221], "'": ['Quote', 222],
};
const SHIFTED = {
  ':': ';', '+': '=', '<': ',', '_': '-', '>': '.', '?': '/', '~': '`', '{': '[', '|': '\\', '}': ']', '"': "'",
  '!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7', '*': '8', '(': '9', ')': '0',
};
const SHIFT = 8; // Input.dispatchKeyEvent modifiers: Alt=1, Ctrl=2, Meta=4, Shift=8

/** Key description for one character or a name like 'Enter'; null if there is no US-keyboard key for it. */
export function keyFor(k) {
  if (NAMED_KEYS[k]) return { ...NAMED_KEYS[k], modifiers: 0 };
  if (/^[a-z]$/.test(k)) return { key: k, code: 'Key' + k.toUpperCase(), vk: k.toUpperCase().charCodeAt(0), text: k, unmod: k, modifiers: 0 };
  if (/^[A-Z]$/.test(k)) return { key: k, code: 'Key' + k, vk: k.charCodeAt(0), text: k, unmod: k.toLowerCase(), modifiers: SHIFT };
  if (/^[0-9]$/.test(k)) return { key: k, code: 'Digit' + k, vk: k.charCodeAt(0), text: k, unmod: k, modifiers: 0 };
  if (BASE_KEYS[k]) return { key: k, code: BASE_KEYS[k][0], vk: BASE_KEYS[k][1], text: k, unmod: k, modifiers: 0 };
  if (SHIFTED[k]) {
    const b = SHIFTED[k];
    const [code, vk] = /^\d$/.test(b) ? ['Digit' + b, b.charCodeAt(0)] : BASE_KEYS[b];
    return { key: k, code, vk, text: k, unmod: b, modifiers: SHIFT };
  }
  return null;
}

// ---------------------------------------------------------------- Page

// Runs inside the page: is the element there, visible, enabled, and the real hit target at its centre?
const probeSource = selector => `(() => {
  const el = document.querySelector(${JSON.stringify(selector)});
  if (!el) return { why: 'no element matches' };
  el.scrollIntoView({ block: 'center', inline: 'center' });
  const r = el.getBoundingClientRect();
  if (r.width < 1 || r.height < 1) return { why: 'empty box' };
  const cs = getComputedStyle(el);
  if (cs.visibility === 'hidden' || cs.display === 'none') return { why: 'not visible' };
  if (el.disabled) return { why: 'disabled' };
  const x = r.left + r.width / 2, y = r.top + r.height / 2;
  const top = document.elementFromPoint(x, y);
  if (!top || !(top === el || el.contains(top))) return { why: 'covered by ' + (top ? top.tagName : 'nothing') };
  return { ok: true, x: Math.round(x * 10) / 10, y: Math.round(y * 10) / 10, w: Math.round(r.width), h: Math.round(r.height) };
})()`;

export class Page {
  constructor(browser, session) {
    this.browser = browser; this.session = session; this.targetId = session.targetId; this.console = [];
    if (browser.console) {
      browser.conn.onEvent((m, p, sid) => {
        if (sid !== session.id || this.console.length >= 200) return;
        if (m === 'Runtime.consoleAPICalled') this.console.push(`${p.type}: ${(p.args || []).map(a => a.value ?? a.description ?? '').join(' ')}`);
        if (m === 'Runtime.exceptionThrown') this.console.push(`exception: ${p.exceptionDetails.exception?.description || p.exceptionDetails.text}`);
      });
    }
  }
  send(method, params, timeout) { return this.session.send(method, params, timeout); }

  /** Navigate and wait for Page.loadEventFired. Throws LocalOnlyError BEFORE any request for a non-loopback URL. */
  async goto(url, { timeout = 15000 } = {}) {
    const target = assertLocal(url, { allow: this.browser.allow });
    const loaded = this.session.waitEvent('Page.loadEventFired', timeout);
    try {
      const r = await this.send('Page.navigate', { url: target }, timeout);
      if (r.errorText) throw new Error(`navigation to ${target} failed: ${r.errorText}`);
    } catch (e) { loaded.cancel(); throw e; }
    await loaded;
    return target;
  }

  /** Evaluate a JS expression string (or a function plus JSON-able args); promises are awaited; returns the value. */
  async evaluate(code, ...args) {
    const expression = typeof code === 'function' ? `(${code.toString()}).apply(null, ${JSON.stringify(args)})` : String(code);
    const r = await this.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error(`evaluate failed: ${r.exceptionDetails.exception?.description || r.exceptionDetails.text}`);
    return r.result.value;
  }

  /** Poll a JS expression until it is truthy (no fixed sleeps). Returns the value; throws on timeout. */
  async waitForFunction(expression, { timeout = 5000, interval = 50 } = {}) {
    const end = Date.now() + timeout;
    while (Date.now() < end) {
      const v = await this.evaluate(expression);
      if (v) return v;
      await sleep(interval);
    }
    throw new Error(`timeout after ${timeout} ms waiting for: ${String(expression).slice(0, 80)}`);
  }

  /** Wait until the element is visible, enabled, still, and not covered. Returns its centre point. */
  async waitForActionable(selector, timeout = 5000) {
    const end = Date.now() + timeout;
    let last = { why: 'never probed' }, prev = null;
    while (Date.now() < end) {
      last = await this.evaluate(probeSource(selector));
      if (last.ok) {
        if (prev && prev.x === last.x && prev.y === last.y && prev.w === last.w && prev.h === last.h) return last;
        prev = last;
      } else prev = null;
      await sleep(60);
    }
    throw new Error(`${selector}: not actionable after ${timeout} ms (${last.why})`);
  }

  /** Real mouse events: move, press, release at the element centre (events arrive with isTrusted true). */
  async click(selector, { timeout = 5000 } = {}) {
    const { x, y } = await this.waitForActionable(selector, timeout);
    await this.send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y });
    await this.send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', buttons: 1, clickCount: 1 });
    await this.send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', buttons: 0, clickCount: 1 });
  }

  /** One real key press (keyDown + keyUp). k is a character or a name like Enter, Tab, Backspace, ArrowDown. */
  async press(k) {
    const i = keyFor(k);
    if (!i) { await this.send('Input.insertText', { text: k }); return; } // no key for it: text only, no key events
    const base = { modifiers: i.modifiers, key: i.key, code: i.code, windowsVirtualKeyCode: i.vk, nativeVirtualKeyCode: i.vk };
    await this.send('Input.dispatchKeyEvent', { ...base, type: i.text ? 'keyDown' : 'rawKeyDown', text: i.text, unmodifiedText: i.unmod ?? i.text });
    await this.send('Input.dispatchKeyEvent', { ...base, type: 'keyUp' });
  }

  /** Click the element to focus it (real click), then press each character as a real key. delay = ms between keys. */
  async type(selector, text, { delay = 0, timeout = 5000 } = {}) {
    await this.click(selector, { timeout });
    for (const ch of text) { await this.press(ch); if (delay) await sleep(delay); }
  }

  /** Viewport screenshot to a PNG file. */
  async screenshot(path) {
    const { data } = await this.send('Page.captureScreenshot', { format: 'png' });
    const buf = Buffer.from(data, 'base64');
    writeFileSync(path, buf);
    return { path, bytes: buf.length };
  }

  async close() { await this.browser.conn.send('Target.closeTarget', { targetId: this.targetId }); }
}

// ---------------------------------------------------------------- Browser

class Browser {
  constructor(o) { Object.assign(this, o); this.sessions = new Map(); this.waiters = new Map(); this.blocked = []; this.guardGaps = []; this.closed = false; }

  get blockedCount() { return this.blocked.length; }

  _onEvent(method, params, sessionId) {
    if (method === 'Target.attachedToTarget') this._attached(params);
    else if (method === 'Target.detachedFromTarget') this.sessions.delete(params.sessionId);
    else if (method === 'Fetch.requestPaused') this._paused(params, sessionId);
  }

  _paused(p, sessionId) {
    const url = p.request.url;
    if (requestAllowed(url, { allow: this.allow })) {
      this.conn.send('Fetch.continueRequest', { requestId: p.requestId }, sessionId).catch(() => {});
      return;
    }
    if (this.blocked.length < 1000) {
      this.blocked.push({ url, method: p.request.method, resourceType: p.resourceType, targetType: this.sessions.get(sessionId)?.type, afterRedirect: Boolean(p.redirectedRequestId) });
    }
    this.conn.send('Fetch.failRequest', { requestId: p.requestId, errorReason: 'BlockedByClient' }, sessionId).catch(() => {});
  }

  _waiter(targetId) {
    if (!this.waiters.has(targetId)) {
      let resolve; const promise = new Promise(r => { resolve = r; });
      this.waiters.set(targetId, { promise, resolve });
    }
    return this.waiters.get(targetId);
  }

  async _attached({ sessionId, targetInfo, waitingForDebugger }) {
    const s = new Session(this.conn, sessionId, targetInfo);
    this.sessions.set(sessionId, s);
    try {
      if (this.fetchGuard) await s.send('Fetch.enable', { patterns: [{ urlPattern: '*' }] });
    } catch (e) { s.guardError = e.message; this.guardGaps.push({ type: targetInfo.type, url: targetInfo.url, error: e.message }); }
    // Children of this target (frames, workers) attach paused, get the same guard, then resume.
    await s.send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: true, flatten: true }).catch(() => {});
    if (targetInfo.type === 'page') {
      await s.send('Page.enable').catch(() => {});
      if (this.console) await s.send('Runtime.enable').catch(() => {});
    }
    if (waitingForDebugger) await s.send('Runtime.runIfWaitingForDebugger').catch(() => {});
    this._waiter(targetInfo.targetId).resolve(s);
  }

  /** Open a new tab (about:blank) with the guards already on. */
  async newPage() {
    const { targetId } = await this.conn.send('Target.createTarget', { url: 'about:blank' });
    const session = await withTimeout(this._waiter(targetId).promise, 15000, 'attach to new page');
    if (session.guardError) throw new Error(`Fetch guard could not be enabled on the new page (${session.guardError}); refusing to use it`);
    return new Page(this, session);
  }

  /**
   * Browser.close, then wait for the browser process to be gone. Never kills.
   * If it is still alive after `timeout` ms, throws and leaves it alone.
   */
  async close({ timeout = this.closeTimeout } = {}) {
    if (this.closed) return;
    this.closed = true;
    await this.conn.send('Browser.close', {}, undefined, 5000).catch(() => {}); // the socket may drop before the reply
    // Chrome: the process node spawned IS the browser, so node's exit event is exact and free.
    // Edge on Windows: the spawned launcher exits at once, so look the real pid up (tasklist only looks).
    const gone = async () => (this.pid === this.spawnedPid ? this.state.exit !== null : !(await pidAlive(this.pid)));
    const end = Date.now() + timeout;
    while (Date.now() < end && !(await gone())) await sleep(150);
    if (!(await gone())) {
      throw new Error(`browser pid ${this.pid} did not exit within ${timeout / 1000} s after Browser.close; not killing it (profile ${this.userDataDir} left in place)`);
    }
    // children can hold the profile a little longer than the main process
    for (let i = 0; i < 40 && existsSync(this.userDataDir); i++) {
      try { rmSync(this.userDataDir, { recursive: true, force: true }); } catch { await sleep(250); }
    }
    this.profileRemoved = !existsSync(this.userDataDir);
  }
}

// Flags that would open the debugging port to the network, change the profile, or bypass the proxy guard.
const FORBIDDEN_ARGS = ['--remote-debugging-address', '--remote-allow-origins', '--remote-debugging-port', '--remote-debugging-pipe',
  '--user-data-dir', '--proxy-server', '--proxy-bypass-list', '--proxy-pac-url', '--no-proxy-server', '--proxy-auto-detect',
  '--host-resolver-rules', '--headless', '--disable-web-security'];

/**
 * Start the installed browser headless on a fresh temporary profile and connect.
 * opts: browser ('auto'|'edge'|'chrome'|path), width, height, args (extra flags), allow (schemes to whitelist),
 *       console (collect page console, needs Runtime.enable which pages can notice), timeout (start),
 *       closeTimeout (ms close() waits for the process to exit, default 10000; a real GPU can need 30000+),
 *       fetchGuard / proxyGuard (default true; turn off only to test the other layer).
 */
export async function launch(opts = {}) {
  const { browser = 'auto', width = 1280, height = 800, args = [], allow = [], console: consoleOn = false,
    timeout = 20000, closeTimeout = 10000, fetchGuard = true, proxyGuard = true } = opts;
  for (const a of args) {
    if (FORBIDDEN_ARGS.some(f => a === f || a.startsWith(f + '='))) throw new Error(`launch arg not allowed: ${a}`);
  }
  for (const a of allow) {
    if (/^(https?|wss?):/i.test(String(a))) throw new Error(`allow cannot admit a network scheme or host: ${a}`);
  }
  const found = findBrowser(browser);
  if (!found) throw new Error('no Edge or Chrome found (looked under Program Files, Program Files (x86), LOCALAPPDATA); set CDP_BROWSER to an executable');
  const userDataDir = mkdtempSync(join(tmpdir(), 'cdp-profile-'));
  const flags = [
    '--headless=new', '--remote-debugging-port=0', `--user-data-dir=${userDataDir}`,
    '--no-first-run', '--no-default-browser-check',
  ];
  if (width && height) flags.push(`--window-size=${width},${height}`); // width: 0 leaves the browser default
  // Layer 2: every host except loopback goes to a dead local proxy and fails, popups and workers included.
  if (proxyGuard) flags.push('--proxy-server=http://127.0.0.1:9', '--proxy-bypass-list=127.0.0.1;localhost;*.localhost;[::1]');
  flags.push(...args, 'about:blank');

  const child = spawn(found.path, flags, { stdio: ['ignore', 'ignore', 'pipe'], windowsHide: true });
  const state = { exit: null }; // set by node when the process we spawned has exited
  let stderr = '';
  child.stderr.on('data', d => { if (stderr.length < 4000) stderr += d; });
  child.on('exit', (code, sig) => { state.exit = { code, sig }; });

  let conn = null;
  try {
    // Edge on Windows starts through a launcher that exits with code 0 after ~70 ms while the real
    // browser keeps running, so an early exit with code 0 is normal. Only a non-zero exit is a failure.
    const portFile = join(userDataDir, 'DevToolsActivePort');
    const end = Date.now() + timeout;
    let port, path;
    while (Date.now() < end) {
      if (existsSync(portFile)) {
        let lines = [];
        try { lines = readFileSync(portFile, 'utf8').split(/\r?\n/).filter(Boolean); } catch { /* the browser is still writing it (EBUSY) */ }
        if (lines.length >= 2) { [port, path] = lines; break; }
      }
      if (state.exit && state.exit.code !== 0) throw new Error(`browser exited with code ${state.exit.code} before DevToolsActivePort appeared: ${stderr.trim().slice(0, 300)}`);
      await sleep(50);
    }
    if (!port) throw new Error(`no DevToolsActivePort in ${userDataDir} after ${timeout} ms (browser ${found.path})`);

    conn = await Connection.open(`ws://127.0.0.1:${port}${path}`);
    const version = await conn.send('Browser.getVersion');
    const procs = await conn.send('SystemInfo.getProcessInfo').catch(() => ({ processInfo: [] }));
    const pid = (procs.processInfo.find(p => p.type === 'browser') || {}).id || child.pid;
    const b = new Browser({ conn, name: found.name, executablePath: found.path, product: version.product, userAgent: version.userAgent,
      pid, spawnedPid: child.pid, state, port: Number(port), userDataDir, closeTimeout, allow, console: consoleOn, fetchGuard, proxyGuard, flags });
    conn.onEvent((m, p, sid) => b._onEvent(m, p, sid));
    // pages (ours, and popups) attach paused so the guard is on before their first request
    await conn.send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: true, flatten: true, filter: [{ type: 'page' }, { exclude: true }] });
    return b;
  } catch (e) {
    // a failed start must not leave a browser behind: ask it to close (never kill), then drop the profile
    if (conn) await conn.send('Browser.close', {}, undefined, 3000).catch(() => {});
    await sleep(1500);
    try { rmSync(userDataDir, { recursive: true, force: true }); } catch { /* still in use: leave it */ }
    throw e;
  }
}

// ---------------------------------------------------------------- CLI

function parseArgs(argv) {
  const o = { ops: [], args: [], flags: new Set() }; // ops keep the command-line order: --type then --click runs type first
  const valued = new Set(['url', 'eval', 'click', 'type', 'press', 'screenshot', 'browser', 'timeout', 'wait-for', 'check-url', 'allow', 'width', 'height', 'close-timeout', 'arg']);
  const stepKinds = new Set(['eval', 'click', 'type', 'press', 'wait-for']);
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith('--')) throw new Error(`unexpected argument: ${a}`);
    const k = a.slice(2);
    if (valued.has(k)) {
      if (i + 1 >= argv.length) throw new Error(`--${k} needs a value`);
      const v = argv[++i];
      if (stepKinds.has(k)) o.ops.push([k, v]); else if (k === 'arg') o.args.push(v); else o[k] = v;
    } else o.flags.add(k);
  }
  return o;
}

const USAGE = `usage: node cdp.mjs --url <loopback url> [steps, run in the order given] [--screenshot out.png]
   steps: --wait-for CSS | --click CSS | --type "CSS=text" | --press Key | --eval JS
   other: [--browser edge|chrome|PATH] [--timeout ms] [--close-timeout ms, default 60000] [--arg BROWSER_FLAG]... [--width N --height N] [--allow data:,about:blank] [--console]
       node cdp.mjs --check-url <url>     print ALLOW or REFUSE (exit 0 or 3), no browser started
       node cdp.mjs --info                print which browser would be used`;

export async function main(argv) {
  const o = parseArgs(argv);
  const allow = o.allow ? o.allow.split(',') : [];
  if (o['check-url'] !== undefined) {
    try { console.log(`ALLOW ${assertLocal(o['check-url'], { allow })}`); return 0; } catch (e) { console.log(`REFUSE ${e.message}`); return 3; }
  }
  if (o.flags.has('info')) { console.log(JSON.stringify(findBrowser(o.browser || 'auto'))); return 0; }
  if (!o.url) { console.error(USAGE); return 2; }
  try { assertLocal(o.url, { allow }); } catch (e) { console.error(e.message); return 3; } // refuse before a browser even starts
  const timeout = Number(o.timeout || 15000);
  const b = await launch({ browser: o.browser || 'auto', allow, console: o.flags.has('console'), closeTimeout: Number(o['close-timeout'] || 60000), args: o.args,
    width: Number(o.width || 1280), height: Number(o.height || 800) });
  const out = { browser: b.product, url: o.url, eval: [] };
  let code = 0;
  try {
    const page = await b.newPage();
    await page.goto(o.url, { timeout });
    for (const [kind, v] of o.ops) {
      if (kind === 'click') await page.click(v, { timeout });
      else if (kind === 'wait-for') await page.waitForActionable(v, timeout);
      else if (kind === 'press') await page.press(v);
      else if (kind === 'eval') out.eval.push(await page.evaluate(v));
      else { const i = v.indexOf('='); await page.type(v.slice(0, i), v.slice(i + 1), { timeout }); }
    }
    if (o.screenshot) out.screenshot = await page.screenshot(o.screenshot);
    if (o.flags.has('console')) out.console = page.console;
  } catch (e) {
    out.error = e.message; code = e instanceof LocalOnlyError ? 3 : 1;
  } finally {
    out.blockedRequests = b.blocked;
    try { await b.close(); out.closed = true; } catch (e) { out.closeError = e.message; code = code || 1; }
  }
  console.log(JSON.stringify(out, null, 2));
  return code;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main(process.argv.slice(2)).then(c => { process.exitCode = c; }, e => { console.error(e.message); process.exitCode = 1; });
}

// loop-keeper: continues THIS repo's /sprint when its session goes idle, and
// only when nothing went wrong. Each desktop session has its own keeper; the
// other two repos are read for status, never driven.
//
// A continue needs all of these, checked at idle and again right before sending:
//   - the owner's latest word is the /sprint command or a plain go ("GO", "g0",
//     "continue", "GO NON STOP"); a question or an instruction pauses the loop
//     until the owner says go or runs /sprint again; stop words stop it;
//   - no halt file, handoff not terminal or paused, this session's lock is
//     fresh and unchanged, the command was not one-round (wave, once, round);
//   - no owner abort or hard error in the last reply and no `LOOP STOP:` line;
//   - recent turns used tools, and recent continues moved the handoff or lock.
// When the loop itself stops (a `LOOP STOP:` line in its reply or its handoff,
// 3 turns without a tool call, 3 continues without a handoff or lock update),
 // the keeper stops it: LOOP STOP means stop. Strict STOP_LINE plus the toolless
// and stall counters guard against a lazy or false stop; the watchdog's GO
// resumes a loop that stopped by itself.
// Transient failures (rate limit, 5xx, network, retry proxy down) are retried
// after 2, 5, 10 and 20 minutes, then it stops. A down proxy with no proxy
// process is started once per 15 minutes from the owner's Desktop bat.
// A full context (overflow, or a 400 on a context over 600k tokens) is
// compacted once on the loop's model, then the continue goes out.
// Ralph pattern (2026-10-02): at the continue point, when the lead session's
// session context (last assistant message's total tokens, knob `fresh_ctx_k`, default 120)
// passes fresh_ctx_k*1000, a fresh sprint session replaces this one (the same path as `new`: retire, then
// /sprint takeover, which resumes from the handoff file) instead of the continue;
// at most once per 30 min per repo, logged.
// The continue keeps the loop's agent, model and variant, carries warnings
// before a stop threshold, and a status line of all three sprints.
// Helpers run in foreground batches (owner 2026-09-28, C-88: "no background in all repos",
// "I want it seen live"; knob `dispatch`, see the queue section): the keeper writes the next
// batch, the loop sends it as one message of Task calls, and every helper works live in the
// loop's own session. With `dispatch` "queue" the 2026-09-27 crew returns: the keeper starts
// queued packets by itself and a Task may go to the background (OpenCode's `background: true`,
// env OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS). Helpers working while the loop's own session
// is idle get no continue in that mode (status "running", busy stays true so a pause or
// restart waits for them); a result turn never counts toward a stop; a new
// message only cancels a waiting continue, and the next idle decides again.
// STOP also cancels the helpers: OpenCode's abort cancels a session's Tasks.
// Lock stops heal: a lock the loop's own handoff names that only aged is a refresh
// the loop forgot (the continue asks for one), and a stop for a missing, invalid or
// stale lock lifts once the lock is valid again (factory 2026-09-27: 5 h dead on a
// lock the new session wrote 11 minutes after the stop). GO carries the same facts.
// Status for the owner: `loop-keeper.json` holds the last decision plus a
// snapshot rewritten every minute (keeper alive, sprint session title, busy,
// todo progress, last words; running / silent after 45 quiet minutes / waiting
// for the owner). The OpenCode server needs a password outside the app, so the
// Prompt Popper talks to this keeper through `loop-keeper.cmd.json`: GO sends
// "GO (from the popper)" to this repo's sprint session as the owner's word
// (a sprint session is one whose /sprint text names this repo's current
// handoff file; an old-protocol session is never driven),
// SPRINT does the same or, when the repo has no sprint session, opens one with
// /sprint (takeover when an orphaned lock exists), STOP aborts its turn, NEW
// opens a fresh sprint session (the old one's turn is aborted and it is retired:
// never continued again). The Empire Boss in center (`empire.mjs`) writes the
// same file with `from` set, so its GO reads "GO (from the Empire Boss)".
// Commands older than 2 minutes are ignored. `loop-keeper.json` advertises
// the supported commands so the popper can enable its Reply button.
// The agents' shell is pwsh, but they write bash: exact equivalents (`2>/dev/null`,
// `| head -20`, `| tail`, `| wc -l`, a `cd` to the repo root) are rewritten before
// a bash call runs, counted in `shellFixes` (see SHELL_FIXES). More rules live in
// code, counted in `callFixes`: todowrite gets its missing fields, a Task stays in the
// foreground (queue mode: a writer goes to the background, see FOREGROUND), `packet: <name>`
// becomes that packet's text and role, a generic-agent packet goes to the role
// its title names, and every non-gate packet asks for a RESULT line (see GATE).
// Knobs (the owner's numbers, `.opencode/knobs.json`, set from the popper or empire.mjs):
// a change since the last continue is named in the next one, and `knobsSeen` in
// loop-keeper.json records which version the loop was told.
// OpenCode starts every exported function as a plugin: export only LoopKeeper.
// Only the CFG block differs between the repos (the three loops and center); keep the rest identical.
import { appendFileSync, existsSync, mkdirSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { execFile, spawn } from "node:child_process";
import { connect } from "node:net";
import { freemem, homedir, tmpdir } from "node:os";
import { basename, dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const CODE_AT = new Date().toISOString(); // when OpenCode loaded this file

const REPOS = {
  // Generated from center/empire.json by sync-keeper.mjs (keeper-repos.mjs): register a loop there.
  engine2040: {
    lock: "C:/engine2040/target/sprint.lock", halt: "C:/engine2040/target/sprint.halt",
    handoff: "C:/engine2040/target/sprint-handoff.md", inbox: "C:/engine2040/docs/EMPIRE-INBOX.md",
    state: "C:/engine2040/target/loop-keeper.json", cmd: "C:/engine2040/target/loop-keeper.cmd.json",
    knobs: "C:/engine2040/.opencode/knobs.json", command: "C:/engine2040/.opencode/commands/sprint.md",
  },
  forge: {
    lock: "C:/forge-data/sprint/lock.txt", halt: "C:/forge/STOP",
    handoff: "C:/forge-data/sprint/board.md", inbox: "C:/forge-data/sprint/empire-inbox.md",
    state: "C:/forge-data/sprint/loop-keeper.json", cmd: "C:/forge-data/sprint/loop-keeper.cmd.json",
    knobs: "C:/forge/.opencode/knobs.json", command: "C:/forge/.opencode/commands/sprint.md",
  },
  factory: {
    lock: "C:/Users/me/Desktop/autonomous-factory/board/.sprint-lock", halt: "C:/Users/me/Desktop/autonomous-factory/STOP",
    handoff: "C:/Users/me/Desktop/autonomous-factory/board/sprint-handoff.md", inbox: "C:/Users/me/Desktop/autonomous-factory/board/empire-inbox.md",
    state: "C:/Users/me/Desktop/autonomous-factory/logs/loop-keeper.json", cmd: "C:/Users/me/Desktop/autonomous-factory/logs/loop-keeper.cmd.json",
    knobs: "C:/Users/me/Desktop/autonomous-factory/.opencode/knobs.json", command: "C:/Users/me/Desktop/autonomous-factory/.opencode/commands/sprint.md",
  },
  center: {
    lock: "C:/Users/me/Desktop/center/sprint/lock.txt", halt: "C:/Users/me/Desktop/center/sprint/halt",
    handoff: "C:/Users/me/Desktop/center/sprint/handoff.md", inbox: "C:/Users/me/Desktop/center/sprint/inbox.md",
    state: "C:/Users/me/Desktop/center/sprint/loop-keeper.json", cmd: "C:/Users/me/Desktop/center/sprint/loop-keeper.cmd.json",
    knobs: "C:/Users/me/Desktop/center/.opencode/knobs.json", command: "C:/Users/me/Desktop/center/.opencode/commands/sprint.md",
  },
  "fp-research": {
    lock: "C:/Users/me/Desktop/fp-research/sprint/lock.txt", halt: "C:/Users/me/Desktop/fp-research/sprint/halt",
    handoff: "C:/Users/me/Desktop/fp-research/sprint/handoff.md", inbox: "C:/Users/me/Desktop/fp-research/sprint/inbox.md",
    state: "C:/Users/me/Desktop/fp-research/sprint/loop-keeper.json", cmd: "C:/Users/me/Desktop/fp-research/sprint/loop-keeper.cmd.json",
    knobs: "C:/Users/me/Desktop/fp-research/.opencode/knobs.json", command: "C:/Users/me/Desktop/fp-research/.opencode/commands/sprint.md",
  },
  "marketing-studio": {
    lock: "C:/Users/me/Desktop/marketing-studio/sprint/lock.txt", halt: "C:/Users/me/Desktop/marketing-studio/sprint/halt",
    handoff: "C:/Users/me/Desktop/marketing-studio/sprint/handoff.md", inbox: "C:/Users/me/Desktop/marketing-studio/sprint/inbox.md",
    state: "C:/Users/me/Desktop/marketing-studio/sprint/loop-keeper.json", cmd: "C:/Users/me/Desktop/marketing-studio/sprint/loop-keeper.cmd.json",
    knobs: "C:/Users/me/Desktop/marketing-studio/.opencode/knobs.json", command: "C:/Users/me/Desktop/marketing-studio/.opencode/commands/sprint.md",
  },
  jobhunt: {
    lock: "C:/Users/me/Desktop/jobhunt/sprint/lock.txt", halt: "C:/Users/me/Desktop/jobhunt/sprint/halt",
    handoff: "C:/Users/me/Desktop/jobhunt/sprint/handoff.md", inbox: "C:/Users/me/Desktop/jobhunt/sprint/inbox.md",
    state: "C:/Users/me/Desktop/jobhunt/sprint/loop-keeper.json", cmd: "C:/Users/me/Desktop/jobhunt/sprint/loop-keeper.cmd.json",
    knobs: "C:/Users/me/Desktop/jobhunt/.opencode/knobs.json", command: "C:/Users/me/Desktop/jobhunt/.opencode/commands/sprint.md",
  },
  "design-studio": {
    lock: "C:/Users/me/Desktop/design-studio/sprint/lock.txt", halt: "C:/Users/me/Desktop/design-studio/sprint/halt",
    handoff: "C:/Users/me/Desktop/design-studio/sprint/handoff.md", inbox: "C:/Users/me/Desktop/design-studio/sprint/inbox.md",
    state: "C:/Users/me/Desktop/design-studio/sprint/loop-keeper.json", cmd: "C:/Users/me/Desktop/design-studio/sprint/loop-keeper.cmd.json",
    knobs: "C:/Users/me/Desktop/design-studio/.opencode/knobs.json", command: "C:/Users/me/Desktop/design-studio/.opencode/commands/sprint.md",
  },
  skillworks: {
    lock: "C:/Users/me/Desktop/skillworks/sprint/lock.txt", halt: "C:/Users/me/Desktop/skillworks/sprint/halt",
    handoff: "C:/Users/me/Desktop/skillworks/sprint/handoff.md", inbox: "C:/Users/me/Desktop/skillworks/sprint/inbox.md",
    state: "C:/Users/me/Desktop/skillworks/sprint/loop-keeper.json", cmd: "C:/Users/me/Desktop/skillworks/sprint/loop-keeper.cmd.json",
    knobs: "C:/Users/me/Desktop/skillworks/.opencode/knobs.json", command: "C:/Users/me/Desktop/skillworks/.opencode/commands/sprint.md",
  },
};
const CFG = {
  repo: "skillworks",
  marker: "Run the skillworks loop from `sprint/board.md` toward `VISION.md`",
  log: "C:/Users/me/AppData/Local/Temp/opencode/skillworks-kit/sprint/loop-keeper.log",
  proxyPort: 13579, // free Muse through the retry proxy
  proxyStart: "C:\\Users\\me\\Desktop\\Start_Retry_Proxy.bat",
  next: "round",
  handoffName: "`sprint/handoff.md`",
  haltName: "`sprint/halt`",
};
// ---- identical below this line in every repo ----
const GAP_MS = 20_000;
const BACKOFF_MS = [2, 5, 10, 20].map((m) => m * 60_000); // transient failure retries, then stop
const WATCH_MS = 60_000; // snapshot for the popper and empire-scan
const CMD_POLL_MS = 3_000; // popper command file check (one stat)
const CMD_MAX_AGE_MS = 2 * 60_000; // older popper commands are ignored
const SILENT_MS = 45 * 60_000; // busy with no session event this long = silent
const PROXY_RESTART_MS = 15 * 60_000; // at most one proxy start per window, shared by all keepers
const MAX_LOCK_AGE_MS = 2 * 60 * 60_000;
// Stops that lift by themselves once their cause is gone: a lock problem once the lock is valid,
// and "halted" once the owner's resume removed the halt file (forge 2026-09-27: resumed mid-turn,
// no GO went out, and the old "halted" stop held it after the turn ended).
const LOCK_STOP = /^(?:no valid lock|missing lock|stale lock|lock changed|halted)\b/;
const MAX_TOOLLESS = 3; // idle turns in a row without a tool call
const MAX_STALL = 3; // continues in a row that moved neither handoff nor lock
const STOP_LINE = /^\s*LOOP STOP:.*$/m;
const ONE_SHOT = /\bArguments:\s*(?:wave|once|round)(?:[\s.,]|$)/i;
const KEEPER = "[loop-keeper]";
const QUEUE_RESULTS = `${KEEPER} Queue results`;
const QUEUE_STUCK_MS = 60 * 60_000; // a queued helper past this is stopped and reported failed
// Center runs every repo's checks (drift, docs, editors) every few minutes and keeps the results here.
const CHECKS_FILE = "C:/Users/me/Desktop/center/empire-check.json";
const CHECKS_FRESH_MS = 2 * 60 * 60_000; // older results say nothing about now
// Center keeps each repo's lowest open finish bar here (finish-cache.mjs, started by the watchdog pass).
const FINISH_FILE = join(process.env.EMPIRE_STATE || join(homedir(), ".empire", "state"), "finish.json");
const FINISH_FRESH_MS = 2 * 60 * 60_000; // an older file says nothing about now: the fact is left out
const POPPER_GO = "GO (from the popper)";
// Owner words. "GO NON STOP", "don't stop" and "no stops" mean go, not stop.
const KEEP_GOING = /\b(?:non[\s-]?stop|no[\s-]+stops?|don'?t\s+stop|do\s+not\s+stop|never\s+stop|without\s+stopping|no\s+pauses?)\b/gi;
const NO_GO = /\b(?:don'?t|do\s+not|never|no)\s+(?:go|continue|resume|proceed)\b/i;
const STOP_WORD = /\b(?:stop|halt|pause|wait|hold\s+on|quit|cancel|abort|enough|freeze)\b/i;
// "g0" and "goo" are GO typed fast (engine 2026-09-25: the owner's "g0" read as chatting).
const GO_WORD = /\b(?:g[o0]+|continue|resume|proceed|keep\s+going|carry\s+on|next\s+(?:round|wave|cycle))\b/i;
// Errors worth a retry: provider rate limits, 5xx, network. Owner abort, auth,
// context overflow and output length never are.
const HARD_ERRORS = new Set(["MessageAbortedError", "ProviderAuthError", "ContextOverflowError", "MessageOutputLengthError"]);
// A full context window gets one compaction, then the continue. Muse behind the
// proxy answers a full 1M window with a plain 400 "invalid parameters"
// (engine 2026-09-25 at 1,016,682 tokens), so a 400 on a big context counts too.
const OVERFLOW_MIN_TOKENS = 600_000;
const STALE_HANDOFF_MS = 60 * 60_000; // older = the continue asks for a rewrite
const FRESH_CTX_DEFAULT_K = 120; // knob `fresh_ctx_k`: fresh session past this many k input tokens
const FRESH_CTX_MIN_MS = 30 * 60_000; // at most one fresh-context session per window per repo
const TRANSIENT_STATUS = new Set([408, 425, 429, 500, 502, 503, 504, 529]);
const TRANSIENT_TEXT = /ECONNRESET|ECONNREFUSED|ETIMEDOUT|EAI_AGAIN|socket hang up|fetch failed|network|overloaded|rate.?limit|too many requests/i;
// The keeper's own call to the OpenCode server dropped: never a stop (engine 2026-09-27: one
// "terminated" at 10:59 stopped the loop until a GO 35 minutes later).
const keeperGlitch = (e) => TRANSIENT_TEXT.test(String(e?.message ?? e)) || /terminated|other side closed|UND_ERR|aborted|timed? ?out/i.test(String(e?.message ?? e));
const PROXY_PS = Buffer.from("@(Get-CimInstance Win32_Process -Filter \"Name='node.exe'\" | Where-Object CommandLine -like '*retry-proxy*').Count", "utf16le").toString("base64");

const textOf = (m) => (m?.parts ?? [])
  .filter((p) => p.type === "text").map((p) => p.text ?? "").join("\n");
const read = (p) => { try { return readFileSync(p, "utf8"); } catch { return null; } };
const mtime = (p) => { try { return statSync(p).mtimeMs; } catch { return null; } };
const clip = (t, n = 60) => { const s = String(t).replace(/\s+/g, " ").trim(); return s.length > n ? `${s.slice(0, n)}...` : s; };
const keyOf = (m, msgs) => (m ? m.info?.id ?? `msg-${msgs.indexOf(m)}` : null);
const isUser = (m) => m?.info?.role === "user";
const hasCompaction = (m) => (m.parts ?? []).some((p) => p.type === "compaction");
// Compaction turns and OpenCode's own "Continue if you have next steps" are not the owner.
const texts = (m) => (m.parts ?? []).filter((p) => p.type === "text");
const isSystemTurn = (m) => hasCompaction(m) || (texts(m).length > 0 && texts(m).every((p) => p.synthetic));
const isOwner = (m) => isUser(m) && !isSystemTurn(m) && !textOf(m).trimStart().startsWith(KEEPER);
// A GO the keeper sends carries its facts after KEEPER: only the owner's part is read.
const intentOf = (text) => {
  const t = text.split(KEEPER)[0].trim();
  if (!t) return "chat";
  const soft = t.replace(KEEP_GOING, " go ");
  if (NO_GO.test(soft) || STOP_WORD.test(soft)) return "stop";
  if (t.length <= 300 && !t.includes("?") && GO_WORD.test(soft)) return "go";
  return "chat";
};
const isTransient = (e) => !!e && !HARD_ERRORS.has(e.name) && (e.data?.isRetryable === true ||
  TRANSIENT_STATUS.has(e.data?.statusCode) || TRANSIENT_TEXT.test(String(e.data?.message ?? "")));
const tokensOf = (m) => {
  const t = m?.info?.tokens;
  return t ? t.total || (t.input ?? 0) + (t.output ?? 0) + (t.cache?.read ?? 0) + (t.cache?.write ?? 0) : 0;
};
const mayBeOverflow = (e) => e?.name === "ContextOverflowError" || (e?.name === "APIError" && e.data?.statusCode === 400);
const isOverflow = (e, msgs) => e?.name === "ContextOverflowError" || (mayBeOverflow(e) &&
  Math.max(0, ...msgs.filter((m) => m.info?.role === "assistant").slice(-6).map(tokensOf)) >= OVERFLOW_MIN_TOKENS);
const describe = (e) => (e.name === "MessageAbortedError" ? "the owner pressed stop"
  : `assistant error: ${e.name ?? "unknown"}${e.data?.message ? ` (${clip(e.data.message)})` : ""}`);
const viaOf = (m) => ({ agent: m?.info?.agent, model: m?.info?.model, variant: m?.info?.model?.variant });
const bodyFor = ({ agent, model, variant }, text) => ({
  ...(agent ? { agent } : {}),
  ...(model?.providerID && model?.modelID ? { model: { providerID: model.providerID, modelID: model.modelID } } : {}),
  ...(variant ? { variant } : {}),
  parts: [{ type: "text", text }],
});
const probePort = (port) => new Promise((resolve) => {
  const socket = connect({ host: "127.0.0.1", port });
  const done = (ok) => { socket.destroy(); resolve(ok); };
  socket.setTimeout(2000, () => done(false));
  socket.once("connect", () => done(true));
  socket.once("error", () => done(false));
});
// Start the owner's proxy bat (it restarts crashes itself), never a second proxy.
const startProxyBat = (bat) => new Promise((resolve) => {
  execFile("powershell.exe", ["-NoProfile", "-NonInteractive", "-EncodedCommand", PROXY_PS],
    { timeout: 20_000, windowsHide: true }, (err, out) => {
      if (!err && Number(String(out).trim()) > 0) return resolve("a proxy process runs but its port does not answer; not starting another");
      if (!existsSync(bat)) return resolve(`cannot start it: ${bat} is missing`);
      spawn("cmd.exe", ["/d", "/s", "/c", `start "Retry Proxy :13579" /min "${bat}"`],
        { detached: true, stdio: "ignore", windowsHide: true, windowsVerbatimArguments: true }).unref();
      resolve(`started ${bat}`);
    });
});

// Agents write bash into a pwsh shell. 24 h to 2026-09-26: `| head` failed 315 times,
// `2>/dev/null` 274, `| tail` 55, `| wc` 22 (OpenCode marks most "completed"), and
// deny-all reviewers lost whole calls to a `cd` into the repo or a `| head`. OpenCode
// starts pwsh with -NoProfile, so no alias can help: exact equivalents are rewritten
// before the call runs and before its permission check. Quoted text is never touched.
const SHELL_END = String.raw`(?=\s*(?:$|[|;&)]))`;
const SHELL_FIXES = [
  ["devnull", /&>\s*\/dev\/null\b/g, () => "*>$null"],
  ["devnull", /(\d?)>\s*\/dev\/null\b/g, (_, fd) => `${fd}>$null`],
  ["head", new RegExp(String.raw`\|\s*head(?:\s+-n\s*(\d+)|\s+-(\d+))?${SHELL_END}`, "g"), (_, a, b) => `| Select-Object -First ${a ?? b ?? 10}`],
  ["tail", new RegExp(String.raw`\|\s*tail(?:\s+-n\s*(\d+)|\s+-(\d+))?${SHELL_END}`, "g"), (_, a, b) => `| Select-Object -Last ${a ?? b ?? 10}`],
  ["wc", new RegExp(String.raw`\|\s*wc\s+-l${SHELL_END}`, "g"), () => "| Measure-Object -Line | Select-Object -ExpandProperty Lines"],
  // Windows has `python`, not `python3` (2026-09-29, 24 h: 21 failed calls in center).
  ["python3", /(^|[;&|(]\s*|\n\s*)python3(?=\s)/g, (_, pre) => `${pre}python`],
];
// Unix tools the agents write and pwsh lacks (2026-09-29, 24 h: 271 failed calls in center, 64 in forge, 60 in factory:
// "'grep' is not a pwsh command", sed, head, awk). Git for Windows ships them; a command that uses one gets that
// folder added to its own PATH, at the END, so every Windows command keeps its meaning. Nothing system-wide changes.
// Rules kept in code because the prompts asked and the models did not (2026-09-27):
// - todowrite: helpers leave out `priority` (factory 2026-09-26: 99 schema failures a day).
// - task, foreground (the default since 2026-09-28): `background: true` becomes false, so every
//   helper runs live in the loop's session; the batch is the unit, not a lone helper.
// - task, queue mode only: a writer runs in the background, so the loop never waits on its slowest
//   helper (2026-09-26: 1,019 Task calls, none in background, 1.3 of 20 helpers busy on average).
//   Gates go to the background too (2026-09-27: engine's orchestrator sat 33 of 180 minutes in 9
//   foreground judge/checker Tasks while nothing new started; their result wakes the loop like
//   any helper's). Quick lookups stay in the foreground.
//   Only in this repo's sprint sessions, only with OpenCode's background flag on, and an
//   explicit `background: false` wins.
const FOREGROUND = /^(?:overseer|explore|explorer)(?:-paid)?$/;
// - bash, every session: a build, test or gate command gets at least BUILD_TIMEOUT_MS. Models pick 5,
//   10 or 15 minutes; a cold pool build under load needs more, the call was killed and the work run
//   again (engine 2026-09-27/28: 35 calls, about 8 h of 48 h, all killed at their own timeout).
const BUILD_CMD = /(?:^|[;&|(\n])\s*(?:cargo(?:\.exe)?\s+(?:test|clippy|build|check|run|bench|nextest)|dotnet(?:\.exe)?\s+(?:build|test)|node\s+\S*(?:proof|test-fast|fresh-clone)\.mjs)\b/;
const BUILD_TIMEOUT_MS = 45 * 60_000;
// - bash, every session: that same heavy command goes through center's machine-wide slot queue (heavy.mjs).
//   2026-09-29, one PC of 12 threads: 4 loops started up to 9 heavy jobs at once, load 100% for hours, engine
//   cargo test 594 runs (35 h), forge's suite 221 runs (22 h), 16 calls a day killed at 45 min each, and forge's
//   fresh-clone proof (404 s on a quiet box) killed at 45 min in cycles 81, 83, 84 and 85. Now at most 4 heavy
//   commands run at once across ALL loops, a proof goes first, fresh-clone gets the empty box. The wait is
//   bounded (30 min, then the command runs anyway) and only a dead owner's slot is ever freed. Off: KEEPER_NO_HEAVY
//   in the command, `node heavy.mjs off`, KEEPER_HEAVY_OFF=1, or center's heavy.mjs missing (the command runs as before).
const HEAVY_WAIT_MS = 30 * 60_000;
const HEAVY_B64_MAX = 20_000;
const heavyJs = () => {
  const c = REPOS.center?.command;
  return c ? `${String(c).replace(/\\/g, "/").replace(/\/\.opencode\/commands\/sprint\.md$/, "")}/heavy.mjs` : null;
};
const heavyOn = () => {
  if (process.env.KEEPER_HEAVY_OFF) return false;
  const js = heavyJs();
  if (!js || !existsSync(js)) return false;
  return !existsSync(join(process.env.EMPIRE_STATE || join(homedir(), ".empire", "state"), "heavy", "off"));
};
const SUPPORTED_COMMANDS = ["go", "sprint", "stop", "new", "say", "archive", "chat"];
const centerDir = () => {
  const c = REPOS.center?.command;
  return c ? String(c).replace(/\\/g, "/").replace(/\/\.opencode\/commands\/sprint\.md$/, "") : null;
};
const sayJs = () => {
  const d = centerDir();
  return d ? `${d}/chat-say.mjs` : null;
};
const archiveJs = () => {
  const d = centerDir();
  return d ? `${d}/chat-archive.mjs` : null;
};
// A proof (forge's fresh clone) may wait in the queue and then run past helper_max_min: it keeps at least 90 minutes.
const PROOF_TEXT = /fresh-clone\.mjs/;
const PROOF_MIN = 90;
// - task: a packet sent to the generic agent whose title starts with a role this repo has goes to
//   that role, with its prompt, skills and model (factory 2026-09-27: 61 of 325 packets in 24 h,
//   "wildcard free", "picker score", "judge fall-65" on `general`).
// - task: every packet but a gate's asks for a closing RESULT line, so center's dispatch meter
//   (dispatch.mjs) reads what each helper delivered instead of guessing from its words.
const GATE = /^(?:judge|checker|overseer|api-reviewer)(?:-paid)?$/;
const NOT_ROLES = new Set(["orchestrator", "lead", "overseer", "general", "build", "plan"]);
const RESULT_ASK = "\n\nEnd your reply with one line: `RESULT: DONE|PARTIAL|BLOCKED|NOOP - <what changed, or the blocker> | proof: <command result, file or URL>`.";
// Roles that have a `<role>-paid.md` twin (the Go lane): hybrid mode (knob paid_mode = 1) sends those roles to the twin.
const paidIn = (dir) => {
  const out = new Map(); // role -> twin file
  for (const f of ["agents", "agent"]) {
    try {
      for (const n of readdirSync(join(dir, ".opencode", f))) if (n.endsWith("-paid.md")) out.set(n.slice(0, -"-paid.md".length).toLowerCase(), join(dir, ".opencode", f, n));
    } catch { /* no such folder */ }
  }
  return out;
};
const rolesIn = (dir) => {
  const out = new Set();
  for (const f of ["agents", "agent"]) {
    try {
      for (const n of readdirSync(join(dir, ".opencode", f))) if (n.endsWith(".md") && !n.endsWith("-paid.md")) out.add(n.slice(0, -3).toLowerCase());
    } catch { /* no such folder */ }
  }
  for (const n of NOT_ROLES) out.delete(n);
  return out;
};
const TODO_DEFAULTS = { status: "pending", priority: "medium" };
// Navigation rules (center's review of 67,178 tool calls, 2026-10-03): agents look for the claims file at the repo root
// (14+ misses), and read "No files found" from glob as "the file is missing" (428 empty globs in 48 h): OpenCode's glob runs
// ripgrep without --hidden and honors .gitignore, so .opencode/, .lanes/, queue/, target/ and logs/ are invisible to it.
const GLOB_BLIND_HINT = "[loop-keeper] glob does not see hidden folders (.opencode, .lanes) or paths in .gitignore (queue, target, logs), so \"No files found\" does not mean the file is missing. Read the exact path with the read tool, or list it with: Get-ChildItem -Force -Recurse <dir> -Filter <name>.";
const NOT_FOUND = /Cannot find path|cannot find the path|No such file|ItemNotFound/i;
const backgroundOn = () => /^(?:1|true)$/i.test(process.env.OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS ?? process.env.OPENCODE_EXPERIMENTAL ?? "");
const CD_FIRST = /^\s*cd\s+("[^"]*"|'[^']*'|[^\s;&|]+)\s*(?:&&|;)\s*/;
const QUOTED_OR_PLAIN = /("(?:[^"`]|`[\s\S])*"|'[^']*')|([^"']+)/g;
// `/c/forge`, `/forge`, `C:\forge\` and `"C:/forge"` are all the same place.
const pathKey = (p, drive = "c") => {
  let s = String(p ?? "").trim().replace(/^["']|["']$/g, "").replace(/\\/g, "/").replace(/\/+$/, "");
  const posix = s.match(/^\/([a-z])(\/.*)?$/i);
  if (posix) s = `${posix[1]}:${posix[2] ?? ""}`;
  else if (s.startsWith("/")) s = `${drive}:${s}`;
  return s.toLowerCase();
};
const shellOf = (dir) => {
  const home = process.env.USERPROFILE ?? process.env.HOME ?? "";
  const files = [dir && `${dir}/opencode.jsonc`, dir && `${dir}/opencode.json`, `${home}/.config/opencode/opencode.jsonc`, `${home}/.config/opencode/opencode.json`];
  for (const f of files) {
    const m = f && read(f)?.match(/^\s*"shell"\s*:\s*"([^"]+)"/m);
    if (m) return m[1];
  }
  return "";
};

// The keeper itself. LoopKeeper (the shell at the end of this file) runs it and swaps in a fresh
// copy when this file changes.
const createSeatReadiness = function createSeatReadiness({ read, file, claimsFile, now = Date.now, seen = new Map() }) {
  const json = (path) => { try { return JSON.parse(read(path)); } catch { return null; } };
  const baseRole = (role) => String(role ?? "").trim().split(/\s+/)[0].replace(/-paid$/, "");
  const no = (why) => ({ ok: false, why, items: [] });
  const activeClaims = () => {
    const ids = new Set();
    for (const line of String(read(claimsFile) ?? "").split(/\r?\n/)) {
      const cells = line.split("|").map((cell) => cell.trim());
      const at = Date.parse(cells[2]);
      if (cells.length >= 3 && (!Number.isFinite(at) || now() - at < 2 * 3_600_000)) ids.add(cells[0]);
    }
    return ids;
  };
  const rows = (raw) => {
    const lines = String(raw).replace(/\r\n/g, "\n").split("\n");
    const cells = (line) => line.trim().replace(/^\||\|$/g, "").split(/(?<!\\)\|/).map((cell) => cell.trim());
    const start = lines.findIndex((line) => /^\|/.test(line) && cells(line).includes("ID") && cells(line).includes("Status") && (cells(line).includes("Role") || cells(line).includes("Owner role")));
    if (start < 0) return null;
    const header = cells(lines[start]).map((cell) => cell === "Owner role" ? "Role" : cell);
    const out = [];
    for (let i = start + 2; i < lines.length && /^\s*\|/.test(lines[i]); i++) {
      const values = cells(lines[i]);
      if (values.length !== header.length) continue; // malformed rows are not dispatchable
      out.push({ ...Object.fromEntries(header.map((key, j) => [key, values[j]])), text: lines[i] });
    }
    return out;
  };
  const selected = (value, path) => String(path ?? "").split(".").filter(Boolean).reduce((obj, key) => obj?.[key], value);
  const stable = (value) => {
    if (Array.isArray(value)) return value.map(stable);
    if (value && typeof value === "object") return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stable(value[key])]));
    return value;
  };
  const evaluate = (packet, used = new Set()) => {
    const fm = packet?.fm ?? {};
    if (!fm.ready) {
      // Legacy standing seat (no opt-in metadata): no free pass. Its trigger is
      // its own packet: an unseen or redefined packet launches, so migrating
      // crews keep running; a packet consumed by an empty run holds until it is
      // redefined. A DONE run re-arms it in complete(), so productive seats
      // never starve. One-offs never reach this gate (take() admits them).
      const key = `legacy|${packet?.role ?? ""}|${packet?.title ?? ""}`;
      const stamp = JSON.stringify(stable({ fm, body: packet?.body ?? "" }));
      if (seen.get(key) === stamp) return no("legacy seat ran empty: no changed trigger or eligible work since");
      return { ok: true, legacy: true, items: [{ id: packet?.title ?? packet?.role ?? "legacy", key, stamp }] };
    }
    const path = fm["ready-file"] && file(fm["ready-file"]);
    if (!path) return no("readiness source is missing (ready-file)");
    let items;
    if (fm.ready === "board") {
      const raw = read(path);
      if (raw == null) return no("readiness board is unreadable");
      const board = rows(raw);
      if (!board) return no("readiness board has no ID/Status/Role table");
      items = board.filter((row) => row.ID && ["READY", "TOP"].includes(row.Status) && baseRole(row.Role) === baseRole(fm["ready-role"] ?? packet.role)
        && (!fm["ready-match"] || row.text.includes(fm["ready-match"])))
        .map((row) => ({ id: row.ID, key: `board|${path}|${row.ID}`, stamp: row.text }));
    } else if (fm.ready === "watch") {
      // The center watch already holds new research while its unbuilt pile is
      // over cap. Apply that same stored-evidence rule before spending a worker.
      if (fm["ready-index-file"]) {
        const index = read(file(fm["ready-index-file"]));
        const cap = Number(fm["ready-pile-cap"] ?? 40);
        if (index == null || !Number.isFinite(cap) || cap < 0) return no("readiness research pile is unreadable or invalid");
        const pile = (String(index).match(/^- (?:CANDIDATE|ACCEPTED)\b/gm) ?? []).length;
        if (pile > cap) return no(`readiness research pile ${pile} exceeds cap ${cap}`);
      }
      const cfg = json(path);
      const state = fm["ready-watch-file"] && json(file(fm["ready-watch-file"]));
      const age = now() - Date.parse(state?.polledAt);
      if (!cfg?.corners || typeof cfg.corners !== "object" || Array.isArray(cfg.corners)
        || !state?.arms || typeof state.arms !== "object" || Array.isArray(state.arms)
        || !Number.isFinite(age) || age < 0 || age > 3 * 3_600_000) return no("readiness watch is missing or stale");
      items = [];
      for (const [id, corner] of Object.entries(cfg.corners)) {
        if (fm["ready-corner"] && fm["ready-corner"] !== id) continue;
        if (!corner || typeof corner !== "object" || !Array.isArray(corner.arms ?? [])) continue;
        const ack = Date.parse(corner.ackedAt ?? "1970-01-01T00:00:00Z");
        if (!Number.isFinite(ack)) continue;
        const moved = (corner.arms ?? []).filter((arm) => {
          if (!arm?.id) return false;
          const live = state.arms[`${id}/${arm.id}`];
          return live && !live.error && live.live !== undefined && arm.pin !== undefined && live.live !== arm.pin;
        }).map((arm) => [arm.id, arm.pin, state.arms[`${id}/${arm.id}`].live]);
        const fired = moved.length > 0 && now() - ack >= (corner.cooldown_hours ?? 4) * 3_600_000;
        const dig = !moved.length && corner.mode === "dig" && now() - ack >= (corner.dig_every_hours ?? 12) * 3_600_000;
        if (fired || dig) items.push({ id, key: `watch|${path}|${id}`, stamp: JSON.stringify([corner.ackedAt ?? null, moved, dig ? corner.dig_next ?? null : null]) });
      }
    } else if (fm.ready === "changed") {
      // Select semantic fields, not a generated report's polling timestamp.
      if (!fm["ready-key"]) return no("changed readiness needs a semantic ready-key");
      const value = selected(json(path), fm["ready-key"]);
      if (value == null) return no("readiness field is missing or unreadable");
      const key = `changed|${path}|${fm["ready-key"]}`;
      items = [{ id: fm["ready-key"], key, stamp: JSON.stringify(stable(value)) }];
    } else return no(`unknown readiness rule ${fm.ready}`);
    const claims = activeClaims();
    items = items.filter((item) => !claims.has(item.id) && !used.has(item.key) && seen.get(item.key) !== item.stamp);
    return items.length ? { ok: true, items } : no("no unclaimed ready work or changed evidence");
  };
  const complete = (item, text, failed) => {
    // A failure/cut releases admission; existing keeper backoff still applies.
    // DONE/NOOP consumes this evidence, so a cooldown expiring alone is not work.
    if (!item || failed || !/\bRESULT:\s*(?:DONE|NOOP)\b/i.test(String(text))) return false;
    if (String(item.key ?? "").startsWith("legacy|")) {
      // A legacy trigger is the seat's own packet: an empty (NOOP) run consumes
      // it, so the seat holds until redefined; a DONE run re-arms it, so a
      // productive seat stays eligible without a redefinition.
      seen.delete(item.key);
      if (/\bRESULT:\s*NOOP\b/i.test(String(text))) {
        seen.set(item.key, item.stamp);
        while (seen.size > 256) seen.delete(seen.keys().next().value);
      }
      return true;
    }
    seen.delete(item.key);
    seen.set(item.key, item.stamp);
    while (seen.size > 256) seen.delete(seen.keys().next().value);
    return true;
  };
  return { evaluate, complete, seen };
};

const makeKeeper = async ({ client, worktree, directory }, options) => {
  const opt = options ?? {};
  const cfg = { ...CFG, ...opt.cfg };
  const repos = opt.repos ?? REPOS;
  const here = repos[cfg.repo] ?? {};
  const now = opt.now ?? Date.now;
  const setTimer = opt.setTimer ?? setTimeout;
  const clearTimer = opt.clearTimer ?? clearTimeout;
  const sleep = opt.sleep ?? ((ms) => new Promise((r) => setTimeout(r, ms)));
  const every = opt.setInterval ?? setInterval;
  const proxyUp = opt.proxyUp ?? probePort;
  const startProxy = opt.startProxy ?? startProxyBat;
  const proxyMark = opt.proxyMark ?? join(tmpdir(), "loop-keeper-proxy-start.txt");
  const checksFile = opt.checks ?? CHECKS_FILE;
  const finishFile = opt.finish ?? FINISH_FILE;
  // A hot reload hands the old body's memory to this one: same sessions, helpers, queue and
  // waiting continues (see retire below).
  const ho = opt.handover ?? {};
  const state = ho.state ?? new Map(); // sprint sessions this keeper has decided on
  const busy = ho.busy ?? new Map(); // sessions OpenCode reports busy: { retry }
  const sprint = ho.sprint ?? new Map(); // session -> { v: is this repo's sprint session, at }
  const live = ho.live ?? { at: now(), question: null }; // last session event, open owner prompt
  const iso = () => new Date(now()).toISOString();
  const log = opt.log ?? ((msg) => {
    try {
      mkdirSync(dirname(cfg.log), { recursive: true });
      appendFileSync(cfg.log, `${iso()} ${msg}\n`);
    } catch { /* Logging must not restart a stopped run. */ }
  });
  const ago = (ms) => (ms == null || Number.isNaN(ms) ? "never" : ms < 90 * 60_000 ? `${Math.round(ms / 60_000)}m` : `${Math.round(ms / 3_600_000)}h`);

  // Bash written into a pwsh shell: rewrite exact equivalents, count them for the meter.
  const root = worktree ?? directory;
  // Only the CENTER keeper handles the say command (its worktree basename is center).
  const isCenterKeeper = () => basename(root ?? "").toLowerCase() === "center";
  const pwsh = /pwsh|powershell/i.test(opt.shell ?? shellOf(root));
  const drive = /^[a-z]:/i.test(root ?? "") ? root[0] : "c";
  const rootKey = root ? pathKey(root, drive) : null;
  const fixes = ho.fixes ?? { since: iso(), total: 0 };
  let fixLast = ho.fixLast ?? [];
  const background = opt.background ?? backgroundOn();
  const calls = ho.calls ?? { since: iso(), backgrounded: 0, todoFilled: 0, routed: 0, resultAsked: 0 };
  const roles = opt.roles ?? (root ? rolesIn(root) : new Set());
  const paidRoles = opt.paidRoles ?? (root ? paidIn(root) : new Set());
  // The claims file lives in the queue folder (qsub), never at the repo root. A read of the root guess goes to the real file.
  const claimsPath = () => qsub("claims.txt").replace(/\\/g, "/");
  const isRootClaims = (p) => {
    if (typeof p !== "string" || !qdir || !root) return false;
    const n = p.trim().replace(/\\/g, "/").replace(/^\.\//, "").toLowerCase();
    const r = String(root).replace(/\\/g, "/").replace(/\/+$/, "").toLowerCase();
    return (n === "claims.txt" || n === `${r}/claims.txt`) && !existsSync(join(root, "claims.txt"));
  };
  // An answer that says "missing" for a reason the agent cannot see gets one line that says where to look.
  const navHint = (input, output) => {
    const out = output?.output;
    if (typeof out !== "string" || out.includes("[loop-keeper]")) return;
    const args = input.args ?? {};
    const asked = JSON.stringify(args).replace(/\\\\/g, "/");
    const empty = input.tool === "glob" && /^No files found/.test(out.trim());
    const missing = input.tool === "bash" && NOT_FOUND.test(out);
    let hint = "";
    if (qdir && /claims\.txt/i.test(asked) && (empty || missing) && !asked.toLowerCase().includes(claimsPath().toLowerCase())) {
      hint = `[loop-keeper] this repo's claims file is ${claimsPath()} (the queue folder, never the repo root; it does not exist while no helper holds a claim).`;
    } else if (empty) hint = GLOB_BLIND_HINT;
    if (!hint) return;
    output.output = `${out}\n\n${hint}`;
    calls.navHinted = (calls.navHinted ?? 0) + 1;
  };
  const shellFix = (command, workdir) => {
    const hit = [];
    let out = command;
    const cd = out.match(CD_FIRST);
    if (rootKey && cd && pathKey(cd[1], drive) === rootKey && (!workdir || pathKey(workdir, drive) === rootKey)) {
      out = out.slice(cd[0].length);
      hit.push("cd");
    }
    out = out.replace(QUOTED_OR_PLAIN, (m, quoted, plain) => {
      if (quoted !== undefined) return quoted;
      let s = plain;
      for (const [name, re, to] of SHELL_FIXES) s = s.replace(re, (...a) => { hit.push(name); return to(...a); });
      return s;
    });
    return { out, hit };
  };

  // The status file: last decision + live snapshot. It survives restarts, so the
  // keeper remembers its sprint session and never replays an old popper command.
  let status = {};
  try { status = JSON.parse(read(here.state) ?? "{}") ?? {}; } catch { status = {}; }
  // Sprint sessions replaced by NEW: never driven again, also after a restart.
  const retired = new Set(Array.isArray(status.retired) ? status.retired : []);
  // A sprint command names this repo's current handoff file, so an old-protocol
  // session (the factory's /go before the rename) is never driven again.
  const handoffPath = cfg.handoffName.replace(/`/g, "");
  const isCommand = (m) => isOwner(m) && textOf(m).includes(cfg.marker) && textOf(m).includes(handoffPath);
  const write = (patch) => {
    status = { ...status, repo: cfg.repo, supportedCommands: SUPPORTED_COMMANDS, ...patch };
    if (!here.state) return;
    try {
      mkdirSync(dirname(here.state), { recursive: true });
      writeFileSync(here.state, `${JSON.stringify(status, null, 1)}\n`);
    } catch { /* Status must not restart a stopped run. */ }
  };
  // loaded = this repo's config and agents; code = this file (a hot reload loads it; see the shell).
  write({ ...(ho.loadedAt ? {} : { loaded: iso() }), code: CODE_AT, reload: "hot" });

  // One keeper per repo (the shell retires the old one). inflight counts the calls into this
  // body still running: a hot reload swaps bodies only when none is.
  let gone = false;
  let inflight = 0;
  const intervals = [];
  const track = (fn) => async (...a) => { inflight += 1; try { return await fn(...a); } finally { inflight -= 1; } };
  // Config, agent and command changes load between rounds: only this repo's OpenCode
  // instance reloads, right before the next prompt, when no session of it is working
  // (owner 2026-09-26: never pause all 3 repos for a restart; checked in 1.18.29).
  const loadedAt = ho.loadedAt ?? now();
  const reloadFiles = () => {
    const home = process.env.USERPROFILE ?? process.env.HOME ?? "";
    const out = [`${root}/opencode.jsonc`, `${root}/opencode.json`, `${home}/.config/opencode/opencode.jsonc`, `${home}/.config/opencode/opencode.json`];
    for (const d of ["agents", "agent", "commands", "command"]) {
      try { for (const n of readdirSync(join(root, ".opencode", d))) out.push(join(root, ".opencode", d, n)); } catch { /* no such folder */ }
    }
    return out.filter((f) => (mtime(f) ?? 0) > loadedAt);
  };
  const reload = async () => {
    try {
      if (typeof client.instance?.dispose !== "function" || !root) return;
      const changed = reloadFiles();
      if (!changed.length) return;
      const working = Object.values((await client.session.status())?.data ?? {}).some((s) => s?.type && s.type !== "idle");
      if (working) return;
      log(`reloading this repo's config and agents (${changed.length} changed: ${changed.slice(0, 3).map((f) => f.split(/[\\/]/).pop()).join(", ")})`);
      await client.instance.dispose();
    } catch (e) { log(`reload failed: ${e?.message ?? e}`); }
  };
  // The session's own turn, and its child sessions (helpers) that are working now.
  const turnOf = async (id) => (await client.session.status())?.data?.[id]?.type ?? "idle";
  const helpersRunning = async (id) => {
    try {
      const now3 = (await client.session.status())?.data ?? {};
      const kids = (await client.session.children({ path: { id } }))?.data ?? [];
      return kids.filter((k) => k?.id && now3[k.id]?.type && now3[k.id].type !== "idle").length;
    } catch { return 0; }
  };

  const repoStatus = (p) => {
    if (existsSync(p.halt)) return { status: "halted" };
    const handoff = read(p.handoff);
    if (handoff === null) return { status: "missing handoff" };
    const headline = handoff.split(/\r?\n/, 1)[0].slice(0, 90);
    if (STOP_LINE.test(handoff)) return { status: "terminal handoff", headline };
    const header = handoff.split(/\r?\n/).slice(0, 3).join(" ");
    if (/\b(?:PAUSED|HALTED|STOPPED)\b/i.test(header)) return { status: "paused", headline };
    const lock = read(p.lock)?.trim();
    const token = lock?.match(/^(?:orchestrator|lead)#[0-9a-f]{4}\b/i)?.[0]?.toLowerCase();
    if (!token) return { status: "no valid lock", headline };
    const lockAt = mtime(p.lock);
    if (lockAt === null) return { status: "missing lock", headline };
    const named = header.match(/\b(?:orchestrator|lead)#[0-9a-f]{4}\b/i)?.[0]?.toLowerCase();
    const shortToken = header.match(/\btoken\s+([0-9a-f]{4})\b/i)?.[1]?.toLowerCase();
    const changed = (named && named !== token) || (shortToken && !token.endsWith(`#${shortToken}`));
    if (now() - lockAt > MAX_LOCK_AGE_MS) {
      // owned: the handoff names this token, so the run that holds it wrote the handoff.
      return { status: `stale lock (${ago(now() - lockAt)})`, headline, token, lockAt, stale: true, owned: !changed && !!(named || shortToken) };
    }
    if (changed) return { status: "lock changed", headline, token, named: named ?? `#${shortToken}` };
    return { status: "active", token, headline, lockAt };
  };
  // This repo's lock as the loop sees it: a stale lock that is still this loop's (its handoff
  // names the token, or this keeper saw the token on this session) is a refresh it forgot,
  // not a dead run; the continue asks for the refresh.
  const localStatus = (st) => {
    const local = repoStatus(here);
    return local.stale && (local.owned || (st?.token && st.token === local.token)) ? { ...local, status: "active" } : local;
  };
  // A stop for a missing, invalid or stale lock (or a lifted halt) ends once the repo is active again, for the
  // current sprint session only and never onto another run's token.
  const canHeal = (id, st) => {
    if (!st?.stopped || !LOCK_STOP.test(st.why ?? "") || id !== status.session) return false;
    const local = localStatus(st);
    return local.status === "active" && (!st.token || st.token === local.token);
  };
  const keeperOf = (p) => { try { return JSON.parse(read(p.state) ?? "null"); } catch { return null; } };
  const peerLine = (name) => {
    const p = repos[name];
    const { status: s } = repoStatus(p);
    const k = keeperOf(p);
    const keeper = k?.decision ? `, keeper ${k.decision}${k.reason ? `: ${clip(k.reason, 50)}` : ""} ${ago(now() - Date.parse(k.at))} ago` : "";
    return `${name} ${s}${keeper}`;
  };
  const snapshot = () => Object.keys(repos).map(peerLine).join(" | ");
  const record = (id, decision, reason, st) => {
    if (retired.has(id)) return;
    snapDirty = true; // a recorded decision: the next beat censuses
    if (st) st.recorded = decision;
    write({
      session: id, at: iso(), decision, reason, continues: st?.continues ?? 0, retries: st?.retries ?? 0,
      resume: decision === "stopped" ? `say GO in the ${cfg.repo} /sprint session, press GO in the popper, or run /sprint there` : undefined,
    });
  };
  const stop = (id, st, reason) => {
    const again = st.stopped && st.why;
    st.stopped = true;
    if (st.timer) clearTimer(st.timer);
    st.timer = null;
    if (!again) st.why = reason;
    log(`${id} stop: ${reason}; ${snapshot()}`);
    if (!again || st.recorded !== "stopped") record(id, "stopped", st.why, st);
  };
  const reset = (st, consent) => Object.assign(st, {
    consent, token: null, stopped: false, why: null, errorBeforeFirst: false,
    toolless: 0, stall: 0, progress: null, lastReply: null, continues: 0, retries: 0,
  });
  const fresh = () => reset({ timer: null, busy: false, sending: false }, null);
  const inbox = (p) => (read(p.inbox) ?? "").split(/\r?\n/).filter((l) => /^\s*- \[ \] /.test(l)).length;
  const healProxy = async (id) => {
    if (!cfg.proxyStart) return;
    if (now() - (Number(read(proxyMark)) || 0) < PROXY_RESTART_MS) return;
    try { writeFileSync(proxyMark, String(now())); } catch { return; }
    try { log(`${id} proxy :${cfg.proxyPort} down: ${await startProxy(cfg.proxyStart)}`); } catch (e) { log(`${id} proxy start failed: ${e?.message ?? e}`); }
  };
  // Knobs changed since the version the loop was last told: name them (at most 6).
  const knobsNews = () => {
    if (!here.knobs) return null;
    let doc;
    try { doc = JSON.parse(read(here.knobs) ?? "null"); } catch { return null; }
    if (!doc?.updated || doc.updated === status.knobsSeen) return null;
    const seen = Date.parse(status.knobsSeen ?? "") || 0;
    const news = (Array.isArray(doc.history) ? doc.history : []).filter((h) => (Date.parse(h?.at) || 0) > seen).slice(-6);
    const list = news.map((h) => `${h.knob} ${h.from} -> ${h.to} (${h.by ?? "?"})`).join(", ");
    const what = list ? `changed: ${list}` : "file updated";
    return { updated: doc.updated, text: `knobs ${what}: re-read ${here.knobs} now and apply it from this ${cfg.next}; write one "Knobs:" line in the handoff.` };
  };
  const knobValue = (name) => { try { return JSON.parse(read(here.knobs) ?? "null")?.knobs?.[name]?.value ?? null; } catch { return null; } };
  // Ralph pattern: knob `fresh_ctx_k` (thousands of input tokens, default 120, 0 = off).
  const freshCtxK = () => {
    const v = knobValue("fresh_ctx_k");
    if (v == null || v === "") return FRESH_CTX_DEFAULT_K;
    const n = Number(v);
    if (!Number.isFinite(n) || n < 0) return FRESH_CTX_DEFAULT_K;
    return n;
  };
  // Session context of the lead session: the last assistant message's
  // total tokens (what `empire.mjs status` prints as ctx), falling back to
  // its input count when the total field is missing. The last-turn input
  // alone stays small after a compaction while the total keeps growing
  // (factory 2026-10-02: ctx 290k total, last-turn input under 120k, no
  // renewal before the 300k compaction), so the threshold reads the total.
  const inputTokensOf = (m) => {
    const t = m?.info?.tokens;
    if (!t) return 0;
    const total = Number(t.total);
    if (Number.isFinite(total) && total > 0) return total;
    if (Number.isFinite(Number(t.input))) return Number(t.input);
    return tokensOf(m);
  };
  const lastInputTokens = (msgs) => {
    const last = msgs.filter((m) => m?.info?.role === "assistant").at(-1);
    return last ? inputTokensOf(last) : 0;
  };
  // The last fresh-context renewal, in memory (hot-reload handover) and on disk
  // (the status file survives a restart), so the 30 min window holds either way.
  let freshCtxAt = ho.freshCtxAt ?? Date.parse(status.freshCtxAt ?? "") ?? 0;
  if (!Number.isFinite(freshCtxAt)) freshCtxAt = 0;
  // Pure check: due when the session context passes fresh_ctx_k*1000 and no
  // fresh session started inside the window. 0 = off.
  const freshCtxDue = (msgs) => {
    const k = freshCtxK();
    if (!k || k <= 0) return { due: false, why: `fresh_ctx_k=${k ?? 0} (off)` };
    const input = lastInputTokens(msgs);
    const threshold = k * 1000;
    if (!(input > threshold)) return { due: false, why: `session context ${input} <= ${threshold}`, input, threshold, k };
    if (now() - freshCtxAt < FRESH_CTX_MIN_MS)
      return { due: false, why: `fresh session ${ago(now() - freshCtxAt)} ago (once per 30m)`, input, threshold, k };
    return { due: true, why: `session context ${input} > ${threshold} (fresh_ctx_k=${k})`, input, threshold, k };
  };
  // Fresh-context renewal: the same path as `new` (retire, then /sprint takeover,
  // which resumes from the handoff file), instead of the continue.
  const freshCtxRenew = async (id, input, threshold, k) => {
    const answer = await renew(id);
    freshCtxAt = now();
    write({ freshCtxAt: iso() });
    log(`${id} fresh context: session context ${input} > ${threshold} (fresh_ctx_k=${k}); ${answer}`);
    return answer;
  };
  // Two modes (owner 2026-09-29): free only, or hybrid: with the knob paid_mode at 1 a role that has a -paid twin runs on the Go subscription.
  const paidOf = (role) => (!role || /-paid$/.test(role) || Number(knobValue("paid_mode")) !== 1 || !paidRoles.has(String(role).toLowerCase()) || (paidRoles.get?.(String(role).toLowerCase()) && (mtime(paidRoles.get(String(role).toLowerCase())) ?? 0) > loadedAt) ? role : `${role}-paid`);
  // Knob `dispatch`: "foreground" (the default, owner 2026-09-28) or "queue" (see the queue section).
  const foreground = () => String(knobValue("dispatch") ?? "foreground").trim().toLowerCase() !== "queue";
  // The /sprint command changed since the loop was last told. A running session got the command
  // once, at its start, and works from memory and compaction summaries after that, so center's
  // upgrades to the file never reached it (2026-09-27: 8 applied, 0 read). Told once per change.
  const commandNews = () => {
    const at = here.command ? Math.floor(mtime(here.command) ?? 0) : 0; // whole ms, as the ISO mark keeps
    if (!at || at <= (Date.parse(status.commandSeen ?? "") || 0)) return null;
    return { at: new Date(at).toISOString(), text: `your /sprint command changed ${ago(now() - at)} ago (center's upgrades land there): re-read ${here.command} in full now and follow it from this ${cfg.next}; it wins over what you remember of it.` };
  };
  // Facts the loop acts on, in every continue and every GO: what runs now, what on disk aged.
  // An idle loop with no helper working is the loop's own bottleneck (2026-09-26: 0.7-1.5 of
  // 15-20 helpers busy on average); factory 2026-09-27 held 5 h "at 14/15" for a helper of
  // the round before, which had landed: nothing it waits for can land when none works.
  // This repo's failing checks, from center's last run. Every /sprint says a FAIL is the loop's
  // first packet; the loops read past it for hours (engine 2026-09-27: 13 queued packets, none on
  // its failing spatial focus; the popper called Maxim instead). So every continue and GO
  // carries it until the check passes.
  const checkFails = () => {
    let doc;
    try { doc = JSON.parse(read(checksFile) ?? "null"); } catch { return null; }
    const mine = doc?.repos?.[cfg.repo];
    const at = Date.parse(mine?.at ?? "");
    if (!at || now() - at > CHECKS_FRESH_MS) return null;
    const lines = (mine.checks ?? []).filter((c) => c && !c.ok).flatMap((c) =>
      (c.bad?.length ? c.bad : c.tail ?? []).filter((l) => /\bFAIL|\bBLOCKING\b/.test(l) && !/^\s*RESULT\b/.test(l)).map((l) => `${c.name}: ${clip(l, 200)}`));
    if (!lines.length) return null;
    // Up to 10 lines: engine alone FAILs 10 (7 starved sections, 3 stuck rows; 2026-09-27).
    return `your checks FAIL (center ran them ${ago(now() - at)} ago): ${lines.slice(0, 10).join(" | ")}${lines.length > 10 ? ` | +${lines.length - 10} more` : ""}. ` +
      `A FAIL is this ${cfg.next}'s first packet (your /sprint): ${foreground() ? "write the packet that clears it to the ready queue so it tops the next batch" : "queue or launch the packets that clear it before other work"}, and name in the handoff which packet clears which.`;
  };
  // The finish line (owner 2026-10-03: every round aims at its repo's finish line): every continue and GO
  // names this repo's lowest open bar from center's cache. No file, an old file or no entry for this
  // repo: no fact, never an error.
  const goalFact = () => {
    try {
      const doc = JSON.parse(read(finishFile) ?? "null");
      const mine = doc?.repos?.[cfg.repo];
      const at = Date.parse(mine?.at ?? doc?.at ?? "");
      if (!mine?.open?.id || !mine.open.text || !Number.isInteger(mine.met) || !Number.isInteger(mine.total) || !Number.isFinite(at) || now() - at > FINISH_FRESH_MS) return null;
      return `Lowest open finish bar: ${clip(mine.open.id, 12)} ${clip(mine.open.text, 220)} (${mine.met} of ${mine.total} met). This batch must move it, or say why not in the handoff.`;
    } catch { return null; }
  };
  const stateNotes = (busyNow, local) => {
    const width = knobValue("width");
    const handoffAge = now() - (mtime(here.handoff) ?? now());
    const fg = foreground();
    return {
      checks: checkFails(),
      batch: fg ? batchNote() : null,
      goal: goalFact(),
      idle: !fg && width && busyNow === 0 ? `no helper is working and your width is ${width}: every Task you launched has returned, so nothing more will land; collect what landed and dispatch the ready list up to it this ${cfg.next} (writers go to the background by themselves; each result wakes you).` : null,
      // A loop paused by its halt file releases its lock (forge 2026-09-27): the GO that resumes it
      // must say so, or its first idle stops it again on "missing lock".
      lock: local?.stale ? `your lock is ${ago(now() - local.lockAt)} old: rewrite ${here.lock} first (same token, fresh time); a lock over ${MAX_LOCK_AGE_MS / 3_600_000} h reads as a dead run.`
        : /^(?:missing lock|no valid lock)$/.test(local?.status ?? "") ? `there is no valid lock at ${here.lock}: take it first (one line \`<your role>#<4 hex> since <UTC>\`, the token also in your handoff's first lines); the keeper stops a loop without one.`
        : local?.status === "lock changed" ? `the lock at ${here.lock} holds ${local.token} but your handoff's first lines name ${local.named}: if this run wrote that lock, put its token in the handoff's first lines now; if another run holds it, end with the LOOP STOP line.` : null,
      handoff: handoffAge > STALE_HANDOFF_MS ? `the handoff is ${ago(handoffAge)} old: rewrite it before the next ${cfg.next}, a compaction resumes from it.` : null,
      // No standing team yet: the width fills only as fast as this loop plans (2026-09-27: 0-7 of 20).
      team: !qdir || !width || queueCount("standing") ? null
        : fg ? `you have no standing seats: write one packet per role of your sprint team to ${qsub("standing")}/<role>-<area>.md (front matter role:, title:, copies: N for writers, cpu: heavy for builds; the body names the area and how to pick its next open item). Every batch lists them in fair turns up to your width of ${width}.`
        : `you have no standing team: write one packet per role of your sprint team to ${qsub("standing")}/<role>-<area>.md (front matter role:, title:, copies: N for writers; the body names the area and how to pick its next open item). The keeper keeps them all running, 24/7, up to your width of ${width}, and hands every result back; you judge, merge and re-plan from them.`,
    };
  };
  const continueText = (st, d, busyNow) => {
    const local = d.local ?? localStatus(st);
    const peers = Object.keys(repos).filter((n) => n !== cfg.repo).map(peerLine).join("; ");
    const notes = [];
    const knobs = knobsNews();
    st.knobsPending = knobs?.updated ?? null;
    if (knobs) notes.push(knobs.text);
    const command = commandNews();
    st.commandPending = command?.at ?? null;
    if (command) notes.push(command.text);
    const facts = stateNotes(busyNow, local);
    if (facts.checks) notes.push(facts.checks);
    if (facts.batch) notes.push(facts.batch);
    if (facts.goal) notes.push(facts.goal);
    if (facts.idle) notes.push(facts.idle);
    if (facts.team) notes.push(facts.team);
    if (facts.lock) notes.push(facts.lock);
    if (d.retry) notes.push(`the last turn failed (${d.retry}), retry ${st.retries} of ${BACKOFF_MS.length}: check what it left half done first.`);
    if (st.toolless > 0) notes.push(`${st.toolless} of ${MAX_TOOLLESS} turns in a row without a tool call: do real work or write the LOOP STOP line.`);
    if (st.stall > 0) notes.push(`${st.stall} of ${MAX_STALL} continues without a handoff or lock update: rewrite the handoff and refresh the lock this turn.`);
    if (facts.handoff) notes.push(facts.handoff);
    return `${KEEPER} Continue #${st.continues}: your last turn ended without a stop reason. ` +
      `Here: lock ${local.token ?? "?"}, handoff ${ago(now() - (mtime(here.handoff) ?? now()))} old, inbox ${inbox(here)} open. ` +
      `Other sprints (${cfg.peers ?? "read-only, never touch them"}): ${peers}.\n` +
      (notes.length ? `Keeper notes: ${notes.join(" ")}\n` : "") +
      `Re-read ${cfg.handoffName}, the inbox and your lock. If ${cfg.haltName}, a terminal blocker or an owner stop applies, ` +
      `write \`LOOP STOP: <reason>\` and end. Otherwise run the next ${cfg.next}. Do not report success without its checks.`;
  };
  // Decide from the session and the disk. first = at idle (counts turns), else right before sending.
  const inspect = async (id, st, first) => {
    if (retired.has(id)) return { ignore: true };
    const info = (await client.session.get({ path: { id } }))?.data;
    if (!info || info.parentID) return { ignore: true };
    const msgs = (await client.session.messages({ path: { id } }))?.data;
    if (!Array.isArray(msgs)) return { retry: "session messages unavailable" };
    const command = msgs.findLast(isCommand);
    if (!command) return { ignore: true };
    sprint.set(id, { v: true, at: now() });
    const owner = msgs.findLast(isOwner);
    const turn = msgs.findLast((m) => isUser(m) && !hasCompaction(m));
    const replies = msgs.slice(msgs.indexOf(turn) + 1).filter((m) => m.info?.role === "assistant" && !m.info?.summary);
    const reply = replies.at(-1);
    const keys = {
      consent: keyOf(owner, msgs), turnKey: keyOf(turn, msgs), replyKey: keyOf(reply, msgs),
      lastId: msgs.length ? keyOf(msgs.at(-1), msgs) : null,
      users: new Set(msgs.filter(isUser).map((m) => keyOf(m, msgs))),
      // The continue runs as the loop's own agent and model, not the default agent.
      via: viaOf(owner), title: info.title,
      said: reply ? clip(textOf(reply).slice(-400), 240) : null,
    };
    const out = (x) => ({ ...keys, ...x });
    const intent = owner === command ? "command" : intentOf(textOf(owner));
    if (st.consent !== keys.consent) {
      if (!first) return out({ reason: "the owner spoke while the continue waited" });
      if (st.errorBeforeFirst) {
        st.consent = keys.consent;
        st.errorBeforeFirst = false;
        return out({ reason: "the session failed before the keeper saw it idle" });
      }
      reset(st, keys.consent);
    }
    if (canHeal(id, st)) {
      log(`${id} ${st.why} is over: the stop is lifted`);
      Object.assign(st, { stopped: false, why: null, retries: 0 });
    }
    if (st.stopped) return out({ reason: `still stopped (${st.why ?? "stopped"}); say GO or run /sprint to resume` });
    if (intent === "stop") return out({ reason: `the owner said stop ("${clip(textOf(owner))}")` });
    if (intent === "chat") return out({ reason: `the owner is chatting ("${clip(textOf(owner))}"); say GO to resume` });
    if (ONE_SHOT.test(textOf(command))) return out({ reason: "one-round command; run /sprint without it to loop" });
    const local = localStatus(st);
    const changed = local.status === "lock changed";
    if (local.status !== "active") return out({ reason: changed ? `lock changed (the lock holds ${local.token}, the handoff names ${local.named})` : local.status });
    if (st.token && st.token !== local.token) return out({ reason: "the lock belongs to another run" });
    const error = msgs.findLast((m) => m.info?.role === "assistant")?.info?.error;
    const overflow = !!error && isOverflow(error, msgs);
    if (error && !overflow && !isTransient(error)) return out({ reason: describe(error) });
    if (cfg.proxyPort && !(await proxyUp(cfg.proxyPort))) {
      await healProxy(id);
      return out({ local, retry: `retry proxy :${cfg.proxyPort} is down` });
    }
    if (overflow) {
      // One compaction per failed reply; still failing after it stops the loop.
      if (st.compacted === keys.replyKey) return out({ reason: `${describe(error)}; still failing after a compaction` });
      return out({ local, compact: `context overflow (${describe(error)})` });
    }
    if (error) return out({ local, retry: describe(error), error: true });
    if (!reply) return out({ reason: "no completed assistant reply" });
    const stopLine = replies.map(textOf).join("\n").match(STOP_LINE);
    if (stopLine) return out({ reason: stopLine[0].trim() });
    // A turn a background helper's result started (a synthetic message) is not a continue
    // and never counts toward the tool-less or stall stops.
    if (first && keys.replyKey !== st.lastReply) {
      st.lastReply = keys.replyKey;
      st.retries = 0;
      if (!isSystemTurn(turn) && !textOf(turn).startsWith(QUEUE_RESULTS)) {
        const usedTools = replies.some((m) => (m.parts ?? []).some((p) => p.type === "tool"));
        st.toolless = usedTools ? 0 : st.toolless + 1;
        const progress = `${mtime(here.handoff)}|${mtime(here.lock)}`;
        st.stall = st.continues > 0 && progress === st.progress ? st.stall + 1 : 0;
        st.progress = progress;
      }
    }
    if (st.toolless >= MAX_TOOLLESS) return out({ reason: `${MAX_TOOLLESS} turns in a row without a tool call` });
    if (st.stall >= MAX_STALL) return out({ reason: `${MAX_STALL} continues in a row without a handoff or lock update` });
    return out({ local });
  };

  const wait = (id, st, d, delay, decision, reason) => {
    st.pending = d;
    st.dueAt = now() + delay; // a hot reload re-arms it on the same schedule
    log(`${id} ${decision}: ${reason}; ${snapshot()}`);
    record(id, decision, reason, st);
    st.timer = setTimer(() => fire(id, st, d), delay);
    st.timer?.unref?.();
  };
  const plan = (id, st, d) => {
    if (d.compact) return wait(id, st, d, GAP_MS, "compacting", `${d.compact}; compacting in ${GAP_MS / 1000}s, then continue #${st.continues + 1}`);
    // Foreground with every seat resting and nothing ready: a continue now would be an empty round
    // (center 2026-09-28, C-81: "he responds every second"); it waits for the first seat's rest to end.
    if (!d.retry && foreground()) {
      const p = batchPlan();
      if (p && !p.list.length && p.held.readiness.length) return wait(id, st, d, 60_000, "waiting", "no eligible work: recheck sources in 1m without launching a worker");
      const ends = p && !p.list.length && p.held.resting.length ? Math.min(...p.held.resting.map((n) => standingRest.get(`${n}.md`) ?? 0)) : 0;
      const delay = ends ? Math.min(30 * 60_000, Math.max(2 * 60_000, ends - now())) : 0;
      if (delay) return wait(id, st, d, delay, "waiting", `every seat rests and nothing is ready: continue #${st.continues + 1} in ${Math.round(delay / 60_000)}m, when the first seat's rest ends`);
    }
    if (!d.retry) return wait(id, st, d, GAP_MS, "waiting", `continue #${st.continues + 1} in ${GAP_MS / 1000}s`);
    if (st.retries >= BACKOFF_MS.length) return stop(id, st, `${d.retry}; gave up after ${BACKOFF_MS.length} retries`);
    const delay = BACKOFF_MS[st.retries];
    st.retries += 1;
    return wait(id, st, d, delay, "retrying", `${d.retry}; retry ${st.retries} of ${BACKOFF_MS.length} in ${Math.round(delay / 60_000)}m`);
  };
  const send = async (id, st, d) => {
    await reload();
    st.continues += 1;
    st.sending = true;
    try {
      const busyNow = await helpersRunning(id);
      await client.session.promptAsync({ path: { id }, body: bodyFor(d.via, continueText(st, d, busyNow)) });
    } finally { st.sending = false; }
    if (st.knobsPending) write({ knobsSeen: st.knobsPending, knobsSeenAt: iso() });
    if (st.commandPending) write({ commandSeen: st.commandPending });
    log(`${id} continued #${st.continues} as ${d.via.agent ?? "default agent"}${d.retry ? ` after: ${d.retry}` : ""}`);
    record(id, "continued", `continue #${st.continues}${d.retry ? ` (retry after ${d.retry})` : ""}`, st);
  };
  // Compact on the loop's own model, then decide again: the summary is now the last reply.
  const compact = async (id, st, d) => {
    st.compacted = d.replyKey;
    log(`${id} compacting: ${d.compact}`);
    record(id, "compacting", d.compact, st);
    const { providerID, modelID } = d.via.model ?? {};
    await client.session.summarize({ path: { id }, body: { ...(providerID && modelID ? { providerID, modelID } : {}), auto: false } });
    log(`${id} compacted`);
    return inspect(id, st, false);
  };
  const fire = track(async (id, st, d) => {
    st.timer = null;
    if (gone) return;
    try {
      let now2 = await inspect(id, st, false);
      // A new turn during the wait (a helper result, same owner word): not a stop, and it may
      // still be running; its idle, or the next beat, decides.
      if (d.consent && !now2.ignore && now2.consent === d.consent && (now2.turnKey !== d.turnKey || now2.replyKey !== d.replyKey)) {
        st.recheck = true;
        return log(`${id} a new turn came during the wait; the next idle decides`);
      }
      if (now2.ignore || now2.reason) return stop(id, st, now2.reason ?? "no longer a sprint session");
      if (d.consent && now2.consent !== d.consent) return stop(id, st, "the session changed during the wait");
      if (now2.compact) {
        // sending holds the idle handler off until the continue below is out.
        st.sending = true;
        try { now2 = await compact(id, st, now2); } finally { st.sending = false; }
        if (now2.ignore || now2.reason) return stop(id, st, now2.reason ?? "no longer a sprint session");
      }
      // Proxy still down, or an error landed during a plain wait: back off again (a review stays one).
      if (now2.retry && (!now2.error || !d.retry)) return plan(id, st, now2);
      if (!now2.retry && !now2.why && foreground()) {
        const p = batchPlan();
        if (p && !p.list.length && p.held.readiness.length) return plan(id, st, now2);
      }
      // Ralph pattern: a stale-fat session resumes from the handoff in a fresh
      // session instead of continuing it. Only a plain continue is replaced: a
      // stop, retry or compaction keeps its own path.
      if (!now2.retry && !now2.compact) {
        try {
          const msgs = (await client.session.messages({ path: { id } }))?.data ?? [];
          const fresh = freshCtxDue(msgs);
          if (fresh.due) return freshCtxRenew(id, fresh.input, fresh.threshold, fresh.k);
        } catch { /* a failed read continues as usual */ }
      }
      // Stale-continue guard (bb steerTurn expectedTurnId shape, 2026-10-03):
      // the wait is over, but something else may have moved the session since
      // this continue was planned (a helper result, a retried message, a second
      // keeper). Re-read the last message id right before sending; a newer
      // message means this continue is superseded: skip it, never double-send.
      try {
        const cur = (await client.session.messages({ path: { id } }))?.data ?? [];
        const curLast = cur.length ? keyOf(cur.at(-1), cur) : null;
        if (now2.lastId && curLast && curLast !== now2.lastId) {
          st.recheck = true;
          log(`${id} stale-continue skipped: a newer message (${curLast}) appeared after ${now2.lastId}; no continue sent`);
          return record(id, "waiting", `stale-continue skipped: a newer message appeared after ${now2.lastId}`, st);
        }
      } catch { /* a failed re-read sends as planned */ }
      await send(id, st, now2);
    } catch (e) {
      if (!keeperGlitch(e)) return stop(id, st, `continue failed: ${e?.message ?? e}`);
      st.recheck = true; // the next beat decides again
      log(`${id} continue failed on a connection glitch (${e?.message ?? e}); the next beat retries`);
    }
  });
  // ---- The queue (center C-36, 2026-09-27; since 2026-09-28 the keeper starts packets only with the
  // knob `dispatch` "queue", else the loop starts them in foreground batches, see below; the folders,
  // records, rests and chain serve both). All 3 loops ran 0.8-2.3 of 20 helpers busy: the
  // LLM orchestrator was the queue, and every wave drained to its slowest helper. The loop now
  // writes ready packets to <state dir>/queue/ready/<id>.md (front matter `role:` and `title:`,
  // then the packet) and the keeper keeps the width full from them: each starts as a child
  // session of the sprint session with that role, and each finished one comes back as a
  // `<task>` block at the loop's next idle. The loop plans and judges; code dispatches.
  const qdir = opt.queueDir ?? (here.state ? join(dirname(here.state), "queue") : null);
  const qsub = (s) => join(qdir, s);
  const readySeen = ho.readySeen ?? new Map(Array.isArray(status.readinessSeen) ? status.readinessSeen : []);
  const readyPending = ho.readyPending ?? new Set();
  const seatReadiness = createSeatReadiness({ read, file: (p) => /^(?:[A-Za-z]:[\\/]|\/)/.test(p) ? p : join(root, p), claimsFile: qsub("claims.txt"), now, seen: readySeen });
  const readyBusy = () => new Set([...readyPending, ...[...fgJobs.values(), ...queueRunning.values()].map((j) => j.readiness?.key).filter(Boolean)]);
  const queueRunning = ho.queueRunning ?? new Map(); // child session -> { id, role, title, started }
  const queueDone = ho.queueDone ?? []; // finished queue helpers waiting for the loop's next idle
  // Write-on-decision (lean-2): the per-minute beat used to re-read the sprint
  // session (get/todo/children/status), re-list the queue (ready/running/done/
  // failed/standing), re-plan the foreground batch and rewrite the status file
  // every 60 s even when nothing happened. Now the beat only tends the queue
  // (collect/stuck-abort/launch/deliver still run: they act) and writes a cheap
  // heartbeat ({ alive, busy } + counters); the census above runs only when a
  // decision happened since the last one (decide/record, a dispatch, a result,
  // a popper command, a queue movement). An idle loop costs one tiny JSON
  // write a minute and no session API calls; a decision is still visible at
  // most one beat later, and the loop's own continue always carries a fresh
  // batch via batchNote. Not handed over on hot reload: a reload censuses once.
  let snapDirty = true;
  const standingRest = ho.standingRest ?? new Map(); // standing packet -> resting until
  // Seats run in fair turns (least recently run first); a seat with `priority: N` in its front matter goes ahead of lower ones.
  // Engine 2026-09-29: the FOCUS seat (spatial) got 0 of 121 helpers in 6 h because a dozen heavy seats shared 3 heavy places.
  const seatPriority = (f) => Number(parsePacket(read(join(qsub("standing"), f)))?.fm?.priority) || 0;
  const seatOrder = (a, b) => seatPriority(b) - seatPriority(a) || (standingLast.get(a) ?? 0) - (standingLast.get(b) ?? 0);
  const standingNoops = ho.standingNoops ?? new Map(); // standing packet -> NOOP or BLOCKED runs in a row (each doubles the rest, 30 min up to 2 h)
  // A plain Task the lead sends again after it ended NOOP (factory 2026-09-29: "re-check the vision" every 3 minutes, r275 to r278, each NOOP).
  const adhocRest = ho.adhocRest ?? new Map(); // role|title|prompt head -> { at, noops, until }
  const adhocCalls = new Map(); // callID -> key of a plain Task in flight
  // A plain Task (not a `packet:` job) in the lead's sprint session: callID -> { sid, desc, sub, proof, started, stopped }.
  // helper_max_min covers it too (engine 2026-09-29 20:00Z: the lead sat 72 min on one review Task, 26 packets waiting, 0 running).
  const adhocRun = ho.adhocRun ?? new Map();
  // Helpers of helpers (Maxim 2026-10-04: "each can dispatch helpers for himself up to 10"): every
  // agent may send Tasks; a session that is itself a helper (it has a parent) holds at most
  // SUB_HELPERS_MAX running at once. callID -> parent session id while the Task runs.
  const SUB_HELPERS_MAX = 10;
  const subRun = new Map();
  const subRunning = (sid) => { let n = 0; for (const v of subRun.values()) if (v === sid) n += 1; return n; };
  const parentOf = async (sid) => {
    try { return (await client.session.get({ path: { id: sid } }))?.data?.parentID ?? null; } catch { return null; }
  };
  const repeatKey = (a) => {
    const norm = (s, n) => String(s ?? "").toLowerCase().replace(/\d+/g, "#").replace(/\s+/g, " ").trim().slice(0, n);
    return `${a.subagent_type}|${norm(a.description, 80)}|${norm(a.prompt, 160)}`;
  };
  // W2-14 (C-237 enforcement, w1-18: 297+230+187 dups/7d): every plain-Task dispatch is
  // counted under its repeatKey fingerprint. A fingerprint dispatched REPEAT_CAP times
  // (knob repeat_cap, default 3) within 3 h is held like a NOOP repeat, whether or not any
  // run ended NOOP. `packet:` seat dispatches are excluded: the seat rest/readiness holds
  // already own those, and standing teams re-send by design.
  const REPEAT_WINDOW_MS = 3 * 3_600_000;
  const repeatCap = () => Math.max(2, Number(knobValue("repeat_cap")) || 3);
  const adhocSeen = ho.adhocSeen ?? new Map(); // repeatKey -> dispatch timestamps within the window
  const noteDispatch = (key) => {
    const at = now();
    const list = [...(adhocSeen.get(key) ?? []).filter((t) => at - t < REPEAT_WINDOW_MS), at];
    if (adhocSeen.size > 500 && !adhocSeen.has(key)) adhocSeen.delete(adhocSeen.keys().next().value);
    adhocSeen.set(key, list);
    for (const [k, v] of adhocSeen) if (v.length && at - v.at(-1) > REPEAT_WINDOW_MS) adhocSeen.delete(k);
    return list.length;
  };
  const standingRuns = ho.standingRuns ?? new Map(); // standing packet -> runs started
  let memLogAt = 0; // the last 'held: memory' log line (one per 10 min)
  const standingLast = ho.standingLast ?? new Map(); // standing packet -> when its last run started
  // A one-off or plain Task stopped at helper_max_min twice in 12 h is not sent a third time (owner 2026-09-30, engine and forge logs:
  // "GX5 headless close" was stopped 4 times, three hours of one helper's time, and forge's speed repairs twice each, 20 stops in 10 h).
  // Hybrid dispatch (owner 2026-09-30, "today I am brave"): the knob bg_width N (0 = off, the default) runs RESEARCH helpers
  // (role researcher, scout, explorer) in the background, N at a time, started by the keeper from the ready one-offs and the
  // standing seats of those roles; the lead's batches then hold only writers, judges, pilots and planners, sent live as before.
  // Research results come back to the lead as "[loop-keeper] Queue results" messages at its next idle, like any queue result.
  // The machine floor (min_free_gb) and the serial rule of the old queue mode apply. The children are sessions under the
  // sprint session, titled "<title> (@researcher subagent)", so OpenCode lists them.
  const bgWidth = () => Math.max(0, Math.min(12, Number(knobValue("bg_width")) || 0));
  const BG_ROLE = /^(?:researcher|scout|explorer)(?:-paid)?$/;
  const isBg = (p) => bgWidth() > 0 && !!p && BG_ROLE.test(String(p.role ?? ""));
  const bgLine = () => {
    if (!bgWidth()) return "";
    const run = [...queueRunning.values()];
    return ` Background research: ${run.length} of ${bgWidth()} running${run.length ? ` (${run.slice(0, 4).map((j) => clip(j.title, 40)).join("; ")})` : ""}; the keeper starts those seats itself and their results arrive as "[loop-keeper] Queue results" messages: collect them like Task results and never send those seats in a batch.`;
  };
  const capStops = ho.capStops ?? new Map(); // packet name, or `sub|title` of a plain Task -> { n, at }
  const CAP_STOP_MAX = 2, CAP_STOP_WINDOW_MS = 12 * 3_600_000;
  const adhocKey = (sub, desc) => `${String(sub ?? "").toLowerCase()}|${String(desc ?? "").toLowerCase().replace(/\d+/g, "#").replace(/\s+/g, " ").trim().slice(0, 80)}`;
  const noteCapStop = (key) => { const e = capStops.get(key); capStops.set(key, { n: e && now() - e.at < CAP_STOP_WINDOW_MS ? e.n + 1 : 1, at: now() }); };
  const capStopped = (key) => { const e = capStops.get(key); return e && e.n >= CAP_STOP_MAX && now() - e.at < CAP_STOP_WINDOW_MS ? e : null; };
  const standingBad = new Set(); // refused standing packets, logged once
  const parsePacket = (text) => {
    const m = String(text ?? "").replace(/\r\n/g, "\n").match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
    if (!m) return null;
    const fm = Object.fromEntries(m[1].split("\n").map((l) => l.match(/^([\w-]+):\s*(.*)$/)).filter(Boolean)
      .map((x) => [x[1], x[2].trim().replace(/^["']|["']$/g, "")]));
    return fm.role && m[2].trim() ? { role: fm.role, title: fm.title || "queued packet", body: m[2].trim(), copies: Number(fm.copies) || 1, fm } : null;
  };
  // A one-off writer packet names its Goal, Scope, Proof and Stop (center 2026-09-27: all 50
  // engine writer packets in 12 h missed one). The words are the dispatch meter's, so a repo's own
  // names count (owned paths, acceptance, budget). Gates and the chain's own packets are exempt.
  const CARD = {
    Goal: /\bGoal\b|EMPIRE outcome|outcome it moves/i,
    Scope: /\bScope\b|owned paths?|\bOwns?\b|\bOwned\b|only these (?:files|paths)|\bhome\b/i,
    Proof: /\bProof\b|acceptance|Done[- ]when|\bAccept\b/i,
    Stop: /\bStop\b|\bBudget\b|\b[SML] \d+ min/i,
  };
  const cardMissing = (p) => (GATE.test(p.role) || (p.fm && p.fm.chain && p.fm.chain !== "start") ? [] : Object.keys(CARD).filter((k) => !CARD[k].test(p.body)));
  // Packets with the same `serial:` run one at a time (engine merges into master, the forge
  // editor): the rest wait in ready/ or standing/ until that one ends.
  const serialBusy = (s) => !!s && [...queueRunning.values()].some((j) => j.serial === s);
  // One admission path for both dispatchers (lean-2): the queue launcher, the
  // foreground batch planner and the `packet:` hook used to ask the same three
  // questions (known role? complete card? seat eligible?) in triplicated inline
  // code. They now share these verdicts and differ only in what they do with
  // the answer (the queue refuses to failed/ with a teaching note, the batch
  // skips its line for the launch pass to refuse, `packet:` refuses it to the
  // loop). Serial, heavy, copies and the research reserve stay delivery-side:
  // they depend on each dispatcher's live batch/queue state.
  const roleKnown = (p) => !!p && roles.has(String(p.role ?? "").replace(/-paid$/, ""));
  const admitPacket = (p) => {
    if (!p) return { why: "no front matter with role: and title:", note: "no front matter", teachable: false };
    if (!roleKnown(p)) return { why: `no agent named ${p.role} in this repo`, note: `unknown role ${p.role}`, teachable: false };
    const missing = cardMissing(p);
    if (missing.length) return { why: `no ${missing.join(", ")} line`, note: `no ${missing.join(", ")} line`, teachable: true };
    return { ok: true };
  };
  // One seat-eligibility path: rest, role and readiness holds are the same
  // whether the seat runs as a background child (queue) or live (foreground).
  const seatHold = (f, p, used) => {
    if ((standingRest.get(f) ?? 0) > now()) return { kind: "resting" };
    if (!roleKnown(p)) return { kind: "refused", why: p ? `unknown role ${p.role}` : "no front matter" };
    const readiness = seatReadiness.evaluate(p, used);
    if (!readiness.ok) return { kind: "readiness", why: readiness.why };
    return { ok: true, readiness };
  };
  // One file may hold a whole ready list: each packet starts with its own front matter (a `---`
  // line, `key: value` lines with a `role:`, a `---` line). It is split into one file per packet
  // before any starts, so the loop queues a wave in one write instead of one message per packet.
  const FRONT = /^---\n(?:[\w-]+:[^\n]*\n)*role:[^\n]*\n(?:[\w-]+:[^\n]*\n)*---\n/gm;
  const splitBatch = (file) => {
    const text = (read(file) ?? "").replace(/\r\n/g, "\n");
    const starts = [...text.matchAll(FRONT)].map((m) => m.index);
    if (starts.length < 2) return false;
    const base = file.slice(0, -3);
    starts.forEach((at, i) => writeFileSync(`${base}-${String(i + 1).padStart(2, "0")}.md`, text.slice(at, starts[i + 1] ?? text.length).trimEnd() + "\n"));
    rmSync(file, { force: true });
    return starts.length;
  };
  const queueMove = (from, dir, extra = "") => {
    try {
      mkdirSync(qsub(dir), { recursive: true });
      const to = join(qsub(dir), basename(from));
      writeFileSync(to, (read(from) ?? "") + extra);
      rmSync(from, { force: true });
      return to;
    } catch { return null; }
  };
  const queueCount = (dir) => { try { return readdirSync(qsub(dir)).filter((f) => f.endsWith(".md")).length; } catch { return 0; } };
  // Failed one-offs of the last 24 h (center 2026-09-28: 69 failed rows sat unread 12+ h in three
  // queues, most of them queue-era refusals of renamed roles). A standing run's failed record is a
  // log, not a packet (its seat runs again); older rows are history, the board is the truth.
  const FAILED_FRESH_MS = 24 * 3_600_000;
  const STANDING_RECORD = /^# .*\(@[\w.-]+, standing\)/;
  const failedFresh = () => {
    let files;
    try { files = readdirSync(qsub("failed")).filter((f) => f.endsWith(".md")); } catch { return []; }
    const out = [];
    for (const f of files) {
      const full = join(qsub("failed"), f);
      let t;
      try { t = statSync(full).mtimeMs; } catch { continue; }
      if (Date.now() - t > FAILED_FRESH_MS) continue; // file times are the wall clock
      const text = read(full) ?? "";
      if (STANDING_RECORD.test(text)) continue;
      const why = text.match(/<!-- keeper: ([^>]*?) -->/)?.[1] ?? text.match(/## Result \(failed: ([^)\n]*)/)?.[1] ?? "failed";
      out.push({ name: f.slice(0, -3), why: clip(why, 80), t });
    }
    return out.sort((a, b) => b.t - a.t);
  };
  const askFor = (p) => (GATE.test(p.role) || /^\s*`?RESULT:/m.test(p.body) ? "" : RESULT_ASK);
  // A claim lives as long as its run (center 2026-09-28: finished and NOOP runs held center's 8 coder
  // rows for 3 h each, the NOOP runs renewed them with "NOOP sweep" lines, and the coder seat ran 18
  // times for nothing). Each line names its run; the keeper deletes a run's lines when it ends; the
  // 2 h window (over helper_max_min) only ends the lines of a run the keeper never saw end.
  const claimText = (n, role, id) => `\n\nStanding team run #${n}: you are one of this sprint's standing helpers (run \`${id}\`). When you take an item, first append one line \`<item ID> | ${id} | <UTC> | <the files, folder or crate you will own>\` to ${qsub("claims.txt")} (a shell append works where your edits are scoped); skip an item, and any files, folder or crate, another run claimed there in the last 2 h. The keeper deletes your lines when this run ends; a run that takes nothing writes no line. One item per run, done end to end by the /sprint rules.`;
  // Every release also drops lines older than that 2 h window: one-off packets' helpers name runs the
  // keeper cannot match, so their lines never ended (2026-10-03: fp-research 207 dead lines, 20 KB the
  // helpers read 185 times a day; center's size-check FAILs past 20 dead lines).
  const CLAIM_TTL_MS = 2 * 60 * 60_000;
  const claimAt = (line) => {
    const m = String(line.split("|")[2] ?? "").match(/(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})(?::(\d{2}))?/);
    const t = m ? Date.parse(`${m[1]}T${m[2]}:${m[3] ?? "00"}Z`) : NaN;
    return Number.isFinite(t) ? t : null;
  };
  const releaseClaims = (id) => {
    const file = qsub("claims.txt");
    const text = read(file);
    if (!text) return;
    const lines = text.split(/\r?\n/);
    const cut = now() - CLAIM_TTL_MS;
    const keep = lines.filter((l) => !(id && l.split("|")[1]?.trim() === id) && !((claimAt(l) ?? cut) < cut));
    if (keep.length !== lines.length) try { writeFileSync(file, keep.join("\n")); } catch { /* the 2 h window ends them anyway */ }
  };
  // The chain (owner 2026-10-04, "y if useful": the lean keeper of 2026-10-02 had cut it, and judges then ran only when a lead
  // sent one by hand: design-studio 0 in 4 rounds, forge 4 a day). A helper whose packet carries `chain: start` and ends
  // `RESULT: DONE` gets ONE review one-off from <queue>/chain/review.md; a review ending `VERDICT: FAIL` gets ONE repair from
  // chain/repair.md, and the repair's DONE one more review. PASS writes nothing (the lead lands it); NOOP, BLOCKED, PARTIAL, a cut
  // or failed run, a second FAIL, a BLOCKED verdict and a gate's own seat write nothing either: the lead sees them as before.
  // Templates are the repo's words with {{id}} {{role}} {{title}} {{record}} (the finished run's record in done/) and {{result}}
  // (its reply, cut) filled in, plus the run's RESULT/ROW/LANE/FILES lines (the reply's tail is what the cut loses). A repo
  // without them has no chain, logged once (rename chain/review.md to switch one repo's chain off). One step per name: a step
  // already waiting in ready/ or running/ is not written again.
  const chainWarned = new Set();
  const chainNext = (job, text, record) => {
    const fm = job.fm ?? {};
    const step = fm.chain;
    const last = (re) => [...String(text).matchAll(re)].at(-1)?.[1]?.toUpperCase();
    let next, attempt = Number(fm.attempt) || 1;
    if (!qdir || !step || (step === "start" && GATE.test(job.role))) return;
    if (step === "start" || step === "repair") {
      if (last(/RESULT:\s*(DONE|PARTIAL|BLOCKED|NOOP)\b/gi) !== "DONE") return;
      next = "review";
    } else if (step === "review" && last(/VERDICT:\s*\**\s*(PASS|FAIL|BLOCKED)\b(?!\|)/gi) === "FAIL" && attempt < 2) { next = "repair"; attempt += 1; }
    else return;
    const sid = job.sid ?? status.session ?? "-";
    const tpl = read(join(qsub("chain"), `${next}.md`));
    if (!tpl) { if (!chainWarned.has(next)) { chainWarned.add(next); log(`${sid} chain: no ${next}.md in ${qsub("chain")}: no ${next} step for this repo`); } return; }
    const origin = fm.of ?? job.id;
    const writer = fm.writer ?? job.role;
    const title = fm.origin_title ?? job.title;
    const name = `${origin}-${next}${next === "review" && attempt > 1 ? `-${attempt}` : ""}.md`;
    if (["ready", "running"].some((d) => existsSync(join(qsub(d), name)))) return;
    const vals = { id: origin, role: writer, title, record, result: clip(text, 4000) };
    const p = parsePacket(tpl.replace(/\r\n/g, "\n").replace(/\{\{(\w+)\}\}/g, (m, k) => vals[k] ?? m));
    if (!p || !roleKnown(p)) {
      if (!chainWarned.has(`${next}!`)) { chainWarned.add(`${next}!`); log(`${sid} chain: ${next}.md has no front matter with role: and title:, or names a role this repo has no agent for`); }
      return;
    }
    const head = { ...p.fm, role: p.role, title: p.title, chain: next, of: origin, writer, attempt, origin_title: title.replace(/\n/g, " ") };
    delete head.copies;
    const facts = [...String(text).matchAll(/^[ \t>*`-]*(?:RESULT|VERDICT|ROW|LANE|BRANCH|OWNED|HOME|FILES|CRATE|FLAGS|CHANGED)\b.*$/gim)].slice(-6).map((m) => `\n${clip(m[0], 300)}`).join("");
    try {
      mkdirSync(qsub("ready"), { recursive: true });
      writeFileSync(join(qsub("ready"), name), `---\n${Object.entries(head).map(([k, v]) => `${k}: ${v}`).join("\n")}\n---\n${p.body}\n\nKeeper facts: run ${job.id} (${job.standing ? `seat ${job.standing.slice(0, -3)}, ` : ""}@${job.role}), ${clip(job.title, 100)}.${facts}\n`);
      log(`${sid} chain: ${job.id} -> ${name.slice(0, -3)} as ${p.role}`);
    } catch (e) { log(`${sid} chain: ${next} for ${job.id} not written (${e?.message ?? e})`); }
  };
  // A finished helper's record (done/ or failed/), its seat's rest, and any chain packet it names.
  const finishJob = (job, text, failed) => {
    const result = failed ? "failed" : "completed";
    const note = `\n\n## Result (${result}${failed ? `: ${failed}` : ""})\n\n${text}\n`;
    if (job.standing) {
      // A standing packet stays in standing/; this run's record goes to done/ (or failed/).
      try { mkdirSync(qsub(failed ? "failed" : "done"), { recursive: true }); writeFileSync(join(qsub(failed ? "failed" : "done"), `${job.id}.md`), `# ${job.title} (@${job.role}, standing)${note}`); } catch { /* the record is best effort */ }
      releaseClaims(job.id);
      if (seatReadiness.complete(job.readiness, text, failed)) write({ readinessSeen: [...readySeen] });
      // center coder-rows 2026-09-29: NOOP every 3-4 minutes for an hour, because the lead sent the resting seat again.
      if (failed || now() - job.started < 2 * 60_000 || /RESULT:\s*(?:NOOP|BLOCKED)\b/.test(text)) {
        const row = standingNoops.get(job.standing) ?? 0;
        standingNoops.set(job.standing, row + 1);
        standingRest.set(job.standing, now() + 30 * 2 ** Math.min(row, 2) * 60_000);
      } else standingNoops.delete(job.standing);
    } else {
      const from = join(qsub("running"), `${job.id}.md`);
      queueMove(from, failed ? "failed" : "done", note);
      rmSync(`${from}.json`, { force: true });
      releaseClaims(job.id); // a line naming the packet goes with it; older strays go by the 2 h window
    }
    if (!failed && !job.stopped) chainNext(job, text, join(qsub("done"), `${job.id}.md`));
    return result;
  };
  const launchQueued = async (sid = status.session) => {
    if (!qdir || !sid || gone || retired.has(sid) || existsSync(here.halt) || state.get(sid)?.stopped) return 0;
    let files;
    try {
      for (const f of readdirSync(qsub("ready")).filter((f) => f.endsWith(".md"))) {
        const n = splitBatch(join(qsub("ready"), f));
        if (n) log(`${sid} queue: ${f.slice(0, -3)} split into ${n} packets`);
      }
      files = readdirSync(qsub("ready")).filter((f) => f.endsWith(".md")).sort();
    } catch { files = []; }
    const width = Number(knobValue("width")) || 0;
    if (!width) return 0;
    // Every bad packet is refused at once (the loop learns it this round), good ones wait their turn.
    const good = [];
    for (const f of files) {
      const src = join(qsub("ready"), f);
      let p = parsePacket(read(src));
      if (p && !roles.has(p.role.replace(/-paid$/, ""))) {
        // `role: pilot-bench-r3`, `lead-c74` (forge, 7 packets in 24 h): the packet's own name in the role line. A leading part that is an agent
        // of this repo is the role; the file is rewritten once and the packet goes on. No such part: refused below, as before.
        const parts = p.role.split("-");
        const alias = parts.map((_, i) => parts.slice(0, parts.length - 1 - i).join("-")).find((c) => c && roles.has(c));
        if (alias) {
          try {
            const raw = read(src);
            const m = raw.replace(/\r\n/g, "\n").match(/^---\n([\s\S]*?)\n---/);
            if (m) {
              writeFileSync(src, raw.replace(/\r\n/g, "\n").replace(m[1], () => m[1].replace(/^role:.*$/m, `role: ${alias}`)));
              log(`${sid} queue: ${f.slice(0, -3)} role ${p.role} is no agent here, read as ${alias}`);
              p = parsePacket(read(src));
            }
          } catch { /* refused below */ }
        }
      }
      const missing = p && roleKnown(p) ? cardMissing(p) : null;
      if (missing && !missing.length) { good.push({ f, src, p }); continue; }
      const admitted = admitPacket(p);
      queueMove(src, "failed", `\n\n<!-- keeper: ${admitted.why} -->\n`);
      log(`${sid} queue: ${f.slice(0, -3)} refused (${admitted.note})`);
      snapDirty = true; // a refused packet moved: the next beat censuses
      // The loop learns it with its next results, not from a log it never reads.
      if (missing) queueDone.push({ child: `refused-${f.slice(0, -3)}`, id: f.slice(0, -3), role: p.role, title: p.title, result: "refused",
        text: `The keeper refused this packet: ${admitted.why}. A writer packet carries Goal:, Scope: (owned paths), Proof: (the acceptance command) and Stop: (budget or stop rule) lines. Rewrite it and queue it again; it sits in ${qsub("failed")}.` });
    }
    // Foreground: the loop starts its helpers itself, in batches (see batchPlan); helpers the
    // queue started before the switch finish and report (drain, never cut).
    const hybrid = foreground();
    if (hybrid && !bgWidth()) return 0;
    const cap = hybrid ? Math.min(bgWidth(), width) : width;
    // The machine (center 2026-09-27): four loops share one 16 GB laptop, and a starved build
    // times out (forge's gateway build did, twice). No new helper while free memory is under
    // the knob min_free_gb (1.5 by default): the width is the ceiling, the machine the floor.
    // KEEPER_FREE_MEM (bytes) stands in for the machine in tests.
    const floor = (Number(knobValue("min_free_gb")) || 1.5) * 2 ** 30;
    const roomy = () => {
      const free = Number(process.env.KEEPER_FREE_MEM) || freemem();
      if (free >= floor) return true;
      calls.heldMem = (calls.heldMem ?? 0) + 1;
      if (now() - memLogAt > 10 * 60_000) { memLogAt = now(); log(`${sid} queue: held, ${(free / 2 ** 30).toFixed(1)} GB free (under ${floor / 2 ** 30} GB): no new helper until memory frees`); }
      return false;
    };
    let working = hybrid ? queueRunning.size : await helpersRunning(sid);
    let started = 0;
    for (const { f, src, p } of good) {
      if (hybrid && !isBg(p)) continue;
      if (working >= cap || !roomy()) break;
      if (serialBusy(p.fm.serial)) continue;
      const id = f.slice(0, -3);
      const child = (await client.session.create({ body: { parentID: sid, title: `${p.title} (@${p.role} subagent)` } }))?.data;
      if (!child?.id) break;
      await client.session.promptAsync({ path: { id: child.id }, body: { agent: p.role, parts: [{ type: "text", text: p.body + askFor(p) }] } });
      const to = queueMove(src, "running");
      try { if (to) writeFileSync(`${to}.json`, JSON.stringify({ child: child.id, role: p.role, title: p.title, started: iso() })); } catch { /* recovery is best effort */ }
      queueRunning.set(child.id, { id, role: p.role, title: p.title, started: now(), serial: p.fm.serial, fm: p.fm });
      working += 1;
      started += 1;
      calls.queued = (calls.queued ?? 0) + 1;
      log(`${sid} queue: started ${id} as ${p.role} (${child.id})`);
      snapDirty = true; // a queued helper started: the next beat censuses
    }
    // The standing team (owner 2026-09-27: "each agent from 1/20 does his part, all as a team,
    // 24/7"). Packets in standing/ are never used up: each keeps `copies:` helpers running (default
    // 1), one more per pass across the team until the width is full; a finished run goes back to
    // the loop like any queue result and its packet starts again. Ready packets go first. A run
    // that ended in under 2 minutes or said NOOP/BLOCKED rests 30 minutes.
    let team;
    try { team = readdirSync(qsub("standing")).filter((f) => f.endsWith(".md")).sort(); } catch { team = []; }
    // Fair turns when the seats outnumber the width (factory 13 seats on width 10, 2026-09-27):
    // the seat that started longest ago goes first; ties keep the name order.
    team.sort(seatOrder);
    const runningOf = (f) => [...queueRunning.values()].filter((j) => j.standing === f).length;
    for (let more = true; more && working < cap;) {
      more = false;
      for (const f of team) {
        if (working >= cap) break;
        if (!roomy()) { more = false; break; }
        const p = parsePacket(read(join(qsub("standing"), f)));
        const hold = seatHold(f, p, readyBusy());
        if (!hold.ok) {
          if (hold.kind === "refused" && !standingBad.has(f)) { standingBad.add(f); log(`${sid} standing: ${f.slice(0, -3)} refused (${hold.why})`); }
          continue;
        }
        if (hybrid && !isBg(p)) continue;
        if (runningOf(f) >= Math.min(Math.max(1, p.copies), cap) || serialBusy(p.fm.serial)) continue;
        const readiness = hold.readiness;
        const readyItem = readiness.items?.[0];
        const n = (standingRuns.get(f) ?? 0) + 1;
        standingRuns.set(f, n);
        standingLast.set(f, now());
        const id = `${f.slice(0, -3)}-r${n}`;
        if (readyItem) readyPending.add(readyItem.key);
        try {
          const child = (await client.session.create({ body: { parentID: sid, title: `${p.title} #${n} (@${p.role} subagent)` } }))?.data;
          if (!child?.id) return started;
          await client.session.promptAsync({ path: { id: child.id }, body: { agent: p.role, parts: [{ type: "text", text: p.body + (readyItem && !readiness.legacy ? `

Ready work: ${readyItem.id}. Claim only this item; selectors do not authorize switching items. Stop if its eligibility changed.` : "") + claimText(n, p.role, id) + askFor(p) }] } });
          queueRunning.set(child.id, { id, role: p.role, title: `${p.title} #${n}`, started: now(), standing: f, readiness: readyItem, serial: p.fm.serial, fm: p.fm });
          working += 1;
          started += 1;
          more = true;
          calls.standing = (calls.standing ?? 0) + 1;
          log(`${sid} standing: started ${id} as ${p.role} (${child.id})`);
          snapDirty = true; // a standing run started: the next beat censuses
        } finally { if (readyItem) readyPending.delete(readyItem.key); }
      }
    }
    return started;
  };
  // ---- Foreground batches (owner 2026-09-28, C-88: "I don't want background stuff", "lead should
  // dispatch in batches workers every time", "I want it seen live"). The keeper starts no helper:
  // it writes the next batch to <queue>/batch.md (ready one-offs and chain steps first, then the
  // standing seats in fair turns, up to the width, at most `heavy_max` packets with `cpu: heavy`
  // (owner 2026-09-27: rustc ate the CPU), one per `serial:`), and the loop sends it as ONE message
  // of Task calls whose prompt is `packet: <name>`. The keeper puts that packet's text and role into
  // the call, so each helper runs live in the loop's session, and its result goes through the same
  // records, rests and chain (review, repair) as a queued helper's. A helper past
  // `helper_max_min` (90) is stopped so its batch can end; a packet whose batch ended without its
  // result (a stop, a restart) goes back to ready/.
  const PACKET_REF = /^\s*(?:packet|seat):\s*`?([\w.+-]+?)(?:\.md)?`?\s*$/i;
  const SERIAL_GROUP_MAX = 3; // engine 2026-09-28: a group of 5 merges held a batch of 20 for 40 min after the rest were done
  const refOf = (x) => x.names.join("+");
  const titleOf = (x) => (x.names.length > 1 ? `${x.title} (+${x.names.length - 1} more, in order)` : x.title);
  const HEAVY_MAX = 3;
  const BATCH_GAP_MS = 60_000; // Task calls of one message start seconds apart; batches minutes apart
  const fgJobs = ho.fgJobs ?? new Map(); // Task callID -> { id, role, title, desc, started, standing, fm, sid }
  const batchMeter = ho.batchMeter ?? { n: 0, at: 0, startAt: 0 }; // the loop's latest batch: Task calls, first and last call
  const heavyOf = (p) => /\bheavy\b/i.test(p?.fm?.cpu ?? "");
  const batchPlan = () => {
    const width = Number(knobValue("width")) || 0;
    if (!qdir || !width) return null;
    const heavyMax = Number(knobValue("heavy_max")) || HEAVY_MAX;
    const busyJobs = [...fgJobs.values(), ...queueRunning.values()];
    const serials = new Set(busyJobs.map((j) => j.fm?.serial).filter(Boolean));
    let heavy = busyJobs.filter(heavyOf).length;
    const list = [];
    const held = { heavy: new Set(), serial: new Set(), resting: new Set(), readiness: new Set() };
    const readyUsed = readyBusy();
    // One-offs of one `serial:` ride in one call that runs them in order (engine 2026-09-28: 12
    // merges waited on master; one per batch would take hours).
    const grouped = new Map(); // serial -> the list entry holding this batch's packets of it
    const names = (dir) => { try { return readdirSync(qsub(dir)).filter((f) => f.endsWith(".md")).sort(); } catch { return []; } };
    // One heavy place stays for the seats while a heavy seat is ready (engine 2026-09-28: one-offs
    // and chain steps took all 3 for hours; the FOCUS seats look, spatial and speed never ran).
    const heavySeatWaits = heavyMax > 1 && names("standing").some((f) => {
      const p = parsePacket(read(join(qsub("standing"), f)));
      return p && heavyOf(p) && roles.has(p.role.replace(/-paid$/, "")) && !((standingRest.get(f) ?? 0) > now()) && seatReadiness.evaluate(p, readyUsed).ok;
    });
    const take = (name, p, kind) => {
      const readiness = kind === "seat" ? seatReadiness.evaluate(p, readyUsed) : { ok: true };
      if (!readiness.ok) { held.readiness.add(name); return false; }
      const item = readiness.items?.[0];
      const g = kind !== "seat" && p.fm.serial ? grouped.get(p.fm.serial) : null;
      if (g && g.role === p.role && g.names.length < SERIAL_GROUP_MAX) { g.names.push(name); return true; }
      if (p.fm.serial && serials.has(p.fm.serial)) { held.serial.add(name); return false; }
      if (heavyOf(p) && heavy >= (kind === "seat" || !heavySeatWaits ? heavyMax : heavyMax - 1)) { held.heavy.add(name); return false; }
      if (p.fm.serial) serials.add(p.fm.serial);
      if (heavyOf(p)) heavy += 1;
      const entry = { name, names: [name], role: p.role, title: p.title.replace(/\s+/g, " "), kind };
      if (kind !== "seat" && p.fm.serial) grouped.set(p.fm.serial, entry);
      list.push(entry);
      if (item) readyUsed.add(item.key);
      return true;
    };
    // Research and plan seats keep a share of every batch (owner 2026-09-30, forge overnight: 4 batches, one-offs and chain steps filled
    // 9-15 of 15 places each time, and no researcher seat ran after 17:52Z): a fifth of the width, at least one, while such a seat is ready.
    const RESEARCH_ROLE = /^(?:researcher|planner|scout|explorer)(?:-paid)?$/;
    const researchSeatsReady = names("standing").filter((f) => {
      const p = parsePacket(read(join(qsub("standing"), f)));
      return p && !isBg(p) && RESEARCH_ROLE.test(p.role) && roles.has(p.role.replace(/-paid$/, "")) && !((standingRest.get(f) ?? 0) > now()) && seatReadiness.evaluate(p, readyUsed).ok;
    }).length;
    const reserve = Math.min(researchSeatsReady, Math.max(1, Math.ceil(width / 5)));
    for (const f of names("ready")) {
      if (list.length >= width - reserve) break;
      const p = parsePacket(read(join(qsub("ready"), f)));
      if (!admitPacket(p).ok) continue; // the launch pass refuses it
      if (isBg(p)) continue; // research runs in the background (bg_width)
      take(f.slice(0, -3), p, p.fm.chain && p.fm.chain !== "start" ? p.fm.chain : "one-off");
    }
    const seats = [];
    for (const f of names("standing").sort(seatOrder)) {
      const p = parsePacket(read(join(qsub("standing"), f)));
      if (p && isBg(p)) continue; // research runs in the background (bg_width)
      const hold = seatHold(f, p, readyUsed);
      if (!hold.ok) {
        if (hold.kind === "resting") held.resting.add(f.slice(0, -3));
        else if (hold.kind === "readiness") held.readiness.add(f.slice(0, -3));
        continue; // refused seats wait silently, serial holds are reported by take()
      }
      seats.push({ f, p });
    }
    const copies = new Map();
    if (reserve) {
      let got = 0;
      for (const { f, p } of seats) {
        if (got >= reserve || list.length >= width) break;
        if (!RESEARCH_ROLE.test(p.role)) continue;
        if (take(f.slice(0, -3), p, "seat")) { copies.set(f, (copies.get(f) ?? 0) + 1); got += 1; }
      }
    }
    for (let more = true; more && list.length < width;) {
      more = false;
      for (const { f, p } of seats) {
        if (list.length >= width) break;
        const n = copies.get(f) ?? 0;
        if (n >= Math.min(Math.max(1, p.copies), width)) continue;
        if (take(f.slice(0, -3), p, "seat")) { copies.set(f, n + 1); more = true; }
      }
    }
    return { width, heavyMax, list, held: Object.fromEntries(Object.entries(held).map(([k, v]) => [k, [...v]])) };
  };
  const batchLines = (plan) => plan.list.map((x, i) => `${i + 1}. ${x.role} | ${titleOf(x)} | packet: ${refOf(x)}`);
  let batchWritten = null;
  // A one-off listed in STALE_LISTINGS batch notes in a row and never sent is dead weight: center 2026-09-29 listed five packets
  // whose verdicts were already recorded 94 times, and every round the lead had to decline them again. They go to failed/ with the reason.
  const STALE_LISTINGS = 12;
  const listings = new Map();
  const writeBatch = () => {
    const plan = batchPlan();
    if (!plan) return null;
    const heldLine = Object.entries(plan.held).filter(([, v]) => v.length).map(([k, v]) => `${k}: ${v.join(", ")}`).join("; ");
    const failed = failedFresh();
    const body = `Send every line below as ONE message of ${plan.list.length} Task call${plan.list.length === 1 ? "" : "s"}: subagent_type = the role, description = the title, ` +
      `prompt = \`packet: <name>\` exactly. The keeper puts each packet's text into its call, so all of them run at once, live in your session. ` +
      `Width ${plan.width}, CPU-heavy at most ${plan.heavyMax}.\n\n${batchLines(plan).join("\n")}\n${heldLine ? `\nNot in this batch (${heldLine}).\n` : ""}` +
      (failed.length ? `\nFailed in the last 24 h (${qsub("failed")}; rewrite what still matters into ready/ under a new name, the rest is history):\n${failed.slice(0, 15).map((x) => `- ${x.name}: ${x.why}`).join("\n")}\n` : "");
    if (body !== batchWritten) {
      try { mkdirSync(qdir, { recursive: true }); writeFileSync(join(qdir, "batch.md"), `# Next batch: ${cfg.repo} (the keeper rewrites this file, ${iso()})\n\n${body}`); batchWritten = body; } catch { /* the continue carries the list anyway */ }
    }
    return plan;
  };
  // The continue's and the GO's batch note: the list itself, so the loop sends it without a read.
  const batchNote = () => {
    const plan = writeBatch();
    if (!plan) return null;
    for (const k of [...listings.keys()]) if (!plan.list.some((x) => x.name === k)) listings.delete(k); // only a run of listings in a row counts
    let dropped = false;
    for (const x of plan.list) {
      if (x.kind === "seat") continue;
      const n = (listings.get(x.name) ?? 0) + 1;
      listings.set(x.name, n);
      if (n < STALE_LISTINGS) continue;
      listings.delete(x.name);
      if (queueMove(join(qsub("ready"), `${x.name}.md`), "failed", `\n\n<!-- keeper: listed in ${n} batch notes in a row and never sent -->\n`)) dropped = true;
    }
    if (dropped) return batchNote(); // the list without it
    const sent = batchMeter.n;
    const failed = failedFresh().length;
    const thin = (sent && sent < plan.width && plan.list.length >= plan.width ? ` Your last batch sent ${sent} Task call${sent === 1 ? "" : "s"} for a width of ${plan.width}: send the whole list.` : "") +
      (failed ? ` ${failed} one-off packet${failed === 1 ? "" : "s"} failed in the last 24 h (listed in batch.md): rewrite what still matters into ready/.` : "");
    if (!plan.list.length) return `no packet is ready for a batch (width ${plan.width}): write one-offs to ${qsub("ready")} or seats to ${qsub("standing")} (front matter role: and title:), then send them.${thin}${bgLine()}`;
    return `next batch, ${plan.list.length} of width ${plan.width} (also in ${join(qdir, "batch.md")}): send it now as ONE message of ${plan.list.length} Task call${plan.list.length === 1 ? "" : "s"}, subagent_type the role, prompt exactly \`packet: <name>\`; then collect every result, judge and re-plan before the next batch.${thin} ` +
      plan.list.map((x) => `[${x.role}: ${clip(titleOf(x), 60)} | packet: ${refOf(x)}]`).join(" ") + bgLine();
  };
  // `packet: <name>` in a Task call: the ready one-off (moved to running/) or the standing seat
  // (a new run) with that name, its text, claim and RESULT asks.
  const takePacket = (name, sid) => {
    snapDirty = true; // a foreground dispatch, however it ends: the next beat censuses
    const readyFile = join(qsub("ready"), `${name}.md`);
    const cs = capStopped(name);
    if (existsSync(readyFile) && cs) {
      queueMove(readyFile, "failed", `

<!-- keeper: stopped at the helper_max_min cap ${cs.n} times in 12 h -->
`);
      return { why: `packet ${name} was stopped at the ${Number(knobValue("helper_max_min")) || 90} min cap ${cs.n} times in 12 h, so the keeper does not send it again unchanged (it sits in ${qsub("failed")}): split it into packets of half the size, or replan it under a new name` };
    }
    if (existsSync(readyFile) && isBg(parsePacket(read(readyFile)))) return { why: `${name} is a research packet: with bg_width on the keeper starts it in the background itself, do not send it` };
    if (existsSync(readyFile)) {
      const p = parsePacket(read(readyFile));
      const missing = roleKnown(p) ? cardMissing(p) : null;
      if (!missing || missing.length) {
        const why = !p ? "it has no front matter with role: and title:" : !missing ? `this repo has no agent named ${p.role}` : `it has no ${missing.join(", ")} line`;
        queueMove(readyFile, "failed", `\n\n<!-- keeper: ${why} -->\n`);
        return { why: `the keeper refused packet ${name}: ${why} (it sits in ${qsub("failed")})` };
      }
      const to = queueMove(readyFile, "running");
      try { if (to) writeFileSync(`${to}.json`, JSON.stringify({ fg: true, role: p.role, title: p.title, started: iso() })); } catch { /* recovery is best effort */ }
      return { id: name, role: p.role, title: p.title, started: now(), fm: p.fm, sid, text: p.body + askFor(p) };
    }
    const f = `${name}.md`;
    const p = existsSync(join(qsub("standing"), f)) ? parsePacket(read(join(qsub("standing"), f))) : null;
    if (!p) return { why: `no packet ${name} waits in ${qsub("ready")} or ${qsub("standing")} (taken already, or a typo)` };
    const hold = seatHold(f, p, readyBusy());
    if (hold.kind === "refused") return { why: `the seat ${name} names ${p.role}, which is no agent of this repo` };
    if (isBg(p)) return { why: `the seat ${name} is research: with bg_width on the keeper runs it in the background itself, do not send it` };
    if (hold.kind === "resting") { const restUntil = standingRest.get(f) ?? 0; return { why: `the seat ${name} rests until ${new Date(restUntil).toISOString().slice(11, 16)}Z: its last ${standingNoops.get(f) ?? 1} run(s) ended NOOP or BLOCKED. Send another packet, or write a one-off to ready/ if there is new work for it` }; }
    if (!hold.ok) throw new Error("Keeper readiness hold: " + hold.why);
    const readyItem = hold.readiness.items?.[0];
    const n = (standingRuns.get(f) ?? 0) + 1;
    standingRuns.set(f, n);
    standingLast.set(f, now());
    return { id: `${name}-r${n}`, role: p.role, title: `${p.title} #${n}`, started: now(), standing: f, readiness: readyItem, fm: p.fm, sid, text: p.body + (readyItem && !hold.readiness.legacy ? `

Ready work: ${readyItem.id}. Claim only this item; selectors do not authorize switching items. Stop if its eligibility changed.` : "") + claimText(n, p.role, `${name}-r${n}`) + askFor(p) };
  };
  // `packet: a+b+c`: one call runs those one-offs in order (a `serial:` group, see batchPlan).
  const takeGroup = (ref, sid) => {
    const names = ref.split("+").filter(Boolean);
    if (names.length < 2) return takePacket(ref, sid);
    const jobs = [];
    const refused = [];
    for (const n of names) { const j = takePacket(n, sid); if (j.text) jobs.push(j); else refused.push(j.why); }
    if (!jobs.length) return { why: refused.join("; ") };
    if (jobs.length === 1) return jobs[0];
    const text = `This call carries ${jobs.length} packets. Run them one after another, in this order; finish each (its own RESULT line) before the next.` +
      (refused.length ? ` Not included: ${refused.join("; ")}.` : "") +
      jobs.map((j, i) => `\n\n### Packet ${i + 1} of ${jobs.length}: ${j.title}\n\n${j.text}`).join("");
    return { id: jobs.map((j) => j.id).join("+"), role: jobs[0].role, title: `${jobs[0].title} (+${jobs.length - 1} more)`, started: now(), fm: jobs[0].fm, sid, group: jobs, text };
  };
  const collectForeground = (call, text, failed) => {
    const job = fgJobs.get(call);
    if (!job) return;
    snapDirty = true; // a batch result landed
    fgJobs.delete(call);
    for (const one of job.group ?? [job]) log(`${job.sid} batch: ${one.id} ${finishJob(one, text, failed)}`);
  };
  // Before a cap stop (Maxim 2026-10-04 "why agents get interrupted"): the cut helper's files and its last
  // words go into the packet file, so the next run of the packet goes on from there instead of from zero
  // (engine 357-ra14-review cut 3 times, 355-bv1 2 h twice, each from scratch). One block, replaced each cut.
  const SALVAGE_MARK = "<!-- keeper: cut-run salvage -->";
  const salvage = async (job, childId) => {
    try {
      const msgs = (await client.session.messages({ path: { id: childId } }))?.data ?? [];
      const files = new Set();
      for (const m of msgs) for (const p of m.parts ?? []) {
        if (p?.type !== "tool" || !/^(edit|write|patch|apply_patch|multiedit)$/i.test(String(p.tool ?? ""))) continue;
        const f = p.state?.input?.filePath ?? p.state?.input?.path;
        if (typeof f === "string" && f) files.add(f.replace(/\\/g, "/"));
      }
      const said = msgs.filter((m) => m?.info?.role === "assistant").map(textOf).filter((t) => t.trim()).join("\n").trim().slice(-3000);
      if (!files.size && !said) return null;
      const block = `\n\n${SALVAGE_MARK}\n## Earlier run was cut (${iso()})\n\nAn earlier run of this packet was stopped after ${ago(now() - job.started)} (time cap, a stop or a restart). Its work is on disk: read it, keep what is right and go on from there; do not start over.\n` +
        (files.size ? `\nFiles it edited: ${[...files].slice(0, 40).map((f) => `\`${f}\``).join(", ")}\n` : "") +
        (said ? `\nIts last words:\n\n${said.replace(/^/gm, "> ")}\n` : "");
      for (const one of job.group ?? [job]) {
        const f = join(qsub("running"), `${one.id}.md`);
        const cur = read(f);
        if (cur == null) continue;
        const at = cur.indexOf(`\n\n${SALVAGE_MARK}`);
        writeFileSync(f, (at < 0 ? cur.replace(/\s+$/, "") : cur.slice(0, at)) + block);
      }
      return { files: [...files], said };
    } catch { return null; }
  };
  // Every beat: a helper past helper_max_min is stopped (its Task returns, the batch can end); a
  // packet whose batch ended without its result waits for the next batch.
  const tendForeground = async () => {
    if (!fgJobs.size && !adhocRun.size) return;
    // A packet may carry its own cap (front matter max_min: 90 for a long proof); the knob is the floor
    // (Maxim 2026-10-04: engine packets with max_min 20-40 were cut under a 45 min knob, 33 cuts in 24 h).
    const capOf = (job) => Math.max(Number(job.fm?.max_min) || 0, Number(knobValue("helper_max_min")) || 90, PROOF_TEXT.test(String(job.text ?? "")) ? PROOF_MIN : 0) * 60_000;
    const kids = new Map();
    for (const [call, job] of fgJobs) {
      if (now() - job.started > 2 * 60_000 && (await turnOf(job.sid)) === "idle") {
        fgJobs.delete(call);
        // A stop, a retire or a restart cut the batch (2026-10-04: 122 of 198 cut helpers died in such
        // clusters): its work goes back with the packet like a cap cut's (a cap cut already wrote it).
        let kept = null;
        if (!job.standing && !job.stopped) {
          try {
            if (!kids.has(job.sid)) kids.set(job.sid, (await client.session.children({ path: { id: job.sid } }))?.data ?? []);
            const child = kids.get(job.sid).filter((k) => k?.title === `${job.desc} (@${job.sub ?? job.role} subagent)`).sort((a, b) => (b.time?.created ?? 0) - (a.time?.created ?? 0))[0];
            if (child?.id) kept = await salvage(job, child.id);
          } catch { /* the packet still goes back */ }
        }
        for (const one of job.group ?? [job]) if (!one.standing) { const from = join(qsub("running"), `${one.id}.md`); queueMove(from, "ready"); rmSync(`${from}.json`, { force: true }); } else releaseClaims(one.id);
        log(`${job.sid} batch: ${job.id} got no result (its batch ended first); ${job.standing ? "the seat runs in a later batch" : `back to ready/${kept ? ` with its work (${kept.files.length} files)` : ""}`}`);
        continue;
      }
      if (job.stopped || now() - job.started <= capOf(job)) continue;
      if (!kids.has(job.sid)) kids.set(job.sid, (await client.session.children({ path: { id: job.sid } }))?.data ?? []);
      const child = kids.get(job.sid).filter((k) => k?.title === `${job.desc} (@${job.sub ?? job.role} subagent)`).sort((a, b) => (b.time?.created ?? 0) - (a.time?.created ?? 0))[0];
      if (!child?.id) continue;
      const kept = job.standing ? null : await salvage(job, child.id);
      try { await client.session.abort({ path: { id: child.id } }); } catch { /* it may be gone */ }
      job.stopped = true;
      if (!job.standing) for (const one of job.group ?? [job]) noteCapStop(one.id);
      log(`${job.sid} batch: ${job.id} ran ${ago(now() - job.started)}, over helper_max_min: stopped so its batch can end${kept ? `; kept its work (${kept.files.length} files, ${kept.said.length} chars) for the next run` : ""}`);
      snapDirty = true; // a helper was stopped at the cap: the next beat censuses
    }
    // The lead's own plain Tasks get the same cap; the closest child by start time is the one.
    for (const [call, run] of adhocRun) {
      try {
        if (run.stopped) { if (now() - run.started > 6 * 3_600_000) adhocRun.delete(call); continue; }
        const cap = Math.max(Number(knobValue("helper_max_min")) || 90, run.proof ? PROOF_MIN : 0) * 60_000;
        if (now() - run.started <= cap) continue;
        if (!kids.has(run.sid)) kids.set(run.sid, (await client.session.children({ path: { id: run.sid } }))?.data ?? []);
        const child = kids.get(run.sid).filter((k) => k?.title === `${run.desc} (@${run.sub} subagent)`)
          .sort((a, b) => Math.abs((a.time?.created ?? 0) - run.started) - Math.abs((b.time?.created ?? 0) - run.started))[0];
        if (!child?.id) continue;
        try { await client.session.abort({ path: { id: child.id } }); } catch { /* it may be gone */ }
        run.stopped = true;
        noteCapStop(adhocKey(run.sub, run.desc));
        calls.adhocStopped = (calls.adhocStopped ?? 0) + 1;
        log(`${run.sid} task: "${clip(run.desc, 50)}" ran ${ago(now() - run.started)}, over helper_max_min: stopped so the lead can go on`);
        snapDirty = true; // a plain Task was stopped at the cap: the next beat censuses
      } catch { /* the next beat tries again */ }
    }
  };
  const collectQueued = async (child, failed) => {
    const job = queueRunning.get(child);
    if (!job) return;
    snapDirty = true; // a queued result landed
    queueRunning.delete(child);
    let text = "";
    try {
      const msgs = (await client.session.messages({ path: { id: child } }))?.data ?? [];
      const last = msgs.findLast((m) => m.info?.role === "assistant");
      text = textOf(last).trim();
      if (!failed && last?.info?.error) failed = describe(last.info.error);
    } catch (e) { failed = failed ?? `result unreadable (${e?.message ?? e})`; }
    // The loop gets the result before the chain's next step is written (the old order).
    const result = failed ? "failed" : "completed";
    queueDone.push({ child, ...job, result, text: failed ? `${failed}\n${text}` : text });
    log(`${status.session} queue: ${job.id} ${result}`);
    finishJob(job, text, failed);
  };
  // At the loop's idle (from decide, whose own busy flag is already set) or from the beat.
  const deliverQueued = async (fromDecide = false, sid = status.session) => {
    const st = sid && state.get(sid);
    if (!queueDone.length || !st || gone || st.stopped || st.sending || st.timer || (!fromDecide && st.busy)) return false;
    if ((await turnOf(sid)) !== "idle") return false;
    const batch = queueDone.splice(0);
    const clipped = (t) => (t.length > 6000 ? `${t.slice(0, 6000)}\n[... cut at 6000 chars; the full result is in ${qsub("done")}]` : t);
    const text = `${QUEUE_RESULTS}: ${batch.length} queued helper${batch.length > 1 ? "s" : ""} finished. Collect each like a Task result, then top the queue up (${qsub("ready")}).\n` +
      batch.map((r) => `<task id="${r.child}" state="${r.result}">\n<summary>Queued task ${r.result}: ${r.title} (@${r.role})</summary>\n<task_result>\n${clipped(r.text)}\n</task_result>\n</task>`).join("\n");
    st.sending = true;
    try {
      await client.session.promptAsync({ path: { id: sid }, body: bodyFor(st.via ?? {}, text) });
    } catch (e) {
      queueDone.unshift(...batch);
      log(`${sid} queue: results not delivered (${e?.message ?? e}); the next beat retries`);
      return false;
    } finally { st.sending = false; }
    st.recheck = true;
    log(`${sid} queue: delivered ${batch.length} result(s)`);
    snapDirty = true; // results went back to the loop: the next beat censuses
    return true;
  };
  // Every beat: helpers that ended without an idle event (a restart, a lost event) are collected,
  // one past the limit is stopped; then free width is filled and finished results go out.
  const tendQueue = async () => {
    if (!qdir) return;
    await tendForeground();
    for (const [child, job] of queueRunning) {
      if (now() - job.started > QUEUE_STUCK_MS) {
        try { await client.session.abort({ path: { id: child } }); } catch { /* it may be gone */ }
        await collectQueued(child, `stopped after ${ago(now() - job.started)} (the queue limit is ${QUEUE_STUCK_MS / 60_000} min)`);
      } else if (now() - job.started > 60_000 && (await turnOf(child)) === "idle") {
        const last = ((await client.session.messages({ path: { id: child } }))?.data ?? []).at(-1);
        if (last?.info?.role === "assistant" && last.info.time?.completed) await collectQueued(child);
      }
    }
    await launchQueued();
    await deliverQueued();
    // batch.md is the loop's dispatch view: rewrite it when a decision moved
    // the queue (a launch, refusal, result or cap stop set snapDirty above),
    // not on every idle beat. The loop's continue always carries a fresh list
    // via batchNote, so the file is fresh as of the last decision.
    if (foreground() && snapDirty) writeBatch();
  };
  // After a restart: packets that were running come back into the map (or to ready/ when their
  // session is gone; a foreground batch always is), so nothing is lost or run twice.
  const recoverQueue = track(async () => {
    if (!qdir) return;
    let metas;
    try { metas = readdirSync(qsub("running")).filter((f) => f.endsWith(".md.json")); } catch { return; }
    for (const f of metas) {
      try {
        const m = JSON.parse(read(join(qsub("running"), f)) ?? "{}");
        const md = join(qsub("running"), f.slice(0, -5));
        if (m.fg) { queueMove(md, "ready"); rmSync(join(qsub("running"), f), { force: true }); continue; }
        const got = await client.session.get({ path: { id: m.child } });
        const fm = parsePacket(read(md))?.fm;
        if (got?.data) queueRunning.set(m.child, { id: f.slice(0, -8), role: m.role, title: m.title, started: Date.parse(m.started) || now(), serial: fm?.serial, fm });
        else if (got?.response?.status === 404) { queueMove(md, "ready"); rmSync(join(qsub("running"), f), { force: true }); }
      } catch { /* the next restart tries again */ }
    }
  });

  // The idle decision: continue, review, stop, or wait while background helpers work.
  const decide = async (id) => {
    const current = state.get(id) ?? fresh();
    state.set(id, current);
    if (current.busy || current.timer || current.sending) return;
    current.busy = true;
    current.recheck = false;
    try {
      const decision = await inspect(id, current, true);
      if (decision.ignore) { state.delete(id); sprint.set(id, { v: false, at: now() }); return; }
      let helpers = await helpersRunning(id);
      write({ title: decision.title, said: decision.said, busy: helpers > 0 });
      if (decision.reason) return stop(id, current, decision.reason);
      if (decision.local?.token) current.token = decision.local.token;
      current.via = decision.via;
      // The queue first: finished helpers go back to the loop, free width starts queued packets.
      if (!decision.retry && !decision.compact) {
        if (await deliverQueued(true, id)) return record(id, "running", "queue results delivered", current);
        if (await launchQueued(id)) helpers = await helpersRunning(id);
      }
      // Helpers still working: no continue; each result wakes the loop, the beat covers a lost one.
      if (helpers && !foreground() && !decision.retry && !decision.compact) {
        current.recheck = true;
        log(`${id} waiting: ${helpers} background helpers working; each result wakes the loop`);
        return record(id, "running", `${helpers} background helpers working; each result wakes the loop`, current);
      }
      plan(id, current, decision);
    } catch (e) {
      if (!keeperGlitch(e)) return stop(id, current, `keeper error: ${e?.message ?? e}`);
      current.recheck = true; // the next beat decides again
      log(`${id} keeper read failed on a connection glitch (${e?.message ?? e}); the next beat retries`);
    } finally {
      current.busy = false;
    }
  };

  // Snapshot every minute: keeper alive, the sprint session, busy state, todo progress.
  // null = the read failed (OpenCode just started, a big session): unknown, not "not ours",
  // and not cached (2026-09-26: after a restart that turned forge's and the factory's
  // sessions into strangers, and the restart's sprint command opened new ones).
  const isSprint = async (id) => {
    if (retired.has(id)) return false;
    const known = sprint.get(id);
    if (known && (known.v || now() - known.at < 10 * 60_000)) return known.v;
    let v = false;
    try {
      const got = await client.session.get({ path: { id } });
      const info = got?.data;
      if (!info) return got?.response?.status === 404 ? false : null; // deleted = not ours
      if (!info.parentID) {
        const msgs = (await client.session.messages({ path: { id } }))?.data;
        if (!Array.isArray(msgs)) return null;
        v = msgs.some(isCommand);
      }
    } catch { return null; }
    sprint.set(id, { v, at: now() });
    return v;
  };
  // After a restart nothing has idled yet: find this repo's latest sprint session
  // among the recent root sessions, so the popper can show it and GO it.
  let lastDiscover = 0;
  let discovering = null;
  const discover = () => (discovering ??= findSprint().finally(() => { discovering = null; }));
  const findSprint = async () => {
    if (status.session || now() - lastDiscover < 10 * 60_000) return;
    lastDiscover = now();
    try {
      const list = (await client.session.list())?.data ?? [];
      const recent = list.filter((s) => s?.id && !s.parentID)
        .sort((a, b) => (b.time?.updated ?? 0) - (a.time?.updated ?? 0)).slice(0, 6);
      for (const s of recent) {
        if (!(await isSprint(s.id))) continue;
        write({ session: s.id, title: s.title });
        snapDirty = true; // the sprint session was (re)discovered: census it
        return log(`${s.id} found the sprint session "${clip(s.title ?? "", 60)}"`);
      }
    } catch { /* discovery is best effort */ }
  };
  // The remembered session must still be a current sprint session; else forget it.
  let checked = false;
  const recheck = async () => {
    if (checked || !status.session) return;
    checked = true;
    const v = await isSprint(status.session);
    if (v === null) { checked = false; return; } // could not read it: keep it, ask again next beat
    if (v) return;
    log(`${status.session} is not a current /sprint session any more; looking for one`);
    write({ session: undefined, title: undefined, todo: undefined, said: undefined, decision: undefined, reason: undefined });
    snapDirty = true; // the remembered session was forgotten: census the clean slate
  };
  const beat = track(async () => {
    if (gone) return;
    await recheck();
    await discover();
    for (const [id, b] of busy) {
      if (!(await isSprint(id))) continue;
      const st = state.get(id);
      const quiet = now() - live.at;
      if (live.question) record(id, "waiting for the owner", `open prompt: ${clip(live.question, 80)}`, st);
      else if (quiet > SILENT_MS) {
        if (!b.silent) log(`${id} silent: busy but no session event for ${ago(quiet)}`);
        b.silent = true;
        record(id, "silent", `busy but no session event for ${ago(quiet)}: a hung tool, subagent or provider`, st);
      } else record(id, "running", b.retry ? `provider retry: ${b.retry}` : `busy, last event ${ago(quiet)} ago`, st);
    }
    const snap = { alive: iso(), busy: status.session ? busy.has(status.session) : false };
    if (fixes.total) snap.shellFixes = { ...fixes, last: fixLast };
    if (calls.backgrounded || calls.todoFilled || calls.routed || calls.resultAsked || calls.delegated || calls.queued || calls.packets || calls.foregrounded || calls.timeoutRaised || calls.repeatHeld || calls.paidRouted || calls.heavyQueued || calls.adhocStopped || calls.claimsRouted || calls.navHinted || calls.subHelpers || calls.subCapHeld) snap.callFixes = { ...calls };
    // The queue acts every beat (a stuck helper aborts, free width fills,
    // finished results go out); the census below only runs when a decision
    // dirtied it, so an idle beat costs no session API call and no queue scan.
    // write() merges: a clean beat keeps the last decision's census keys.
    try { await tendQueue(); } catch (e) { log(`${status.session ?? "-"} queue: ${e?.message ?? e}`); }
    // Consumed after the tend above, so a launch, refusal, result or cap stop
    // this same beat takes is censused with it.
    const censused = snapDirty;
    snapDirty = false;
    if (censused && status.session) {
      try {
        const info = (await client.session.get({ path: { id: status.session } }))?.data;
        if (info?.title) snap.title = info.title;
        const todos = (await client.session.todo({ path: { id: status.session } }))?.data;
        if (Array.isArray(todos)) {
          const done = todos.filter((t) => t.status === "completed").length;
          const doing = todos.find((t) => t.status === "in_progress");
          snap.todo = todos.length ? `${done}/${todos.length} done${doing ? `, now: ${clip(doing.content, 70)}` : ""}` : null;
        }
        // Helpers: an orchestrator waiting on its Tasks looks idle in its own tab.
        const kids = (await client.session.children({ path: { id: status.session } }))?.data;
        if (Array.isArray(kids)) {
          const times = kids.map((k) => k?.time?.updated ?? 0);
          const active = times.filter((t) => now() - t < 3 * 60_000).length;
          const hour = times.filter((t) => now() - t < 60 * 60_000).length;
          const turns = (await client.session.status())?.data ?? {};
          const working = kids.filter((k) => k?.id && turns[k.id]?.type && turns[k.id].type !== "idle").length;
          snap.helpers = hour ? `${working ? `${working} helpers working, ` : ""}${active} helpers active now, ${hour} this hour` : null;
          // Background helpers keep the loop busy: a pause or a restart waits for them.
          if (working) snap.busy = true;
          const last = Math.max(0, ...times);
          if (last) snap.lastActivity = new Date(Math.max(last, live.at)).toISOString();
        }
      } catch { /* the snapshot is best effort */ }
    }
    if (censused && qdir) {
      snap.queue = { ready: queueCount("ready"), running: queueRunning.size, waiting: queueDone.length, done: queueCount("done"), failed: failedFresh().length };
      const team = queueCount("standing");
      if (team) snap.queue.standing = { packets: team, running: [...queueRunning.values()].filter((j) => j.standing).length, resting: [...standingRest.values()].filter((t) => t > now()).length };
      // Foreground: what the loop's batches do, for the popper (the last one sent, the one running, the next).
      if (foreground()) {
        snap.batch = { mode: "foreground", width: Number(knobValue("width")) || 0, running: fgJobs.size, sent: batchMeter.n,
          sentAt: batchMeter.startAt ? new Date(batchMeter.startAt).toISOString() : null, next: batchPlan()?.list.length ?? 0 };
      } else snap.batch = { mode: "queue" };
    }
    write(snap);
    // Nothing else wakes a loop whose helpers all ended without a result turn, or whose
    // continue met a new turn: once the session is idle and no helper works, decide again.
    const sid = status.session;
    const sst = sid && state.get(sid);
    // A keeper that never decided on its sprint session (after an OpenCode restart) whose session
    // sits idle: no idle event will come (forge 2026-09-27: the restart's GO met "already running",
    // the turn ended before the new keeper saw it, 47 min idle, a queue result undelivered). It
    // decides once; the decision reads halts, owner words and errors from disk and messages. A
    // stop the owner pressed stays until his GO.
    const unseen = !!sid && !sst && !retired.has(sid) && !(status.decision === "stopped" && /\bowner\b/.test(status.reason ?? ""));
    if (unseen || (sst?.recheck && !sst.timer && !sst.busy && !sst.sending && !sst.stopped)) {
      try {
        if ((await turnOf(sid)) !== "idle" || (!foreground() && (await helpersRunning(sid)))) return;
        // Only a finished reply: a message whose turn has not started yet is not a stop.
        const last = ((await client.session.messages({ path: { id: sid } }))?.data ?? []).at(-1);
        if (last?.info?.role !== "assistant" || !last.info.time?.completed) return;
        if (sst) sst.recheck = false;
        log(`${sid} idle with no helper working: ${sst ? "deciding again" : "this keeper never decided on it, deciding now"}`);
        await decide(sid);
      } catch { /* the next beat tries again */ }
    }
  });
  // After a hot reload: a continue the old body had waiting goes out on its old schedule.
  for (const [id, st] of state) {
    st.busy = false;
    st.sending = false;
    const due = st.rearm;
    st.rearm = null;
    if (due == null || st.stopped || !st.pending) continue;
    const d = st.pending;
    st.timer = setTimer(() => fire(id, st, d), Math.max(1_000, due - now()));
    st.timer?.unref?.();
  }
  intervals.push(every(() => beat().catch(() => {}), WATCH_MS));
  intervals.at(-1)?.unref?.();
  beat().catch(() => {});
  if (!opt.handover) recoverQueue().catch(() => {}); // recovered helpers are collected by the next beat

  // Popper and Empire Boss commands: GO = the owner's go for this repo's sprint session,
  // STOP = abort its turn, SPRINT = GO, or when no sprint session exists: a new session
  // running /sprint, NEW = a fresh sprint session in place of the current one.
  // A lock with no sprint session anywhere is orphaned, so that run uses `takeover`.
  const startSprint = async () => {
    const takeover = existsSync(here.lock);
    const startedAt = now();
    const created = (await client.session.create({ body: { title: `${cfg.repo} /sprint loop` } }))?.data;
    if (!created?.id) return "could not create a session";
    sprint.set(created.id, { v: true, at: now() });
    write({ session: created.id, title: created.title, decision: undefined, reason: undefined });
    // Not awaited: the command's first turn can run for hours.
    client.session.command({ path: { id: created.id }, body: { command: "sprint", arguments: takeover ? "takeover" : "" } })
      .catch((e) => log(`${created.id} ${now() - startedAt > 60_000 ? "the /sprint call timed out; the session keeps running" : `/sprint failed: ${e?.message ?? e}`}`));
    return `started /sprint${takeover ? " takeover" : ""} in a new session`;
  };
  // NEW: stop the old sprint session's turn, retire it, then a fresh session takes over the lock.
  const renew = async (id) => {
    if (id) {
      const turn = async () => (await client.session.status())?.data?.[id]?.type ?? "idle";
      if ((await turn()) !== "idle") {
        await client.session.abort({ path: { id } });
        for (let i = 0; i < 30 && (await turn()) !== "idle"; i++) await sleep(1_000);
        if ((await turn()) !== "idle") return "the old sprint session did not stop in 30s; nothing started";
      }
      retired.add(id);
      const st = state.get(id);
      if (st?.timer) clearTimer(st.timer);
      state.delete(id);
      busy.delete(id);
      sprint.set(id, { v: false, at: now() });
      write({ retired: [...retired].slice(-10) });
      log(`${id} retired: a fresh sprint session replaces it`);
    }
    return `${id ? `retired ${id}, ` : ""}${await startSprint()}`;
  };
  const goText = (from) => (typeof from === "string" && /^[a-z][a-z ]{0,29}$/i.test(from) ? `GO (from the ${from})` : POPPER_GO);
  // A stop the OpenCode restart sent (its --max-wait ran out) is the restart's, not the owner's
  // (2026-09-27: each restart left "the owner pressed stop" on the cards until its GO took).
  let restartStop = null;
  const abortReason = (id) => (restartStop?.id === id && now() - restartStop.at < 2 * 60_000 ? "stopped for the OpenCode restart" : "the owner pressed stop");
  // Say: send one tagged message into another OpenCode chat via center's chat-say.mjs.
  // Only the CENTER keeper handles it; others answer "say: only center". Same 2-minute
  // staleness as other commands. Never a permission or question answer: sayInto sends a
  // plain tagged text prompt, never a prompt reply.
  const handleSay = async (cmd, target) => {
    if (!isCenterKeeper()) return "only center";
    if (!opt.sayInto) {
      const js = sayJs();
      if (!js || !existsSync(js)) return "center not found";
    }
    const text = String(cmd.text ?? "").trim();
    // A batch (popper "Close out all"): {cmd:"say", id:"batch-..", ids:[...], text} sends the same text into each, max 20.
    const list = [...new Set([target, ...(Array.isArray(cmd.ids) ? cmd.ids : [])].filter((x) => typeof x === "string" && x.startsWith("ses_")))].slice(0, 20);
    if (!list.length || !text) return "NOT SENT: need a session id and a text";
    try {
      const sayInto = opt.sayInto ?? (await import(pathToFileURL(sayJs()).href)).sayInto;
      if (typeof sayInto !== "function") return "center not found";
      const out = [];
      for (const one of list) {
        const r = await sayInto({
          client, id: one, text, own: status.session, ...(cmd.force === true ? { force: true } : {}),
          ...(opt.sayDb !== undefined ? { db: opt.sayDb } : {}),
          ...(cmd.db !== undefined ? { db: cmd.db } : {}),
          ...(opt.sayIds !== undefined ? { ids: opt.sayIds } : {}),
          ...(opt.sayLog !== undefined ? { log: opt.sayLog } : {}),
        });
        out.push({ one, r });
      }
      if (list.length === 1) {
        const { r } = out[0];
        if (r?.ok) return `SENT to ${r.id ?? list[0]}${r.repo ? ` (${r.repo})` : ""}${r.reply ? `: ${clip(r.reply, 120)}` : ""}`;
        return `NOT SENT: ${r?.reason ?? "refused"}`;
      }
      const bad = out.filter((x) => !x.r?.ok);
      return `SENT ${out.length - bad.length} of ${out.length}${bad.length ? `; not: ${clip(bad.map((x) => `${x.one}: ${x.r?.reason ?? "refused"}`).join("; "), 200)}` : ""}`;
    } catch (e) { return `NOT SENT: send failed: ${e?.message ?? e}`; }
  };
  // Chat: one NEW chat in center with a first prompt (2026-10-04, the Loop Boss "Send problems to Muse" button on the
  // desktop app: the app's server answers 401 to anything outside, the keeper runs inside it). Only the CENTER keeper
  // handles it. {cmd:"chat", id, title, text, agent?, model?: { providerID, modelID }}. Never a sprint: a plain chat.
  const handleChat = async (cmd) => {
    if (!isCenterKeeper()) return "only center";
    const text = String(cmd.text ?? "").trim();
    if (!text) return "NOT SENT: need a text";
    try {
      const created = (await client.session.create({ body: { title: clip(String(cmd.title ?? "Loop Boss chat"), 80) } }))?.data;
      if (!created?.id) return "NOT SENT: the chat was not created";
      const model = cmd.model?.providerID && cmd.model?.modelID ? { providerID: String(cmd.model.providerID), modelID: String(cmd.model.modelID) } : null;
      await client.session.promptAsync({ path: { id: created.id }, body: { ...(typeof cmd.agent === "string" && cmd.agent ? { agent: cmd.agent } : {}), ...(model ? { model } : {}), parts: [{ type: "text", text }] } });
      return `CHAT ${created.id}`;
    } catch (e) { return `NOT SENT: ${e?.message ?? e}`; }
  };
  const handleArchive = async (cmd, target) => {
    if (!isCenterKeeper()) return "only center";
    if (!opt.archiveChat) {
      const js = archiveJs();
      if (!js || !existsSync(js)) return "center not found";
    }
    const list = [...new Set([target, ...(Array.isArray(cmd.ids) ? cmd.ids : [])].filter((x) => typeof x === "string" && x.startsWith("ses_")))].slice(0, 100);
    if (!list.length) return "NOT ARCHIVED: need a session id";
    try {
      const archiveChat = opt.archiveChat ?? (await import(pathToFileURL(archiveJs()).href)).archiveChat;
      if (typeof archiveChat !== "function") return "center not found";
      const done = [], not = [];
      for (const one of list) {
        const r = await archiveChat({
          client, id: one, own: status.session, why: String(cmd.why ?? "popper"),
          ...(opt.sayDb !== undefined ? { db: opt.sayDb } : {}),
          ...(opt.sayIds !== undefined ? { ids: opt.sayIds } : {}),
          ...(opt.sayLog !== undefined ? { log: opt.sayLog } : {}),
        });
        if (r?.ok) done.push(`${one}${r.repo ? ` (${r.repo})` : ""}`); else not.push(`${one}: ${r?.reason ?? "refused"}`);
      }
      if (list.length === 1) return done.length ? `ARCHIVED ${done[0]}` : `NOT ARCHIVED: ${not[0].replace(/^[^:]+: /, "")}`;
      return `ARCHIVED ${done.length} of ${list.length}${not.length ? `; not: ${clip(not.join("; "), 200)}` : ""}`;
    } catch (e) { return `NOT ARCHIVED: ${e?.message ?? e}`; }
  };
  let cmdSeen = ho.cmdSeen !== undefined ? ho.cmdSeen : read(here.cmd); // a command written before this keeper started is never run
  const command = track(async () => {
    if (gone) return;
    const raw = read(here.cmd);
    if (raw === null || raw === cmdSeen) return;
    cmdSeen = raw;
    let cmd;
    try { cmd = JSON.parse(raw); } catch { return; }
    const action = cmd.action ?? cmd.cmd;
    const atMs = typeof cmd.at === "number" ? cmd.at : Date.parse(cmd.at);
    const target = cmd.target ?? cmd.sessionId ?? cmd.sessionID ?? ((action === "say" || action === "archive") && typeof cmd.id === "string" && cmd.id.startsWith("ses_") ? cmd.id : null)
      ?? ((action === "archive" || action === "say") && Array.isArray(cmd.ids) ? cmd.ids[0] ?? null : null);
    const commandId = target && cmd.id === target ? `${cmd.at ?? ""}:${target}:${cmd.text ?? ""}` : cmd.id;
    if (!cmd?.id || !action || commandId === status.lastCommand || !(now() - atMs < CMD_MAX_AGE_MS)) return;
    write({ lastCommand: commandId });
    snapDirty = true; // a fresh popper command (GO/STOP/SPRINT/NEW): the next beat censuses
    const id = status.session;
    const answer = (text) => { log(`${id ?? "-"} popper ${action}: ${text}`); write({ command: `${action}: ${text}`, commandAt: iso() }); };
    if (!SUPPORTED_COMMANDS.includes(action)) return answer("unknown command");
    if (action === "say") return answer(await handleSay(cmd, target));
    if (action === "archive") return answer(await handleArchive(cmd, target));
    if (action === "chat") return answer(await handleChat(cmd));
    try {
      const info = id ? (await client.session.get({ path: { id } }))?.data : null;
      if (action === "new") return answer(await renew(info ? id : null));
      // sprint = GO the sprint session, or open one when this repo has none.
      if (!info && action === "sprint") return answer(await startSprint());
      if (!info) return answer(id ? "the sprint session is gone; press Start in the popper or run /sprint" : `no sprint session known yet; press Start in the popper or run /sprint in ${cfg.repo} once`);
      const running = (await client.session.status())?.data?.[id]?.type;
      if (action === "stop") {
        const idle = !running || running === "idle";
        const helpers = await helpersRunning(id);
        if (idle && !helpers) return answer("nothing to stop, the session is idle");
        restartStop = cmd.from === "OpenCode restart" ? { id, at: now() } : null;
        // The abort also cancels the session's background helpers (OpenCode 1.18.29); queued
        // helpers are sessions of their own, so each gets its abort too.
        await client.session.abort({ path: { id } });
        for (const child of queueRunning.keys()) { try { await client.session.abort({ path: { id: child } }); } catch { /* gone */ } }
        if (idle) {
          // No turn ran, so no abort error arrives: record the owner's stop here.
          const st = state.get(id) ?? fresh();
          if (st.consent == null) {
            const msgs = (await client.session.messages({ path: { id } }))?.data ?? [];
            st.consent = keyOf(msgs.findLast(isOwner), msgs);
          }
          state.set(id, st);
          stop(id, st, abortReason(id));
        }
        return answer(helpers ? `aborted ${idle ? "" : "the running turn and "}${helpers} background helpers` : "aborted the running turn");
      }
      if (running && running !== "idle") return answer("already running");
      if (state.get(id)?.timer) return answer("a continue is already waiting");
      const msgs = (await client.session.messages({ path: { id } }))?.data ?? [];
      const goLast = msgs.length ? keyOf(msgs.at(-1), msgs) : null;
      await reload();
      // The GO carries the keeper's facts (a bare GO met "holding at 14/15" twice, factory 2026-09-27).
      const command = commandNews();
      const facts = [command?.text, ...Object.values(stateNotes(await helpersRunning(id), localStatus(state.get(id))))].filter(Boolean);
      const go = facts.length ? `${goText(cmd.from)}\n${KEEPER} Facts: ${facts.join(" ")}` : goText(cmd.from);
      // Same stale-continue guard as the continue above: a newer message since
      // the GO was read means someone already moved the session; skip the send.
      try {
        const cur = (await client.session.messages({ path: { id } }))?.data ?? [];
        const curLast = cur.length ? keyOf(cur.at(-1), cur) : null;
        if (goLast && curLast && curLast !== goLast) return answer(`stale-continue skipped: a newer message appeared after ${goLast}; GO not sent`);
      } catch { /* a failed re-read sends as planned */ }
      await client.session.promptAsync({ path: { id }, body: bodyFor(viaOf(msgs.findLast(isOwner)), go) });
      if (command) write({ commandSeen: command.at });
      return answer(`sent GO to the sprint session${facts.length ? ` with ${facts.length} facts` : ""}`);
    } catch (e) { return answer(`failed: ${e?.message ?? e}`); }
  });
  intervals.push(every(() => command().catch(() => {}), CMD_POLL_MS));
  intervals.at(-1)?.unref?.();

  // Retire: stop this body's intervals and timers and hand its memory to the next body. A
  // waiting continue keeps its due time (rearm); an instance reload drops the memory.
  const retire = () => {
    gone = true;
    for (const h of intervals) clearInterval(h);
    for (const st of state.values()) {
      if (!st.timer) continue;
      clearTimer(st.timer);
      st.timer = null;
      st.rearm = st.pending ? st.dueAt ?? now() : null;
    }
    return { state, busy, sprint, live, queueRunning, queueDone, standingRest, standingNoops, adhocRest, adhocSeen, standingRuns, standingLast, capStops, fgJobs, adhocRun, batchMeter, readySeen, readyPending, fixes, calls, fixLast, cmdSeen, loadedAt, freshCtxAt };
  };
  const quiet = () => inflight === 0 && ![...state.values()].some((st) => st.busy || st.sending);

  const hooks = {
    // Every session of this repo, helpers too. Must never throw or slow a call.
    "tool.execute.before": async (input, output) => {
      try {
        const args = output?.args;
        if (input?.tool === "todowrite" && Array.isArray(args?.todos)) {
          let filled = false;
          for (const t of args.todos) {
            if (!t || typeof t !== "object") continue;
            for (const [k, v] of Object.entries(TODO_DEFAULTS)) if (t[k] == null) { t[k] = v; filled = true; }
          }
          if (filled) calls.todoFilled += 1;
          return;
        }
        if (input?.tool === "task" && args) {
          const sprintV = await isSprint(input.sessionID);
          // A helper sending its own helpers: at most SUB_HELPERS_MAX at once (the 11th waits as a BLOCKED line).
          if (!sprintV && input.callID && (await parentOf(input.sessionID))) {
            if (subRunning(input.sessionID) >= SUB_HELPERS_MAX) {
              args.prompt = `This helper already runs ${SUB_HELPERS_MAX} helpers of its own (the cap). Do nothing else; reply with one line: RESULT: BLOCKED - helper cap ${SUB_HELPERS_MAX} reached, send it after one returns | proof: the keeper`;
              calls.subCapHeld = (calls.subCapHeld ?? 0) + 1;
              return log(`${input.sessionID} sub-helper cap: ${SUB_HELPERS_MAX} running, held ${clip(String(args.description ?? ""), 60)}`);
            }
            if (subRun.size > 500) subRun.delete(subRun.keys().next().value);
            subRun.set(input.callID, input.sessionID);
            calls.subHelpers = (calls.subHelpers ?? 0) + 1;
            return;
          }
          // Owner chats are never capped (Maxim 2026-10-03: the cap cut 24 of his fix agents at 15 min).
          if (!sprintV) return;
          const fg = foreground();
          if (fg) {
            if (args.background === true) { args.background = false; calls.foregrounded = (calls.foregrounded ?? 0) + 1; }
            if (now() - batchMeter.at > BATCH_GAP_MS) Object.assign(batchMeter, { last: batchMeter.n, n: 0, startAt: now() });
            batchMeter.n += 1;
            batchMeter.at = now();
            const ref = qdir && typeof args.prompt === "string" ? args.prompt.match(PACKET_REF) : null;
            if (ref) {
              // A retried message (OpenCode sends a turn again after a stream error) sends its batch
              // again, while the first try's helpers run on as orphans and its packets are taken
              // (factory 2026-09-28 14:34: 13 helpers ran twice for 24 min). More calls of a packet
              // than it has copies is that retry: the new call takes the job over, the old helper stops.
              const same = [...fgJobs.entries()].filter(([c, j]) => c !== input.callID && j.sid === input.sessionID && j.ref === ref[1]);
              if (same.length && same.length >= (same[0][1].copies ?? 1)) {
                const [oldCall, old] = same.sort((x, y) => x[1].started - y[1].started)[0];
                fgJobs.delete(oldCall);
                try {
                  const kids = (await client.session.children({ path: { id: old.sid } }))?.data ?? [];
                  const child = kids.filter((k) => k?.title === `${old.desc} (@${old.sub ?? old.role} subagent)`)
                    .sort((x, y) => Math.abs((x.time?.created ?? 0) - old.started) - Math.abs((y.time?.created ?? 0) - old.started))[0];
                  if (child?.id) await client.session.abort({ path: { id: child.id } });
                } catch { /* it may be gone */ }
                args.subagent_type = old.sub ?? old.role;
                args.description = old.desc;
                args.prompt = old.text;
                fgJobs.set(input.callID, { ...old, started: now() });
                calls.retried = (calls.retried ?? 0) + 1;
                snapDirty = true; // a retried batch takes its job over: the next beat censuses
                return log(`${input.sessionID} batch: ${old.id} sent again (a retried message): the new call takes it over, the earlier helper stopped`);
              }
              const job = takeGroup(ref[1], input.sessionID);
              if (!job.text) {
                args.prompt = `The loop sent \`packet: ${ref[1]}\`, but ${job.why}. Do nothing else; reply with one line: RESULT: BLOCKED - ${job.why} | proof: the keeper`;
                return log(`${input.sessionID} batch: packet ${ref[1]} not started (${job.why})`);
              }
              const sub = paidOf(job.role);
              args.subagent_type = sub;
              if (sub !== job.role) calls.paidRouted = (calls.paidRouted ?? 0) + 1;
              args.description = String(args.description ?? "").trim() || job.title;
              args.prompt = job.text;
              if (input.callID) fgJobs.set(input.callID, { ...job, sub, ref: ref[1], copies: job.standing ? Math.max(1, Number(job.fm?.copies) || 1) : 1, desc: args.description, group: job.group?.map((j) => ({ ...j, text: undefined })) });
              calls.packets = (calls.packets ?? 0) + 1;
              return log(`${input.sessionID} batch: started ${job.id} as ${job.role} (live)`);
            }
          }
          const named = String(args.description ?? "").trim().split(/[\s:]+/)[0].toLowerCase();
          if (args.subagent_type === "general" && roles.has(named)) {
            args.subagent_type = named;
            calls.routed += 1;
          }
          const capHit = capStopped(adhocKey(args.subagent_type, args.description));
          if (capHit) {
            args.prompt = `The loop sent this Task again, but the same Task (role and title) was stopped at the ${Number(knobValue("helper_max_min")) || 90} min cap ${capHit.n} times in 12 h. The keeper holds it: split it into Tasks of half the size or replan it under a new title. Do nothing else; reply with one line: RESULT: BLOCKED - stopped at the cap ${capHit.n} times | proof: the keeper`;
            calls.capHeld = (calls.capHeld ?? 0) + 1;
            return log(`${input.sessionID} cap held: ${clip(String(args.description ?? ""), 60)} was stopped at the cap ${capHit.n} times in 12 h`);
          }
          const repeat = adhocRest.get(repeatKey(args));
          if (repeat && repeat.until > now()) {
            args.prompt = `The loop sent this Task again, but the same Task (role, title and prompt) ended NOOP ${ago(now() - repeat.at)} ago, ${repeat.noops} time(s) in a row, and nothing changed since. The keeper holds it until ${new Date(repeat.until).toISOString().slice(11, 16)}Z. Do nothing else; reply with one line: RESULT: BLOCKED - repeat of a NOOP | proof: the keeper`;
            calls.repeatHeld = (calls.repeatHeld ?? 0) + 1;
            return log(`${input.sessionID} repeat held: ${clip(String(args.description ?? ""), 60)} ended NOOP ${repeat.noops}x in a row, held until ${new Date(repeat.until).toISOString().slice(11, 16)}Z`);
          }
          if (!PACKET_REF.test(String(args.prompt ?? ""))) {
            const sends = noteDispatch(repeatKey(args));
            const cap = repeatCap();
            if (sends >= cap) {
              args.prompt = `The loop sent this Task again, but the same Task (role, title and prompt) was dispatched ${sends} times in the last 3 h (cap ${cap}). The keeper holds repeats for 3 h: send one fresh packet with a new title, or fix the pattern that makes it repeat. Do nothing else; reply with one line: RESULT: BLOCKED - repeat dispatch ${sends}x in 3 h | proof: the keeper`;
              calls.repeatHeld = (calls.repeatHeld ?? 0) + 1;
              return log(`${input.sessionID} repeat held: ${clip(String(args.description ?? ""), 60)} dispatched ${sends}x in 3 h (cap ${cap})`);
            }
          }
          if (input.callID) {
            if (adhocCalls.size > 200) adhocCalls.delete(adhocCalls.keys().next().value);
            adhocCalls.set(input.callID, repeatKey(args));
          }
          const paid = paidOf(args.subagent_type);
          if (paid !== args.subagent_type) { args.subagent_type = paid; calls.paidRouted = (calls.paidRouted ?? 0) + 1; }
          if (input.callID) {
            if (adhocRun.size > 200) adhocRun.delete(adhocRun.keys().next().value);
            adhocRun.set(input.callID, { sid: input.sessionID, desc: String(args.description ?? ""), sub: String(args.subagent_type ?? ""), proof: PROOF_TEXT.test(String(args.prompt ?? "")), started: now() });
          }
          if (typeof args.prompt === "string" && !GATE.test(String(args.subagent_type ?? "")) && !/^\s*`?RESULT:/m.test(args.prompt)) {
            args.prompt += RESULT_ASK;
            calls.resultAsked += 1;
          }
          if (!fg && background && args.background == null && !FOREGROUND.test(String(args.subagent_type ?? ""))) {
            args.background = true;
            calls.backgrounded += 1;
          }
          return;
        }
        if (input?.tool === "read" && isRootClaims(args?.filePath)) {
          args.filePath = claimsPath();
          calls.claimsRouted = (calls.claimsRouted ?? 0) + 1;
          return;
        }
        if (input?.tool === "bash" && typeof args?.command === "string" && BUILD_CMD.test(args.command) && !(Number(args.timeout) >= BUILD_TIMEOUT_MS)) {
          args.timeout = BUILD_TIMEOUT_MS;
          calls.timeoutRaised = (calls.timeoutRaised ?? 0) + 1;
        }
        if (!pwsh || input?.tool !== "bash" || typeof args?.command !== "string") return;
        const { out, hit } = shellFix(args.command, args.workdir);
        if (hit.length) {
          for (const k of hit) fixes[k] = (fixes[k] ?? 0) + 1;
          fixes.total += 1;
          fixLast = [{ at: iso(), from: clip(args.command, 120), to: clip(out, 120) }, ...fixLast].slice(0, 3);
          args.command = out;
        }
        // Heavy commands wait for a machine-wide slot (see HEAVY_WAIT_MS). The whole command rides inside the wrapper as base64,
        // so quoting, pipes and `cd` behave as they did; the wrapper runs it with the same pwsh flags and forwards the exit code.
        if (BUILD_CMD.test(args.command) && !/HEAVY_CMD_B64|KEEPER_NO_HEAVY/.test(args.command) && heavyOn()) {
          const b64 = Buffer.from(args.command, "utf8").toString("base64");
          if (b64.length <= HEAVY_B64_MAX) {
            args.command = `$env:HEAVY_CMD_B64='${b64}'; node '${heavyJs()}' run --repo ${cfg.repo}; exit $LASTEXITCODE`;
            args.timeout = Math.max(Number(args.timeout) || 0, BUILD_TIMEOUT_MS + HEAVY_WAIT_MS);
            calls.heavyQueued = (calls.heavyQueued ?? 0) + 1;
          }
        }
      } catch (error) { if (String(error?.message).startsWith("Keeper readiness hold:")) throw error; /* other fixes stay best effort */ }
    },
    // A batch helper's result (see takePacket).
    "tool.execute.after": async (input, output) => {
      try {
        if (input?.tool === "glob" || input?.tool === "bash") navHint(input, output);
        if (input?.tool === "task" && input.callID) { adhocRun.delete(input.callID); subRun.delete(input.callID); }
        if (input?.tool === "task" && input.callID && fgJobs.has(input.callID)) {
          const out = output?.output;
          return collectForeground(input.callID, (typeof out === "string" ? out : JSON.stringify(out ?? "")).trim());
        }
        if (input?.tool === "task" && input.callID && adhocCalls.has(input.callID)) {
          const key = adhocCalls.get(input.callID);
          adhocCalls.delete(input.callID);
          const out = output?.output;
          if (/RESULT:\s*NOOP\b/.test(typeof out === "string" ? out : JSON.stringify(out ?? ""))) {
            const noops = (adhocRest.get(key)?.noops ?? 0) + 1;
            adhocRest.set(key, { at: now(), noops, until: now() + 30 * 2 ** Math.min(noops - 1, 2) * 60_000 });
            for (const [k, v] of adhocRest) if (v.until < now() - 3_600_000) adhocRest.delete(k);
          } else adhocRest.delete(key);
          return;
        }
      } catch { /* dispatch is best effort */ }
    },
    event: track(async ({ event }) => {
      if (gone) return;
      const props = event?.properties ?? {};
      const type = event?.type ?? "";
      if (type.startsWith("message.") || type.startsWith("session.")) live.at = now();
      if (type === "question.asked" || type === "permission.asked") {
        live.question = props.questions?.[0]?.question ?? props.title ?? props.permission ?? type;
      }
      if (type === "question.replied" || type === "question.rejected" || type === "permission.replied") live.question = null;
      const id = props.sessionID ?? props.info?.sessionID ?? (type === "session.deleted" ? props.info?.id : undefined);
      if (!id) return;
      if (retired.has(id)) return void busy.delete(id);
      if (type === "session.status") {
        if (props.status?.type === "idle") busy.delete(id);
        else busy.set(id, { ...busy.get(id), retry: props.status?.type === "retry" ? `${clip(props.status.message ?? "", 60)} (attempt ${props.status.attempt ?? "?"})` : null });
        return;
      }
      const st = state.get(id);
      // A queued helper ended: its result goes back to the loop, its width takes the next packet.
      if (queueRunning.has(id) && (type === "session.error" || (type === "session.idle"))) {
        busy.delete(id);
        await collectQueued(id, type === "session.error" ? `session error${props.error?.name ? `: ${props.error.name}` : ""}` : undefined);
        await launchQueued();
        await deliverQueued();
        return;
      }
      if (type === "session.error") {
        const err = props.error;
        // Transient: the idle check retries with backoff; a waiting continue re-checks anyway.
        if (isTransient(err)) return st && log(`${id} transient ${err.name}: the idle check decides the retry`);
        // A 400 or an overflow may be a full context: the idle check measures it and compacts.
        if (mayBeOverflow(err)) return st && log(`${id} ${err.name}${err.data?.statusCode ? ` ${err.data.statusCode}` : ""}: the idle check decides (full context?)`);
        let current = st;
        if (!current) {
          current = fresh();
          current.stopped = true;
          current.errorBeforeFirst = true;
          try {
            const msgs = (await client.session.messages({ path: { id } }))?.data ?? [];
            if (!msgs.some(isCommand)) return;
            current.consent = keyOf(msgs.findLast(isOwner), msgs);
            current.errorBeforeFirst = false;
          } catch { /* Fail closed if messages cannot be read. */ }
        }
        state.set(id, current);
        return stop(id, current, err?.name === "MessageAbortedError" ? abortReason(id) : `session error${err?.name ? `: ${err.name}` : ""}`);
      }
      if (type === "session.deleted") {
        if (st?.timer) clearTimer(st.timer);
        state.delete(id);
        busy.delete(id);
        sprint.delete(id);
        return;
      }
      // A new user message cancels a waiting continue; the turn it starts ends in an idle
      // that decides again (an owner word changes the consent there, a helper result does
      // not). Updates to known messages (OpenCode writes diff summaries onto them) do nothing.
      if (type === "message.updated" && props.info?.role === "user" && st?.timer &&
        !st.pending?.users?.has(props.info.id)) {
        clearTimer(st.timer);
        st.timer = null;
        st.recheck = true;
        return log(`${id} a new message arrived while the continue waited; the next idle decides`);
      }
      if (type !== "session.idle") return;
      busy.delete(id);
      await decide(id);
    }),
  };
  return { hooks, retire, quiet, log };
};

// ---- Hot reload (2026-09-27, Maxim: "fully autonomous evolving systems, AI can fix all in
// loops"). OpenCode loads a plugin once, so every keeper fix waited for an OpenCode restart that
// cut helpers. LoopKeeper is a small shell: it runs the keeper body and, when this file changed
// (settled 5 s), imports a fresh copy (a temp file of its own name: no module cache applies),
// waits for a moment when no call into the body runs, retires the old body and starts the new
// one with its memory. A file that fails to load is logged and the running code stays until the
// file changes again. Only a change to this shell or to HOOKS needs an OpenCode restart.
const RELOAD_MS = 15_000;
const RELOAD_SETTLE_MS = 5_000;
const RELOAD_FORCE_MS = 10 * 60_000; // a body never quiet this long is stuck: swap anyway
const HOOKS = ["event", "tool.execute.before", "tool.execute.after"];
const SELF = (() => { try { return fileURLToPath(import.meta.url); } catch { return null; } })();
const SELF_AT = Math.floor(mtime(SELF) ?? 0);
export const LoopKeeper = async (input, options) => {
  const opt = options ?? {};
  // Serve guard: `opencode serve` (:4096) already drives this sprint, so the desktop app's
  // sidecar server must not drive it a second time. Off unless serve mode is on AND this is
  // the desktop app's server. Before any state, timers, file writes or hooks.
  const serveFile = process.env.KEEPER_SERVE_MODE_FILE ?? join(homedir(), ".empire", "state", "serve-mode.json");
  const execPath = (process.env.KEEPER_EXEC_PATH ?? process.execPath ?? "").toLowerCase().replace(/\\/g, "/");
  const isDesktop = execPath.includes("@opencode-aidesktop") ||
    (execPath.includes("/programs/") && execPath.includes("opencode.exe") && !!process.versions?.electron);
  let serveOn = false;
  try { serveOn = JSON.parse(readFileSync(serveFile, "utf8"))?.on === true; } catch { serveOn = false; }
  if (serveOn && isDesktop) {
    (opt.log ?? console.error)("keeper off: serve mode is on and this is the desktop app's server");
    return {};
  }
  const repo = opt.cfg?.repo ?? CFG.repo;
  const every = opt.setInterval ?? setInterval;
  const self = opt.selfFile ?? SELF;
  const reg = opt.keepers ?? (globalThis.__loopKeepers ??= {});
  const bodies = opt.bodies ?? (globalThis.__loopKeeperBodies ??= {});
  // One keeper per repo: an instance reload calls this again while the module stays loaded; the
  // new keeper retires the old one and starts clean (its sessions are idle between rounds).
  const prev = reg[repo];
  if (typeof prev === "function") prev(); else prev?.retire?.();
  // The newest code this process holds for this repo, a hot-loaded one included.
  const mine = { make: makeKeeper, at: opt.selfFile ? Math.floor(mtime(self) ?? 0) : SELF_AT };
  let body = bodies[repo] && bodies[repo].at >= mine.at ? bodies[repo] : (bodies[repo] = mine);
  let cur = await body.make(input, opt);
  let loading = false;
  let gone = false;
  let waitingSince = 0;
  const check = async () => {
    const at = Math.floor(mtime(self) ?? 0);
    if (gone || loading || !at || at === body.at || Date.now() - at < RELOAD_SETTLE_MS) return;
    if (!cur.quiet()) {
      if (!waitingSince) { waitingSince = Date.now(); cur.log(`keeper code changed: it loads at the next quiet moment`); }
      if (Date.now() - waitingSince < RELOAD_FORCE_MS) return;
      cur.log(`keeper: no quiet moment in ${RELOAD_FORCE_MS / 60_000} min; loading the new code anyway`);
    }
    loading = true;
    try {
      const dir = opt.reloadDir ?? join(tmpdir(), "loop-keeper");
      mkdirSync(dir, { recursive: true });
      const copy = join(dir, `${repo}-${at}.mjs`);
      writeFileSync(copy, readFileSync(self));
      const make = (await import(pathToFileURL(copy).href))?.LoopKeeper?.make;
      if (typeof make !== "function") throw new Error("the new file has no LoopKeeper.make");
      if (!cur.quiet() && Date.now() - (waitingSince || Date.now()) < RELOAD_FORCE_MS) return; // a call came in during the import
      const memory = cur.retire();
      try { cur = await make(input, { ...opt, handover: memory }); } catch (e) {
        cur = await body.make(input, { ...opt, handover: memory });
        throw e;
      }
      body = bodies[repo] = { make, at };
      waitingSince = 0;
      cur.log(`keeper code reloaded without a restart (file of ${new Date(at).toISOString()})`);
      for (const f of readdirSync(dir)) if (f.startsWith(`${repo}-`) && f !== basename(copy)) { try { rmSync(join(dir, f), { force: true }); } catch { /* in use */ } }
    } catch (e) {
      body = bodies[repo] = { ...body, at }; // this version failed: wait for the next change
      waitingSince = 0;
      cur.log(`keeper reload failed, the running code stays: ${e?.message ?? e}`);
    } finally { loading = false; }
  };
  const timer = every(() => check().catch(() => {}), RELOAD_MS);
  timer?.unref?.();
  reg[repo] = { retire: () => { gone = true; clearInterval(timer); return cur.retire(); } };
  return Object.fromEntries(HOOKS.map((name) => [name, (...a) => cur.hooks[name]?.(...a)]));
};
LoopKeeper.make = makeKeeper;

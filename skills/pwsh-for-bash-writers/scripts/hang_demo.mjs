// Measure which ways of starting a long-lived program make a shell tool call hang.
//
// A tool call ends when pwsh has exited AND its output pipe is closed. A program that was started
// from the call and is still alive keeps a copy of that pipe open, so the call waits for the program.
// This script plays the tool: it runs pwsh with piped output, starts a child that lives LIFE seconds
// (then exits by itself), and prints how long the call took to exit and to close.
//
//   node scripts/hang_demo.mjs [LIFE_SECONDS]      (default 12; nothing is ever killed)
import { spawn } from "node:child_process";
import { mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const LIFE = Number(process.argv[2] ?? 12);
const dir = mkdtempSync(join(tmpdir(), "hang-demo-"));
const logOf = (k) => join(dir, `server-${k}.log`).replace(/\\/g, "/");
const child = `console.log(1);setTimeout(()=>{},${LIFE * 1000})`; // no quote characters: it is nested inside three quoting levels

const cases = [
  { name: "A  program | Select-Object -Last 1 (child inherits the pipe)", hangs: true,
    cmd: `node -e "require('child_process').spawn(process.execPath,['-e','${child}'],{detached:true,stdio:'ignore'}).unref(); console.log('started')" | Select-Object -Last 1` },
  { name: "B  Start-Process -NoNewWindow", hangs: true,
    cmd: `Start-Process -FilePath node -ArgumentList '-e','${child}' -NoNewWindow; 'started'` },
  { name: "C  Start-Process -RedirectStandardOutput/-Error (the obvious fix)", hangs: true,
    cmd: `Start-Process -FilePath node -ArgumentList '-e','${child}' -RedirectStandardOutput '${logOf('C')}' -RedirectStandardError '${logOf('C')}.err' -WindowStyle Hidden; 'started'` },
  { name: "D  Start-Process cmd.exe /c \"node ... > log 2>&1\" -WindowStyle Hidden", hangs: false,
    cmd: `Start-Process -FilePath cmd.exe -ArgumentList '/c','node -e "${child}" > "${logOf('D')}" 2>&1' -WindowStyle Hidden; 'started'` },
];

function run(c) {
  return new Promise((resolve) => {
    const t0 = Date.now();
    const p = spawn("pwsh", ["-NoLogo", "-NoProfile", "-NonInteractive", "-Command", c.cmd], { stdio: ["ignore", "pipe", "pipe"], windowsHide: true });
    let exitMs = null;
    p.stdout.on("data", () => {});
    p.stderr.on("data", () => {});
    p.on("exit", () => { exitMs = Date.now() - t0; });
    p.on("close", () => resolve({ ...c, exitMs, closeMs: Date.now() - t0 }));
  });
}

const results = await Promise.all(cases.map(run));
console.log(`child lives ${LIFE} s; a call that closes much sooner than that does not wait for it`);
for (const r of results) {
  const waited = r.closeMs - r.exitMs > (LIFE * 1000) / 2;
  console.log(`${waited ? "HANGS" : "ok   "} exit ${String(r.exitMs).padStart(6)} ms, pipe closed ${String(r.closeMs).padStart(6)} ms | ${r.name}`);
}
try { console.log(`log of case D: ${readFileSync(join(dir, "server-D.log"), "utf8").trim() || "(empty)"}`); } catch { /* none */ }

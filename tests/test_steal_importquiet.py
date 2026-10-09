# Steal port: royalpinto007/import-effects (MIT) -- https://github.com/royalpinto007/import-effects
# Pattern: assert_no_effects plus inspect_import import side effect gate. Fresh stdlib only rebuild, no donor code copied.
"""Import quiet gate for book2skill: every module must import with no stdout plus no stderr plus no new files."""
from __future__ import annotations
import ast
import os
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
MODULES = ("book2skill", "book2skill.audit", "book2skill.batch", "book2skill.build", "book2skill.cli", "book2skill.distill", "book2skill.eval", "book2skill.export", "book2skill.extract", "book2skill.gates", "book2skill.graders", "book2skill.index", "book2skill.make", "book2skill.refresh", "book2skill.split", "book2skill.split_chapters", "book2skill.__main__")
LIVE_SKIP_NOTICE = "live tests skipped"
ALLOW_WARN_DOTTED = ("warnings.warn",)
EXACT_FORBIDDEN = ("print", "open", "breakpoint", "exit", "quit", "eval", "exec", "input", "compile")
PREFIX_FORBIDDEN = ("os.system", "os.exec", "os.spawn", "os.popen", "os.remove", "os.unlink", "os.rmdir", "os.removedirs", "os.mkdir", "os.makedirs", "os.replace", "os.rename", "os.write", "os.truncate", "os.chmod", "subprocess.", "socket.", "shutil.", "sys.exit", "os._exit")
ATTR_FORBIDDEN = ("write_text", "write_bytes", "mkdir", "unlink", "touch", "rmtree", "mkstemp", "mkdtemp")
def _dotted_name(func):
    """Dotted name for a call func node, empty string when unknown."""
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        base = _dotted_name(func.value)
        if base:
            return base + "." + func.attr
        return func.attr
    return ""
def _is_main_guard(test):
    """True for the classic if name equals main guard."""
    if not isinstance(test, ast.Compare):
        return False
    if not isinstance(test.left, ast.Name):
        return False
    if test.left.id != "__name__":
        return False
    if len(test.ops) != 1:
        return False
    if not isinstance(test.ops[0], ast.Eq):
        return False
    if len(test.comparators) != 1:
        return False
    comp = test.comparators[0]
    if isinstance(comp, ast.Constant):
        return comp.value == "__main__"
    return False
class _TopLevelVisitor(ast.NodeVisitor):
    """Collect top level calls while skipping def plus class plus lambda bodies and the main guard."""
    def __init__(self):
        self.calls = []
    def visit_FunctionDef(self, node):
        return
    def visit_AsyncFunctionDef(self, node):
        return
    def visit_ClassDef(self, node):
        return
    def visit_Lambda(self, node):
        return
    def visit_If(self, node):
        if _is_main_guard(node.test):
            return
        self.generic_visit(node)
    def visit_Call(self, node):
        self.calls.append(node)
        self.generic_visit(node)
def _is_forbidden_dotted(dotted):
    """True when a dotted call name is a forbidden import time effect."""
    if dotted in ALLOW_WARN_DOTTED:
        return False
    if dotted in EXACT_FORBIDDEN:
        return True
    for prefix in PREFIX_FORBIDDEN:
        if dotted == prefix or dotted.startswith(prefix):
            return True
    attr = dotted.rsplit(".", 1)[-1] if dotted else ""
    if attr in ATTR_FORBIDDEN:
        return True
    if dotted in ("sys.stdout.write", "sys.stderr.write"):
        return True
    return False
def count_forbidden_top_level_effects(path):
    """List of file colon line colon dotted strings for forbidden top level calls in one file."""
    text = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))
    visitor = _TopLevelVisitor()
    visitor.visit(tree)
    hits = []
    for node in visitor.calls:
        dotted = _dotted_name(node.func)
        if _is_forbidden_dotted(dotted):
            hits.append(str(path) + ":" + str(getattr(node, "lineno", 0)) + ":" + dotted)
    return hits
def _child_env(extra=None):
    """Child env with bytecode writes off plus repo root on python path."""
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    root_str = str(ROOT)
    old = env.get("PYTHONPATH", "")
    if old:
        env["PYTHONPATH"] = root_str + os.pathsep + old
    else:
        env["PYTHONPATH"] = root_str
    if extra:
        for key, val in extra.items():
            env[key] = val
    return env
def inspect_import(modname, cwd, extra_env=None, timeout=60):
    """Run a fresh child interpreter importing one module and record stdout plus stderr plus new files."""
    target = Path(cwd)
    target.mkdir(parents=True, exist_ok=True)
    before = set(p.name for p in target.iterdir())
    proc = subprocess.run([sys.executable, "-c", "import " + modname], capture_output=True, text=True, cwd=str(target), env=_child_env(extra_env), timeout=timeout)
    after = [p for p in target.rglob("*") if p.is_file()]
    new_files = [str(p.relative_to(target)) for p in after if p.name not in before]
    return {"module": modname, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr, "new_files": sorted(new_files)}
def assert_no_effects(modname, cwd, extra_env=None, timeout=60):
    """Assert one module imports with no stdout plus no stderr plus no new files. Return the report dict."""
    rep = inspect_import(modname, cwd, extra_env=extra_env, timeout=timeout)
    assert rep["returncode"] == 0, "import failed for " + modname + " rc=" + str(rep["returncode"]) + " stderr=" + rep["stderr"][-500:]
    assert rep["stdout"] == "", "stdout on import for " + modname + " got=" + repr(rep["stdout"][:500])
    assert rep["stderr"] == "", "stderr on import for " + modname + " got=" + repr(rep["stderr"][:500])
    assert rep["new_files"] == [], "new files on import for " + modname + " got=" + repr(rep["new_files"][:5])
    return rep
def test_all_modules_import_quiet_live(tmp_path):
    """Every book2skill module imports quiet with live on, no stdout plus no stderr plus no files."""
    live_env = {"SKILL_LIVE": "1"}
    bad = []
    for idx, mod in enumerate(MODULES):
        cwd = tmp_path / ("quiet" + str(idx))
        rep = inspect_import(mod, cwd, extra_env=live_env)
        if rep["returncode"] != 0 or rep["stdout"] != "" or rep["stderr"] != "" or rep["new_files"] != []:
            bad.append(mod + " rc=" + str(rep["returncode"]) + " out=" + repr(rep["stdout"][:200]) + " err=" + repr(rep["stderr"][:200]) + " files=" + repr(rep["new_files"][:3]))
    assert bad == [], "noisy imports with SKILL_LIVE=1: " + "; ".join(bad)
    (tmp_path / "sharp").mkdir(exist_ok=True)
    assert_no_effects("book2skill.extract", tmp_path / "sharp", extra_env=live_env)
    assert_no_effects("book2skill.cli", tmp_path / "sharp2", extra_env=live_env)
def test_default_mode_only_known_warning(tmp_path):
    """Without live on, the only allowed stderr is the known live skip notice, still no stdout plus no files."""
    rep = inspect_import("book2skill.gates", tmp_path / "default")
    assert rep["returncode"] == 0, "gates import failed rc=" + str(rep["returncode"])
    assert rep["stdout"] == "", "stdout on gates import got=" + repr(rep["stdout"][:200])
    assert rep["new_files"] == [], "new files on gates import got=" + repr(rep["new_files"][:3])
    if rep["stderr"] != "":
        assert LIVE_SKIP_NOTICE in rep["stderr"], "unexpected stderr on gates import got=" + repr(rep["stderr"][:500])
def test_no_forbidden_top_level_effects():
    """Static gate, zero forbidden top level calls across all book2skill files."""
    hits = []
    for name in os.listdir(ROOT / "book2skill"):
        if not name.endswith(".py"):
            continue
        hits.extend(count_forbidden_top_level_effects(ROOT / "book2skill" / name))
    assert hits == [], "forbidden import time effects: " + "; ".join(hits)
    assert len(MODULES) >= 15
def test_gate_catches_noisy_control(tmp_path):
    """Control, the gate flags a noisy module so the zero above is not vacuous."""
    noisy_dir = tmp_path / "noisy_pkg"
    noisy_dir.mkdir()
    noisy_code = "import pathlib" + chr(10) + "print(" + chr(34) + "noisy-hello" + chr(34) + ")" + chr(10)
    noisy_code = noisy_code + "pathlib.Path(" + chr(34) + "pwned.txt" + chr(34) + ").write_text(" + chr(34) + "x" + chr(34) + ", encoding=" + chr(34) + "utf-8" + chr(34) + ")" + chr(10)
    (noisy_dir / "noisy_mod.py").write_text(noisy_code, encoding="utf-8")
    hits = count_forbidden_top_level_effects(noisy_dir / "noisy_mod.py")
    assert len(hits) >= 2, "control static gate missed noisy module got=" + repr(hits)
    before_cwd = tmp_path / "noisy_run"
    before_cwd.mkdir()
    env = _child_env({"PYTHONPATH": str(noisy_dir) + os.pathsep + str(ROOT)})
    proc = subprocess.run([sys.executable, "-c", "import noisy_mod"], capture_output=True, text=True, cwd=str(before_cwd), env=env, timeout=60)
    assert proc.returncode == 0
    assert proc.stdout != "" or proc.stderr != "" or list(before_cwd.rglob("*")) != [], "control runtime gate missed noisy module"
    assert "noisy-hello" in proc.stdout
def test_entry_guards_present():
    """cli plus main keep the classic main guard so import never runs the command."""
    cli_text = (ROOT / "book2skill" / "cli.py").read_text(encoding="utf-8")
    main_text = (ROOT / "book2skill" / "__main__.py").read_text(encoding="utf-8")
    assert "if __name__" in cli_text
    assert "__main__" in main_text
    assert "main()" in main_text

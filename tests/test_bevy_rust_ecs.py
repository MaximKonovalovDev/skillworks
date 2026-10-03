"""bevy-rust-ecs: the two Node scripts, the names in the code blocks, and the live checks of the evidence.

Offline tests (default run): fixture Cargo.toml files written into tmp_path, fixtures for the plugin
script, and a check that every Bevy name written in a ```rust block of SKILL.md or
references/viewer-recipe.md is listed in references/verified-api.md and that no removed name is used.
Live tests (SKILL_LIVE=1, they use `gh api` and the network): the plugin script against a real repo,
the pinned tag and commit, and every `file:line` row of verified-api.md against the tagged source.
"""
import json
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

import skill_gates as g
from skill_gates import live

SKILL = g.SKILLS / "bevy-rust-ecs"
CHECK = SKILL / "scripts" / "check-sim-outside-bevy.mjs"
PLUGIN = SKILL / "scripts" / "plugin-bevy-version.mjs"
REPO = "bevyengine/bevy"
TAG = "v0.19.1"

NODE = shutil.which("node")
GH = shutil.which("gh")
pytestmark = [
    pytest.mark.skipif(not (SKILL / "SKILL.md").is_file(), reason="skill not built yet"),
    pytest.mark.skipif(NODE is None, reason="node is not installed"),
]


def node(*args, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run([NODE, *map(str, args)], capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd, timeout=60)


# ---------------------------------------------------------------- check-sim-outside-bevy.mjs

WORKSPACE_ROOT = """\
[workspace]
members = ["crates/*"]

[workspace.dependencies]
bevy = { version = "0.19", default-features = false }
engine = { package = "bevy", version = "0.19" }
serde = "1"
"""

# name -> (Cargo.toml text, must fail, strings the output must contain)
CASES = {
    "plain_string": ('[package]\nname = "x"\n[dependencies]\nbevy = "0.19"\n', True, ['"bevy"']),
    "inline_table": ('[package]\nname = "x"\n[dependencies]\nbevy = { version = "0.19", default-features = false }\n', True, ['"bevy"']),
    "dep_table": ('[package]\nname = "x"\n[dependencies.bevy]\nversion = "0.19"\nfeatures = ["3d"]\n', True, ['"bevy"']),
    "dotted_key": ('[package]\nname = "x"\n[dependencies]\nbevy.version = "0.19"\n', True, ['"bevy"']),
    "dev_dependency": ('[package]\nname = "x"\n[dev-dependencies]\nbevy_ecs = "0.19"\n', True, ["[dev-dependencies]", '"bevy_ecs"']),
    "build_dependency": ('[package]\nname = "x"\n[build-dependencies]\nbevy-macro-utils = "1"\n', True, ["[build-dependencies]"]),
    "target_table": ('[package]\nname = "x"\n[target.\'cfg(windows)\'.dependencies]\nbevy = "0.19"\n', True, ["cfg(windows)"]),
    "target_dep_table": ('[package]\nname = "x"\n[target.\'cfg(unix)\'.dev-dependencies.bevy_app]\nversion = "0.19"\n', True, ['"bevy_app"']),
    "workspace_inherited": ('[package]\nname = "x"\n[dependencies]\nbevy = { workspace = true }\n', True, ['"bevy"']),
    "workspace_renamed_at_root": ('[package]\nname = "x"\n[dependencies]\nengine = { workspace = true }\n', True, ['"engine"', 'package "bevy"']),
    "package_rename": ('[package]\nname = "x"\n[dependencies]\nrender = { package = "bevy_render", version = "0.19" }\n', True, ['package "bevy_render"']),
    "multiline_inline": ('[package]\nname = "x"\n[dependencies]\nfoo = {\n  version = "1",\n  package = "bevy_math",\n}\n', True, ['package "bevy_math"']),
    "crlf_file": ('[package]\r\nname = "x"\r\n[dependencies]\r\nbevy = "0.19"\r\n', True, ['"bevy"']),
    "clean": ('[package]\nname = "x"\n[dependencies]\nserde = { workspace = true }\nrapier3d = "0.22"\n[dev-dependencies]\ncriterion = "0.5"\n', False, ["no bevy dependency"]),
    "bevy_only_in_text": ('[package]\nname = "x"\ndescription = "not a bevy crate, bevy = \\"0.19\\" is only text"\n[dependencies]\n# bevy = "0.19"\nserde = "1"\n', False, ["no bevy dependency"]),
    "package_named_bevy_but_no_deps": ('[package]\nname = "bevy_clean_lookalike"\n[dependencies]\nserde = "1"\n', False, ["no bevy dependency"]),
}


@pytest.fixture()
def ws(tmp_path: Path) -> Path:
    (tmp_path / "Cargo.toml").write_text(WORKSPACE_ROOT, encoding="utf-8")
    for name, (toml, _fail, _needles) in CASES.items():
        d = tmp_path / "crates" / name
        d.mkdir(parents=True)
        (d / "Cargo.toml").write_bytes(toml.encode("utf-8"))
    return tmp_path


@pytest.mark.parametrize("name", sorted(CASES))
def test_checker_cases(ws: Path, name: str) -> None:
    _toml, must_fail, needles = CASES[name]
    r = node(CHECK, ws / "crates" / name)
    assert r.returncode == (1 if must_fail else 0), r.stdout + r.stderr
    for n in needles:
        assert n in r.stdout, f"{name}: {n!r} missing from output:\n{r.stdout}"


def test_checker_lists_every_crate_and_fails_if_any_has_bevy(ws: Path) -> None:
    r = node(CHECK, ws / "crates" / "clean", ws / "crates" / "plain_string", ws / "crates" / "bevy_only_in_text")
    assert r.returncode == 1
    assert "FAIL" in r.stdout and "OK" in r.stdout
    assert r.stdout.count("plain_string") >= 1


def test_checker_accepts_a_cargo_toml_path(ws: Path) -> None:
    ok = node(CHECK, ws / "crates" / "clean" / "Cargo.toml")
    bad = node(CHECK, ws / "crates" / "plain_string" / "Cargo.toml")
    assert (ok.returncode, bad.returncode) == (0, 1)


def test_checker_expands_a_workspace_root_so_it_cannot_pass_by_accident(ws: Path) -> None:
    r = node(CHECK, ws)
    assert r.returncode == 1, r.stdout
    assert "workspace root" in r.stdout and "plain_string" in r.stdout
    clean = ws.parent / (ws.name + "_clean")
    (clean / "crates" / "one").mkdir(parents=True)
    (clean / "Cargo.toml").write_text('[workspace]\nmembers = ["crates/*"]\n', encoding="utf-8")
    (clean / "crates" / "one" / "Cargo.toml").write_text('[package]\nname = "one"\n[dependencies]\nserde = "1"\n', encoding="utf-8")
    assert node(CHECK, clean).returncode == 0


def test_checker_usage_and_missing_manifest(tmp_path: Path) -> None:
    assert node(CHECK).returncode == 2
    r = node(CHECK, tmp_path / "nothing-here")
    assert r.returncode == 2 and "cannot read" in r.stdout


# ---------------------------------------------------------------- plugin-bevy-version.mjs

MATCH_CASES = [
    ("0.19", "0.19.1", True), ("0.19.1", "0.19.1", True), ("^0.19.0", "0.19.1", True), ("=0.19.1", "0.19.1", True),
    ("~0.19", "0.19.1", True), ("0.19.*", "0.19.1", True), ("*", "0.19.1", True), (">=0.18, <0.20", "0.19.1", True),
    ("<=0.19", "0.19.1", True), ("0", "0.19.1", True),
    ("0.18", "0.19.1", False), ("0.20", "0.19.1", False), ("0.20.0-dev", "0.19.1", False), ("0.19.2", "0.19.1", False),
    (">=0.19.2", "0.19.1", False), (">0.19", "0.19.1", False), ("1", "0.19.1", False), ("=0.19.0", "0.19.1", False),
    ("git https://github.com/bevyengine/bevy", "0.19.1", None), ("not a version!", "0.19.1", None),
]

PLUGIN_TOML = """\
[package]
name = "some_plugin"

[dependencies]
bevy = { version = "0.19", default-features = false, features = ["bevy_render"] }
bevy_app = "0.19"
bevy-some-plugin-derive = "0.37"
serde = "1"

[dev-dependencies]
bevy = { git = "https://github.com/bevyengine/bevy" }
"""


def test_plugin_pure_functions(tmp_path: Path) -> None:
    (tmp_path / "cases.json").write_text(json.dumps({"match": MATCH_CASES, "toml": PLUGIN_TOML, "readme": README}), encoding="utf-8")
    (tmp_path / "h.mjs").write_text(
        "import fs from 'node:fs';\n"
        f"import {{ matchesBevy, readBevyRequirements, readCompatTable }} from {json.dumps(PLUGIN.as_uri())};\n"
        "const c = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));\n"
        "console.log(JSON.stringify({\n"
        "  match: c.match.map(([r, v]) => matchesBevy(r, v)),\n"
        "  reqs: readBevyRequirements(c.toml),\n"
        "  tables: readCompatTable(c.readme),\n"
        "}));\n",
        encoding="utf-8",
    )
    r = node(tmp_path / "h.mjs", tmp_path / "cases.json")
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["match"] == [m[2] for m in MATCH_CASES]
    reqs = {(x["label"], x["name"]): x["req"] for x in out["reqs"]}
    assert reqs[("[dependencies]", "bevy")] == "0.19"
    assert reqs[("[dependencies]", "bevy_app")] == "0.19"
    assert reqs[("[dev-dependencies]", "bevy")].startswith("git ")
    assert ("[dependencies]", "serde") not in reqs
    assert len(out["tables"]) == 1 and out["tables"][0]["header"] == ["bevy", "some_plugin"]
    assert ["0.19", "0.5"] in out["tables"][0]["rows"]


README = """\
# some_plugin

Some text | with a pipe.

| bevy | some_plugin |
|------|-------------|
| 0.19 | 0.5         |
| 0.18 | 0.4         |

| feature | note |
|---------|------|
| a       | b    |
"""


@pytest.mark.parametrize(
    "toml, verdict",
    [
        ('[dependencies]\nbevy = "0.19"\n', "OK with bevy 0.19.1"),
        ('[dependencies]\nbevy = "0.18"\n', "MISMATCH with bevy 0.19.1"),
        ('[dependencies]\nbevy_app = "0.19"\nbevy_ecs = "0.20.0-dev"\n', "MISMATCH with bevy 0.19.1"),
        ('[dependencies]\nbevy = { git = "https://example.com/bevy" }\n', "UNKNOWN with bevy 0.19.1"),
        ('[dependencies]\nbevy-some-plugin-derive = "0.37"\nbevy = "0.19"\n', "OK with bevy 0.19.1"),  # a bevy-named sibling crate is not Bevy
        ('[dependencies]\nserde = "1"\n', "no bevy dependency found"),
    ],
)
def test_plugin_cli_offline(tmp_path: Path, toml: str, verdict: str) -> None:
    (tmp_path / "Cargo.toml").write_text(toml, encoding="utf-8")
    r = node(PLUGIN, "--file", tmp_path / "Cargo.toml")
    assert r.returncode == 0, r.stderr
    assert verdict in r.stdout, r.stdout


def test_plugin_cli_offline_readme_rows_and_target_version(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text('[dependencies]\nbevy = "0.19"\n', encoding="utf-8")
    (tmp_path / "README.md").write_text(README, encoding="utf-8")
    r = node(PLUGIN, "--file", tmp_path / "Cargo.toml", "--readme", tmp_path / "README.md")
    assert "1 row(s) mention 0.19" in r.stdout and "0.19 | 0.5" in r.stdout and "0.18 | 0.4" not in r.stdout
    other = node(PLUGIN, "--file", tmp_path / "Cargo.toml", "--bevy", "0.20.0")
    assert "MISMATCH with bevy 0.20.0" in other.stdout


def test_plugin_cli_usage() -> None:
    assert node(PLUGIN).returncode == 2


# ---------------------------------------------------------------- names in the code blocks

CODE_FILES = [SKILL / "SKILL.md", SKILL / "references" / "viewer-recipe.md"]
VERIFIED = SKILL / "references" / "verified-api.md"
GONE_HEADING = "## Names that do NOT exist"
# Rust and std names that are not Bevy.
STD_TYPES = set("Vec Option Some None Ok Err Result String Duration Default Self Clone Copy Debug Box Into From Iterator Send Sync Fn FnMut".split())
STD_CALLS = set("iter map collect len clone into cos sin from_millis take unwrap".split())
KEYWORDS = set("if while for match return fn let loop in else impl mod use pub struct enum trait where as move derive".split())
GONE_NAMES = [
    "SceneRoot", "SceneInstanceReady", "EventReader", "EventWriter", "Camera3dBundle", "PbrBundle", "SceneBundle",
    "DirectionalLightBundle", "MaterialMeshBundle", "get_single", "despawn_recursive", "add_event", "spawn_bundle",
    "play_with_transition",
]


def rust_code(path: Path) -> str:
    """The ```rust blocks of a markdown file with string literals and // comments removed."""
    blocks = re.findall(r"```rust\r?\n(.*?)```", path.read_text(encoding="utf-8"), re.S)
    out = []
    for block in blocks:
        for line in block.splitlines():
            clean, in_str, i = [], False, 0
            while i < len(line):
                c = line[i]
                if in_str:
                    if c == "\\":
                        i += 2
                        continue
                    if c == '"':
                        in_str = False
                        clean.append('""')
                elif c == '"':
                    in_str = True
                elif line.startswith("//", i):
                    break
                else:
                    clean.append(c)
                i += 1
            out.append("".join(clean))
    return "\n".join(out)


def verified_part() -> str:
    return VERIFIED.read_text(encoding="utf-8").split(GONE_HEADING)[0]


def listed(name: str, text: str) -> bool:
    return re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])", text) is not None


def used_names(code: str) -> tuple[set[str], set[str]]:
    """(CamelCase names, snake_case call names) of a code text, minus what the code defines itself."""
    defined = set(re.findall(r"\b(?:struct|enum|trait|type|fn|mod|const|static)\s+([A-Za-z_][A-Za-z0-9_]*)", code))
    camel = set(re.findall(r"\b[A-Z][a-z][A-Za-z0-9]*\b", code))
    calls = set(re.findall(r"\.([a-z_][a-z0-9_]*)\s*(?:::<[^>]*>)?\(", code))  # x.method(
    calls |= set(re.findall(r"::([a-z_][a-z0-9_]*)\s*\(", code))  # Type::function(
    calls |= set(re.findall(r"(?<![\w.:])([a-z_][a-z0-9_]*)\s*[!(]", code))  # function( and macro!
    return camel - defined - STD_TYPES, calls - defined - STD_CALLS - KEYWORDS


def test_code_blocks_exist() -> None:
    for f in CODE_FILES:
        assert rust_code(f).strip(), f"{f.name} has no ```rust block"


@pytest.mark.parametrize("path", CODE_FILES, ids=lambda p: p.name)
def test_every_bevy_name_in_the_code_is_verified(path: Path) -> None:
    text = verified_part()
    camel, calls = used_names(rust_code(path))
    missing = sorted(n for n in camel | calls if not listed(n, text))
    assert not missing, f"{path.name} uses names that verified-api.md does not list: {missing}"


@pytest.mark.parametrize("path", CODE_FILES, ids=lambda p: p.name)
def test_no_removed_name_in_the_code(path: Path) -> None:
    code = rust_code(path)
    used = [n for n in GONE_NAMES if listed(n, code)]
    assert not used, f"{path.name} uses names that do not exist in 0.19.1: {used}"
    assert not re.search(r":\s*Trigger<", code), "Trigger<..> is not an observer parameter in 0.19.1; use On<..>"


def test_removed_names_are_listed_in_the_not_exist_section() -> None:
    section = VERIFIED.read_text(encoding="utf-8").split(GONE_HEADING)[1]
    for n in GONE_NAMES:
        assert n in section, f"{n} should be listed under {GONE_HEADING}"


def test_verified_rows_have_a_path_and_a_line() -> None:
    rows = re.findall(r"^\| `([^`]+)` \| `([^`:]+):(\d+)` \|", VERIFIED.read_text(encoding="utf-8"), re.M)
    assert len(rows) >= 100, f"only {len(rows)} rows with file:line"
    assert all(int(line) > 0 for _item, _path, line in rows)


def test_qa_musts_literally_appear_in_the_skill_text() -> None:
    text = g.skill_text("bevy-rust-ecs").lower()
    for line in (g.ROOT / "evals" / "bevy-rust-ecs_qa.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        for m in row["must"]:
            assert m.lower() in text, f"must {m!r} is not in the skill text (question: {row['q']})"


def test_pin_is_the_same_in_every_file() -> None:
    sha = "b56fc29d3016e641754765244b5ba3f9cc504671"
    for f in ("references/verified-api.md", "references/sources.md"):
        t = (SKILL / f).read_text(encoding="utf-8")
        assert TAG in t and sha in t, f"{f} must name {TAG} and {sha}"
    assert "0.19.1" in (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "0.19.1" in (SKILL / "references" / "viewer-recipe.md").read_text(encoding="utf-8")


def test_no_private_paths_in_the_public_skill() -> None:
    for p in SKILL.rglob("*"):
        if p.is_file() and p.suffix in {".md", ".mjs"}:
            t = p.read_text(encoding="utf-8")
            assert not re.search(r"[A-Za-z]:\\Users\\|/Users/[a-z]|ghp_|github_pat_", t), f"{p.name} has a private path or token-like text"


# ---------------------------------------------------------------- live (network, gh)


def gh_raw(path: str, ref: str = TAG) -> str | None:
    r = subprocess.run(
        [GH, "api", "-H", "Accept: application/vnd.github.raw", f"repos/{REPO}/contents/{path}?ref={ref}"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
    )
    return r.stdout if r.returncode == 0 else None


needs_gh = pytest.mark.skipif(GH is None, reason="gh is not installed")

# item -> text that must be on the cited line, when the last name part of the item is not enough
LINE_KEYS = {"3d profile": "3d = [", "default features": "default = [", "PluginGroupBuilder::set": "pub fn set"}


@live
@needs_gh
def test_live_pinned_tag_still_points_at_the_pinned_commit() -> None:
    r = subprocess.run([GH, "api", f"repos/{REPO}/git/ref/tags/{TAG}", "--jq", ".object.sha"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    assert r.returncode == 0, r.stderr
    sha = r.stdout.strip()
    assert sha in (SKILL / "references" / "sources.md").read_text(encoding="utf-8")
    assert sha in VERIFIED.read_text(encoding="utf-8")


@live
@needs_gh
def test_live_every_cited_line_holds_the_cited_name() -> None:
    text = VERIFIED.read_text(encoding="utf-8")
    item_rows = re.findall(r"^\| `([^`]+)` \| `([^`:]+):(\d+)` \|", text, re.M)
    usage_rows = re.findall(r"^\| [^|]*\| `([^`:]+):(\d+)` \|$", text, re.M)
    files = sorted({p for _i, p, _l in item_rows} | {p for p, _l in usage_rows})
    with ThreadPoolExecutor(max_workers=8) as pool:
        fetched = dict(zip(files, pool.map(gh_raw, files)))
    problems = []
    for path, body in fetched.items():
        if body is None:
            problems.append(f"cannot fetch {path} at {TAG}")
    for item, path, line in item_rows:
        body = fetched.get(path)
        if body is None:
            continue
        lines = body.splitlines()
        n = int(line)
        if n > len(lines):
            problems.append(f"{path}:{n} is past the end of the file")
            continue
        key = LINE_KEYS.get(item) or re.split(r"::", item)[-1].replace("<", "").replace(">", "")
        if key not in lines[n - 1]:
            problems.append(f"{path}:{n} does not hold {key!r} (row {item}): {lines[n - 1].strip()[:80]!r}")
    for path, line in usage_rows:
        body = fetched.get(path)
        if body is not None and int(line) > len(body.splitlines()):
            problems.append(f"{path}:{line} is past the end of the file")
    assert not problems, "\n".join(problems[:20])


@live
@needs_gh
def test_live_plugin_script_reads_a_real_repo() -> None:
    r = node(PLUGIN, "djeedai/bevy_hanabi")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "default branch" in r.stdout and "VERDICT:" in r.stdout and "latest" in r.stdout
    assert "ghp_" not in r.stdout + r.stderr
    missing = node(PLUGIN, "no-such-owner-0xq/no-such-repo")
    assert missing.returncode == 2 and "ERROR" in missing.stdout

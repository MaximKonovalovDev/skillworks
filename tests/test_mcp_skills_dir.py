"""015: MCP serves out-of-tree skills dirs + unknown-skill names the served dir."""
import json
import os
import subprocess
import sys
from pathlib import Path


def _make_scratch_skills(base: Path) -> Path:
    skill = base / "scratch-demo"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: scratch-demo\ndescription: scratch demo skill\n---\n"
        "quetzal gateway lanes chat vision lease\n",
        encoding="utf-8",
    )
    return base


def _stdio_session(requests: list[dict], argv: list[str] | None = None,
                   env_dir: str | None = None) -> list[dict]:
    payload = "".join(json.dumps(r) + "\n" for r in requests)
    env = dict(os.environ)
    if env_dir is not None:
        env["SKILLWORKS_SKILLS_DIR"] = env_dir
    cmd = [sys.executable, "mcp_server/server.py"] + (argv or [])
    proc = subprocess.run(cmd, input=payload, capture_output=True, text=True,
                          timeout=30, env=env)
    assert proc.returncode == 0, proc.stderr
    return [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]


def _search_call(skill: str | None, query: str = "quetzal gateway lanes") -> dict:
    args: dict = {"query": query}
    if skill is not None:
        args["skill"] = skill
    return {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": "skill_search", "arguments": args}}


def test_out_of_tree_skill_served_via_env_override(tmp_path: Path) -> None:
    base = _make_scratch_skills(tmp_path / "extraskills")
    resps = _stdio_session([_search_call("scratch-demo")], env_dir=str(base))
    body = resps[0]["result"]["content"][0]["text"]
    assert "scratch-demo" in body and "quetzal" in body


def test_out_of_tree_skill_served_via_flag_and_unknown_names_dir(tmp_path: Path) -> None:
    base = _make_scratch_skills(tmp_path / "extraskills2")
    resps = _stdio_session([_search_call("scratch-demo")],
                           argv=["--skills-dir", str(base)])
    assert "scratch-demo" in resps[0]["result"]["content"][0]["text"]
    # unknown skill: isError envelope naming the skill + served dir
    resps2 = _stdio_session([_search_call("nope-missing-skill")],
                            argv=["--skills-dir", str(base)])
    bad = resps2[0]["result"]
    assert bad.get("isError") is True and bad.get("is_error") is True
    text = bad["content"][0]["text"]
    assert "unknown skill 'nope-missing-skill'" in text
    assert "serving 1 skills from" in text
    decoded = json.loads(text)["error"]  # unescape JSON backslashes on win32
    assert str(base) in decoded

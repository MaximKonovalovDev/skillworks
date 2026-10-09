# install safety: backup-before-overwrite and dry-run preview
import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('install_fleet_skills', ROOT / 'tools' / 'install_fleet_skills.py')
inst = importlib.util.module_from_spec(spec)
sys.modules['install_fleet_skills'] = inst
spec.loader.exec_module(inst)

def _prep(tmp_path, monkeypatch):
    src = tmp_path / 'src'
    (src / 'demo').mkdir(parents=True)
    (src / 'demo' / 'SKILL.md').write_text('v1', encoding='utf-8')
    monkeypatch.setattr(inst, 'SKILLS', src)
    dest = tmp_path / 'dest'
    dest.mkdir()
    return dest

def test_backup_exists_after_overwrite(tmp_path, monkeypatch):
    dest = _prep(tmp_path, monkeypatch)
    assert inst.main(['--to', str(dest), 'demo']) == 0
    (dest / 'demo' / 'SKILL.md').write_text('local', encoding='utf-8')
    assert inst.main(['--to', str(dest), 'demo']) == 0
    backs = list(dest.glob('demo.bak-*'))
    assert backs
    assert (backs[0] / 'SKILL.md').read_text(encoding='utf-8') == 'local'
    assert (dest / 'demo' / 'SKILL.md').read_text(encoding='utf-8') == 'v1'

def test_dry_run_writes_nothing(tmp_path, monkeypatch):
    dest = _prep(tmp_path, monkeypatch)
    assert inst.main(['--to', str(dest), 'demo']) == 0
    (dest / 'demo' / 'SKILL.md').write_text('drift', encoding='utf-8')
    before = (dest / 'demo' / 'SKILL.md').read_text(encoding='utf-8')
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = inst.main(['--to', str(dest), '--dry-run', 'demo'])
    assert rc == 0
    assert 'dry-run' in buf.getvalue()
    assert (dest / 'demo' / 'SKILL.md').read_text(encoding='utf-8') == before
    assert list(dest.glob('demo.bak-*')) == []
    fresh = tmp_path / 'fresh'
    with redirect_stdout(io.StringIO()):
        assert inst.main(['--to', str(fresh), '--dry-run', 'demo']) == 0
    assert not (fresh / 'demo').exists()

def test_fleet_bulk_includes_pipe_run():
    assert "pipe-run" in inst.FLEET
    assert (inst.SKILLS / "pipe-run" / "SKILL.md").is_file()
def test_classify_three_way_states(tmp_path, monkeypatch):
    dest = _prep(tmp_path, monkeypatch)
    assert inst.main(["--to", str(dest), "demo"]) == 0
    assert inst.classify("demo", dest) == []
    (dest / "demo" / "SKILL.md").write_text("local", encoding="utf-8")
    states = {d["file"]: d["state"] for d in inst.classify("demo", dest)}
    assert states["SKILL.md"] == "live-drifted"
    (dest / "demo" / "SKILL.md").write_text("v1", encoding="utf-8")
    (inst.SKILLS / "demo" / "SKILL.md").write_text("v2", encoding="utf-8")
    states = {d["file"]: d["state"] for d in inst.classify("demo", dest)}
    assert states["SKILL.md"] == "repo-ahead"
    (dest / "demo" / "SKILL.md").write_text("local2", encoding="utf-8")
    states = {d["file"]: d["state"] for d in inst.classify("demo", dest)}
    assert states["SKILL.md"] == "conflict"
    (dest / "demo" / "extra.md").write_text("x", encoding="utf-8")
    states = {d["file"]: d["state"] for d in inst.classify("demo", dest)}
    assert states["extra.md"] == "extra"
def test_check_json_typed_states(tmp_path, monkeypatch):
    import json as _json
    dest = _prep(tmp_path, monkeypatch)
    assert inst.main(["--to", str(dest), "demo"]) == 0
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = inst.main(["--to", str(dest), "--check", "--json", "demo"])
    assert rc == 0
    assert "states" in buf.getvalue()
    doc = _json.loads(buf.getvalue().strip().splitlines()[-1])
    assert doc["skill"] == "demo"
    assert doc["ok"] is True


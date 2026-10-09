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

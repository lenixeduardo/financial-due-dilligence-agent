from app.backup import verify_backup
from app.db import initialize_database,ensure_workspace
from scripts.backup_loop import run_backup

def test_scheduled_backup_rotation(tmp_path,monkeypatch):
    monkeypatch.setenv("FINSIGHT_SQLITE_PATH",str(tmp_path/"source.sqlite"))
    initialize_database();ensure_workspace("local")
    out=tmp_path/"backups";out.mkdir()
    paths=[run_backup(directory=str(out),keep=2) for _ in range(3)]
    remaining=list(out.glob("finsight-*.sqlite"))
    assert len(remaining)==2
    assert all(verify_backup(str(x)) for x in remaining)
    assert not paths[0].exists()

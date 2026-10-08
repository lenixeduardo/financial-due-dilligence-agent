import sqlite3
import pytest
from app.db import initialize_database,ensure_workspace
from app.backup import backup_database,verify_backup,restore_database

def test_sqlite_backup_and_restore(tmp_path,monkeypatch):
    db=tmp_path/"main.sqlite"
    monkeypatch.setenv("FINSIGHT_SQLITE_PATH",str(db))
    initialize_database()
    ensure_workspace("local")
    backup=backup_database(str(tmp_path/"copies"/"copy.sqlite"))
    assert verify_backup(str(backup))
    restored=restore_database(str(backup),str(tmp_path/"restored.sqlite"))
    with sqlite3.connect(restored) as conn:
        assert conn.execute("SELECT id FROM workspaces").fetchone()[0]=="local"
    with pytest.raises(FileExistsError):
        backup_database(str(backup))
    with pytest.raises(ValueError):
        restore_database(str(backup),str(restored))

def test_missing_file_fails(tmp_path,monkeypatch):
    monkeypatch.setenv("FINSIGHT_SQLITE_PATH",str(tmp_path/"missing.sqlite"))
    with pytest.raises(FileNotFoundError):
        backup_database(str(tmp_path/"copy.sqlite"))

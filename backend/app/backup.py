"""Consistent local SQLite backups and verified restores. Do not expose as HTTP routes."""
from pathlib import Path
import sqlite3
import os
from .db import _database_path

def _check(db: sqlite3.Connection):
    result=db.execute("PRAGMA quick_check").fetchone()[0]
    if result!="ok":
        raise ValueError("SQLite integrity verification failed")

def backup_database(destination: str) -> Path:
    source=_database_path().resolve()
    target=Path(destination).expanduser().resolve()
    if source==target:
        raise ValueError("backup must use a distinct file")
    if not source.is_file():
        raise FileNotFoundError("SQLite source file missing")
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        raise FileExistsError("backup destination must not already exist")
    partial=target.with_name(target.name+".partial")
    if partial.exists():
        raise FileExistsError("incomplete backup already exists")
    try:
        with sqlite3.connect(f"file:{source}?mode=ro",uri=True) as origin:
            _check(origin)
            with sqlite3.connect(partial) as copied:
                origin.backup(copied,pages=128)
                _check(copied)
        os.replace(partial,target)
        os.chmod(target,0o600)
        return target
    finally:
        if partial.exists():
            partial.unlink()

def verify_backup(filename:str) -> bool:
    target=Path(filename).expanduser().resolve()
    with sqlite3.connect(f"file:{target}?mode=ro",uri=True) as db:
        _check(db)
    return True

def restore_database(source:str,destination:str) -> Path:
    """Restore ONLY to a NEW path while the application is offline."""
    original=Path(source).expanduser().resolve()
    target=Path(destination).expanduser().resolve()
    if original==target or target.exists():
        raise ValueError("restore requires a distinct nonexisting target")
    verify_backup(str(original))
    return _copy_backup_to(original,target)

def _copy_backup_to(source:Path,target:Path)->Path:
    target.parent.mkdir(parents=True,exist_ok=True)
    partial=target.with_name(target.name+".partial")
    if partial.exists():
        raise FileExistsError("partial restore already exists")
    try:
        with sqlite3.connect(f"file:{source}?mode=ro",uri=True) as origin:
            with sqlite3.connect(partial) as dest:
                origin.backup(dest)
                _check(dest)
        os.replace(partial,target)
        os.chmod(target,0o600)
        return target
    finally:
        if partial.exists():
            partial.unlink()

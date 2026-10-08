"""Periodically snapshot SQLite onto a separate, operator-managed storage mount."""
import os
import time
from datetime import datetime,timezone
from pathlib import Path
from app.backup import backup_database,verify_backup

PREFIX="finsight-"
SUFFIX=".sqlite"

def run_backup(*,directory:str,keep:int=14)->Path:
    destination=Path(directory).resolve()
    if not destination.is_dir():
        raise ValueError("existing mounted backup directory required")
    if not 2<=keep<=365:
        raise ValueError("backup retention must be 2–365")
    now=datetime.now(timezone.utc)
    filename=f"{PREFIX}{now.strftime('%Y%m%dT%H%M%S%fZ')}{SUFFIX}"
    saved=backup_database(str(destination/filename))
    verify_backup(str(saved))
    completed=sorted((p for p in destination.glob(f"{PREFIX}*{SUFFIX}") if p.is_file()),
                     key=lambda p:p.name,reverse=True)
    for stale in completed[keep:]:
        stale.unlink()
    return saved

def main():
    interval=int(os.environ.get("FINSIGHT_BACKUP_INTERVAL_SECONDS","21600"))
    if not 3600<=interval<=86400:
        raise ValueError("backup interval must be between 1 and 24 hours")
    directory=os.environ["FINSIGHT_BACKUP_DIR"]
    keep=int(os.environ.get("FINSIGHT_BACKUP_KEEP","14"))
    while True:
        try:
            path=run_backup(directory=directory,keep=keep)
            print(f"SQLite backup verified: {path.name}",flush=True)
        except Exception as exc:
            print(f"SQLite backup failed: {type(exc).__name__}",flush=True)
        time.sleep(interval)

if __name__=="__main__":
    main()

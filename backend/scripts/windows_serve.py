"""Start Windows loopback app and periodic backups in one process."""
import os
import threading
import time
from pathlib import Path
from app.backup import backup_database, verify_backup
from app.windows_host import serve

def backup_worker():
    target = Path(os.environ["FINSIGHT_BACKUP_DIR"])
    target.mkdir(parents=True, exist_ok=True)
    while True:
        try:
            stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
            candidate = target / ("finsight-" + stamp + ".sqlite")
            if candidate.exists():
                candidate = target / ("finsight-" + str(time.time_ns()) + ".sqlite")
            saved = backup_database(str(candidate))
            verify_backup(str(saved))
            copies = sorted(target.glob("finsight-*.sqlite"), reverse=True)
            for old in copies[14:]:
                old.unlink()
        except Exception as exc:
            print("Backup unsuccessful:", type(exc).__name__, flush=True)
        time.sleep(21600)

if __name__ == "__main__":
    if os.environ.get("FINSIGHT_AUTH_MODE") != "users":
        raise SystemExit("User authentication is required.")
    threading.Thread(target=backup_worker, daemon=True, name="sqlite-backup").start()
    serve()

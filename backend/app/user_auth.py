"""SQLite identities and opaque bearer sessions for single-host deployments.

No self-registration endpoint. Administrators provision accounts from a protected CLI.
"""
import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime,timezone,timedelta
from .db import connection

AUTH_SCHEMA="""
CREATE TABLE IF NOT EXISTS account_users (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 workspace_id TEXT NOT NULL REFERENCES workspaces(id),
 username TEXT NOT NULL,
 salt_b64 TEXT NOT NULL,
 password_hash TEXT NOT NULL,
 role TEXT NOT NULL CHECK(role IN ('reader','analyst','reviewer','admin')),
 is_active INTEGER NOT NULL DEFAULT 1,
 UNIQUE(workspace_id,username)
);
CREATE TABLE IF NOT EXISTS auth_sessions (
 token_hash TEXT PRIMARY KEY,
 user_id INTEGER NOT NULL REFERENCES account_users(id) ON DELETE CASCADE,
 expires_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS auth_failures (
 workspace_id TEXT NOT NULL,
 username TEXT NOT NULL,
 fail_count INTEGER NOT NULL DEFAULT 0,
 locked_until TEXT,
 PRIMARY KEY(workspace_id,username)
);
"""
DURATION=timedelta(hours=8)
def _derive(password:str,salt:bytes)->str:
    return hashlib.scrypt(password.encode("utf-8"),salt=salt,n=2**14,r=8,p=1,dklen=32).hex()

def create_user(*,workspace_id:str,username:str,password:str,role:str="reader")->None:
    if not (3<=len(username)<=100 and username.isascii() and username.replace("-","").replace("_","").isalnum()):
        raise ValueError("invalid username")
    if len(password)<14 or len(password)>256:
        raise ValueError("password must contain 14-256 characters")
    if role not in ("reader","analyst","reviewer","admin"):
        raise ValueError("invalid role")
    salt=secrets.token_bytes(16)
    with connection() as db:
        db.executescript(AUTH_SCHEMA)
        db.execute("""INSERT INTO account_users(workspace_id,username,salt_b64,password_hash,role)
          VALUES(?,?,?,?,?)""",(workspace_id,username,base64.b64encode(salt).decode(),_derive(password,salt),role))

def authenticate(*,workspace_id:str,username:str,password:str)->str|None:
    now=datetime.now(timezone.utc)
    with connection() as db:
        db.executescript(AUTH_SCHEMA)
        lock=db.execute("SELECT fail_count,locked_until FROM auth_failures WHERE workspace_id=? AND username=?",
            (workspace_id,username)).fetchone()
        if lock and lock["locked_until"] and datetime.fromisoformat(lock["locked_until"])>now:
            return None
        user=db.execute("""SELECT * FROM account_users WHERE workspace_id=? AND username=? AND is_active=1""",
            (workspace_id,username)).fetchone()
        salt=base64.b64decode(user["salt_b64"]) if user else bytes(16)
        derived=_derive(password,salt)
        valid=bool(user and hmac.compare_digest(derived,user["password_hash"]))
        if not valid:
            attempts=(lock["fail_count"] if lock else 0)+1
            until=(now+timedelta(minutes=15)).isoformat() if attempts>=5 else None
            db.execute("""INSERT INTO auth_failures(workspace_id,username,fail_count,locked_until)
              VALUES(?,?,?,?) ON CONFLICT(workspace_id,username) DO UPDATE SET
              fail_count=excluded.fail_count,locked_until=excluded.locked_until""",
              (workspace_id,username,attempts,until))
            return None
        db.execute("DELETE FROM auth_failures WHERE workspace_id=? AND username=?",(workspace_id,username))
        token=secrets.token_urlsafe(32)
        db.execute("INSERT INTO auth_sessions(token_hash,user_id,expires_at) VALUES(?,?,?)",
            (hashlib.sha256(token.encode()).hexdigest(),user["id"],(now+DURATION).isoformat()))
        return token

def lookup_session(token:str,workspace_id:str)->dict|None:
    if len(token)>256 or not token:
        return None
    with connection() as db:
        db.executescript(AUTH_SCHEMA)
        row=db.execute("""SELECT u.username,u.role,u.workspace_id,s.expires_at
            FROM auth_sessions s JOIN account_users u ON u.id=s.user_id
            WHERE s.token_hash=? AND u.workspace_id=? AND u.is_active=1""",
            (hashlib.sha256(token.encode()).hexdigest(),workspace_id)).fetchone()
    if not row or datetime.fromisoformat(row["expires_at"])<=datetime.now(timezone.utc):
        return None
    return dict(row)

def revoke_token(token:str)->None:
    with connection() as db:
        db.executescript(AUTH_SCHEMA)
        db.execute("DELETE FROM auth_sessions WHERE token_hash=?",
            (hashlib.sha256(token.encode()).hexdigest(),))

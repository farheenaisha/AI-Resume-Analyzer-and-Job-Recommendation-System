import sqlite3, json, hashlib, os
from pathlib import Path

DB_PATH = Path(__file__).parent / "careerlens.db"

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def hash_password(password, salt=None):
    salt = salt or os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 200000).hex()
    return salt, digest

def init_db():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL, salt TEXT NOT NULL, password_hash TEXT NOT NULL,
            career_goal TEXT DEFAULT '', bio TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS analyses(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            file_name TEXT NOT NULL, readiness_score INTEGER NOT NULL,
            result_json TEXT NOT NULL, jobs_json TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS saved_jobs(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            job_key TEXT NOT NULL, job_json TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, job_key), FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """)

def create_user(name,email,password):
    salt,digest = hash_password(password)
    try:
        with connect() as con:
            cur=con.execute("INSERT INTO users(name,email,salt,password_hash) VALUES(?,?,?,?)",(name,email,salt,digest))
            return True, "created"
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."

def verify_user(email,password):
    with connect() as con:
        row=con.execute("SELECT * FROM users WHERE email=?",(email,)).fetchone()
    if not row: return None
    _, digest=hash_password(password,row["salt"])
    if digest != row["password_hash"]: return None
    return {"id":row["id"],"name":row["name"]}

def get_user(user_id):
    with connect() as con:
        row=con.execute("SELECT id,name,email,career_goal,bio FROM users WHERE id=?",(user_id,)).fetchone()
    return dict(row) if row else None

def update_profile(user_id,name,goal,bio):
    with connect() as con:
        con.execute("UPDATE users SET name=?,career_goal=?,bio=? WHERE id=?",(name,goal,bio,user_id))

def save_analysis(user_id,file_name,score,result,jobs):
    with connect() as con:
        con.execute("INSERT INTO analyses(user_id,file_name,readiness_score,result_json,jobs_json) VALUES(?,?,?,?,?)",
                    (user_id,file_name,score,json.dumps(result),json.dumps(jobs)))

def get_analyses(user_id):
    with connect() as con:
        rows=con.execute("SELECT * FROM analyses WHERE user_id=? ORDER BY id DESC",(user_id,)).fetchall()
    return [dict(r) for r in rows]

def save_job(user_id,job):
    with connect() as con:
        con.execute("INSERT OR IGNORE INTO saved_jobs(user_id,job_key,job_json) VALUES(?,?,?)",
                    (user_id,str(job["id"]),json.dumps(job)))

def get_saved_jobs(user_id):
    with connect() as con:
        rows=con.execute("SELECT job_key,job_json FROM saved_jobs WHERE user_id=? ORDER BY id DESC",(user_id,)).fetchall()
    out=[]
    for r in rows:
        j=json.loads(r["job_json"]); j["job_key"]=r["job_key"]; out.append(j)
    return out

def delete_saved_job(user_id,job_key):
    with connect() as con:
        con.execute("DELETE FROM saved_jobs WHERE user_id=? AND job_key=?",(user_id,str(job_key)))

def delete_analysis(user_id, analysis_id):
    with connect() as con:
        con.execute("DELETE FROM analyses WHERE user_id=? AND id=?",(user_id,int(analysis_id)))

"""
BizShock — Database Layer (SQLite)
No external connection needed. Runs entirely on Render's disk.
"""
import os
import json
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "bizshock.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ── Schema bootstrap ──────────────────────────────────────────────────────────
def init_db():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name     TEXT,
            business_name TEXT,
            created_at    TEXT DEFAULT (datetime('now'))
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scenarios (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL REFERENCES users(id),
            scenario_name TEXT NOT NULL,
            business_type TEXT,
            verdict       TEXT,
            cost_impact   REAL,
            predictions   TEXT,
            baseline      TEXT,
            live_prices   TEXT,
            breakdown     TEXT,
            replay        TEXT,
            created_at    TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()

# ── User operations ───────────────────────────────────────────────────────────
def create_user(email, password_hash, full_name, business_name):
    try:
        conn = get_conn()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO users (email, password_hash, full_name, business_name)
            VALUES (?, ?, ?, ?)
        """, (email.lower().strip(), password_hash, full_name, business_name))
        user_id = cur.lastrowid
        conn.commit()
        conn.close()
        return user_id, None
    except sqlite3.IntegrityError:
        return None, "email_taken"
    except Exception as e:
        return None, str(e)

def get_user_by_email(email):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

# ── Scenario operations ───────────────────────────────────────────────────────
def save_scenario(user_id, scenario_name, business_type, verdict,
                  cost_impact, predictions, baseline, live_prices,
                  breakdown, replay=None):
    try:
        conn = get_conn()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO scenarios
            (user_id, scenario_name, business_type, verdict, cost_impact,
             predictions, baseline, live_prices, breakdown, replay)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, scenario_name, business_type, verdict, cost_impact,
            json.dumps(predictions), json.dumps(baseline),
            json.dumps(live_prices), json.dumps(breakdown), replay
        ))
        conn.commit()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def scenario_name_exists(user_id, scenario_name):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT 1 FROM scenarios
        WHERE user_id = ? AND scenario_name = ?
    """, (user_id, scenario_name))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

def get_user_scenarios(user_id):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT scenario_name, business_type, verdict, cost_impact,
               predictions, created_at
        FROM scenarios
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        if d.get("predictions"):
            d["predictions"] = json.loads(d["predictions"])
        result.append(d)
    return result

def delete_scenario(user_id, scenario_name):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        DELETE FROM scenarios
        WHERE user_id = ? AND scenario_name = ?
    """, (user_id, scenario_name))
    conn.commit()
    conn.close()
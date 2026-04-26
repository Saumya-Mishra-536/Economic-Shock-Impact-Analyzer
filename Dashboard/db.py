"""
BizShock — Database Layer (Supabase PostgreSQL)
All DB operations in one place. Never import credentials anywhere else.
"""
import os
import json
import psycopg2
import psycopg2.extras
from datetime import datetime

# ── Connection ────────────────────────────────────────────────────────────────
DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:bizshock_secret_key_Saumya@536_dva@db.oqctdnwbahyjintqxvks.supabase.co:5432/postgres"
)

def get_conn():
    return psycopg2.connect(DB_URL, sslmode="require")

# ── Schema bootstrap — run once on startup ────────────────────────────────────
def init_db():
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            SERIAL PRIMARY KEY,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name     TEXT,
            business_name TEXT,
            created_at    TIMESTAMP DEFAULT NOW()
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scenarios (
            id            SERIAL PRIMARY KEY,
            user_id       INTEGER REFERENCES users(id) ON DELETE CASCADE,
            scenario_name TEXT NOT NULL,
            business_type TEXT,
            verdict       TEXT,
            cost_impact   REAL,
            predictions   JSONB,
            baseline      JSONB,
            live_prices   JSONB,
            breakdown     JSONB,
            replay        TEXT,
            created_at    TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# ── User operations ───────────────────────────────────────────────────────────
def create_user(email, password_hash, full_name, business_name):
    try:
        conn = get_conn()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO users (email, password_hash, full_name, business_name)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (email.lower().strip(), password_hash, full_name, business_name))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return user_id, None
    except psycopg2.errors.UniqueViolation:
        return None, "email_taken"
    except Exception as e:
        return None, str(e)

def get_user_by_email(email):
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM users WHERE email = %s", (email.lower().strip(),))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return dict(user) if user else None

# ── Scenario operations ───────────────────────────────────────────────────────
def save_scenario(user_id, scenario_name, business_type, verdict,
                  cost_impact, predictions, baseline, live_prices, breakdown, replay=None):
    try:
        conn = get_conn()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO scenarios
            (user_id, scenario_name, business_type, verdict, cost_impact,
             predictions, baseline, live_prices, breakdown, replay)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            user_id, scenario_name, business_type, verdict, cost_impact,
            json.dumps(predictions), json.dumps(baseline),
            json.dumps(live_prices), json.dumps(breakdown), replay
        ))
        conn.commit()
        cur.close()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def scenario_name_exists(user_id, scenario_name):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT 1 FROM scenarios
        WHERE user_id = %s AND scenario_name = %s
    """, (user_id, scenario_name))
    exists = cur.fetchone() is not None
    cur.close()
    conn.close()
    return exists

def get_user_scenarios(user_id):
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT scenario_name, business_type, verdict, cost_impact,
               predictions, created_at
        FROM scenarios
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]

def delete_scenario(user_id, scenario_name):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        DELETE FROM scenarios
        WHERE user_id = %s AND scenario_name = %s
    """, (user_id, scenario_name))
    conn.commit()
    cur.close()
    conn.close()

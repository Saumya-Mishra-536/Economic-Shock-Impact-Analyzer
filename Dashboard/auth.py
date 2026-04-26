"""
BizShock — Auth Layer
Signup, login, JWT token creation and verification.
"""
import os
import bcrypt
import jwt
import importlib.util
import pathlib
from datetime import datetime, timedelta

# ── Load db.py directly by file path ─────────────────────────────────────────
def _load_db():
    here = pathlib.Path(__file__).parent
    for candidate in [here / "db.py", here.parent / "db.py"]:
        if candidate.exists():
            spec = importlib.util.spec_from_file_location("db", candidate)
            mod  = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise ImportError("Cannot find db.py")

_db              = _load_db()
create_user      = _db.create_user
get_user_by_email = _db.get_user_by_email
get_user_by_id   = _db.get_user_by_id

SECRET_KEY        = os.environ.get("SECRET_KEY", "bizshock_secret_key_Saumya@536_dva")
TOKEN_EXPIRY_DAYS = 7

# ── Password ──────────────────────────────────────────────────────────────────
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False

# ── JWT ───────────────────────────────────────────────────────────────────────
def create_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=TOKEN_EXPIRY_DAYS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# ── Signup ────────────────────────────────────────────────────────────────────
def signup(email, password, full_name, business_name):
    if not email or not password:
        return None, None, "Email and password are required."
    if len(password) < 8:
        return None, None, "Password must be at least 8 characters."
    if "@" not in email:
        return None, None, "Please enter a valid email address."

    pw_hash = hash_password(password)
    user_id, err = create_user(email, pw_hash, full_name, business_name)

    if err == "email_taken":
        return None, None, "An account with this email already exists. Please log in."
    if err:
        return None, None, f"Signup failed: {err}"

    user  = get_user_by_id(user_id)
    token = create_token(user_id)
    return token, user, None

# ── Login ─────────────────────────────────────────────────────────────────────
def login(email, password):
    if not email or not password:
        return None, None, "Email and password are required."

    user = get_user_by_email(email)
    if not user:
        return None, None, "No account found with this email."

    if not verify_password(password, user["password_hash"]):
        return None, None, "Incorrect password. Please try again."

    token = create_token(user["id"])
    return token, user, None

# ── Session restore ───────────────────────────────────────────────────────────
def get_user_from_token(token: str):
    if not token:
        return None
    user_id = verify_token(token)
    if not user_id:
        return None
    return get_user_by_id(user_id)
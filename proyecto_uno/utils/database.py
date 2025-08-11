import sqlite3
import os
import secrets
import hashlib
from typing import Tuple, Optional


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def init_db(path: str):
    conn = sqlite3.connect(path)
    with conn:
        conn.executescript(SCHEMA)
    conn.close()


def _hash_password(password: str, salt_hex: str) -> str:
    salt = bytes.fromhex(salt_hex)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return dk.hex()


def register_user(path: str, username: str, password: str) -> Tuple[bool, Optional[str]]:
    if not username or not password:
        return False, "Usuario y contraseña requeridos"
    conn = sqlite3.connect(path)
    try:
        with conn:
            salt = secrets.token_hex(16)
            ph = _hash_password(password, salt)
            conn.execute(
                "INSERT INTO users(username, password_hash, salt, created_at) VALUES (?, ?, ?, datetime('now'))",
                (username, ph, salt),
            )
        return True, None
    except sqlite3.IntegrityError:
        return False, "Usuario ya existe"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def login_user(path: str, username: str, password: str) -> Tuple[bool, Optional[str]]:
    if not username or not password:
        return False, "Usuario y contraseña requeridos"
    conn = sqlite3.connect(path)
    try:
        cur = conn.execute("SELECT password_hash, salt FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        if not row:
            return False, "Usuario no existe"
        ph, salt = row
        return (_hash_password(password, salt) == ph), (None if _hash_password(password, salt) == ph else "Contraseña incorrecta")
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

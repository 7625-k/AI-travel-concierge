import sqlite3
import hashlib
import secrets


def create_database():
    conn = sqlite3.connect("travel.db")
    cursor = conn.cursor()

    # Create users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT,
            salt TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Create searches table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            query TEXT,
            result TEXT
        )
        """
    )

    # Safely migrate existing database by adding username column to searches if it is missing
    try:
        cursor.execute("ALTER TABLE searches ADD COLUMN username TEXT")
    except sqlite3.OperationalError:
        # Column already exists
        pass

    conn.commit()
    conn.close()


def hash_password(password, salt=None):
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
    return hashed, salt


def create_user(username, password):
    if user_exists(username):
        return False
    
    password_hash, salt = hash_password(password)
    
    conn = sqlite3.connect("travel.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username.lower().strip(), password_hash, salt)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def verify_user(username, password):
    conn = sqlite3.connect("travel.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password_hash, salt FROM users WHERE username = ?",
        (username.lower().strip(),)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False

    stored_hash, salt = row
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == stored_hash


def user_exists(username):
    conn = sqlite3.connect("travel.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM users WHERE username = ?",
        (username.lower().strip(),)
    )
    row = cursor.fetchone()
    conn.close()
    return row is not None


def save_search(username, query, result):
    conn = sqlite3.connect("travel.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO searches (username, query, result) VALUES (?, ?, ?)",
        (username.lower().strip() if username else None, query, result)
    )
    conn.commit()
    conn.close()


def get_recent_searches(username, limit=10):
    conn = sqlite3.connect("travel.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT query, result FROM searches WHERE username = ? ORDER BY id DESC LIMIT ?",
        (username.lower().strip() if username else "", limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

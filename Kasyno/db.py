import sqlite3
import threading

DB_PATH = 'players.db'
db_lock = threading.Lock()

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nick TEXT NOT NULL UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                pesel TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                balance INTEGER DEFAULT 2000
            )
        ''')
        conn.commit()

def register_user(nick, first_name, last_name, pesel, password):
    with db_lock:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO players (nick, first_name, last_name, pesel, password) VALUES (?, ?, ?, ?, ?)",
                    (nick, first_name, last_name, pesel, password)
                )
                conn.commit()
                return True, None
        except sqlite3.IntegrityError as e:
            if 'nick' in str(e):
                return False, "Nick już istnieje"
            return False, "PESEL już istnieje"

def authenticate_user(nick, password):
    with db_lock:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT nick, balance FROM players WHERE nick=? AND password=?",
                (nick, password)
            )
            result = cursor.fetchone()
            return result if result else None
import sqlite3
from contextlib import contextmanager
from typing import List, Dict


class DatabaseManager:
    def __init__(self, db_name="nazm_ara.db"):
        self.db_name = db_name
        self.initDb()


    @contextmanager
    def getConnection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Database Error: {e}")
            raise
        finally:
            conn.close()

    def initDb(self):
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        nickname TEXT,
                        token TEXT,
                        f_name TEXT,
                        l_name TEXT,
                        email TEXT
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tags (
                        local_id TEXT PRIMARY KEY NOT NULL,
                        server_id INTEGER DEFAULT NULL,
                        name TEXT NOT NULL UNIQUE,
                        needs_sync INTEGER DEFAULT 1 CHECK(needs_sync IN (0,1)),
                        deleted_at TEXT DEFAULT NULL,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        local_id TEXT PRIMARY KEY NOT NULL,
                        server_id INTEGER DEFAULT NULL,
                        title TEXT NOT NULL,
                        description TEXT,
                        priority INTEGER DEFAULT 1 CHECK(priority IN (0,1,2)),
                        date_time TEXT,
                        tag_id TEXT DEFAULT NULL,
                        needs_sync INTEGER DEFAULT 1 CHECK(needs_sync IN (0,1)),
                        deleted_at TEXT DEFAULT NULL,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (tag_id) REFERENCES tags(local_id) ON DELETE SET NULL
                    )
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_tasks_server_id ON tasks(server_id)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_tasks_sync ON tasks(needs_sync)
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS habits (
                        local_id TEXT PRIMARY KEY NOT NULL,
                        server_id INTEGER DEFAULT NULL,
                        title TEXT NOT NULL,
                        question TEXT NOT NULL,
                        unit INTEGER NOT NULL,
                        tag_id TEXT DEFAULT NULL,
                        description TEXT,
                        priority INTEGER DEFAULT 1 CHECK(priority IN (0,1,2)),
                        archive INTEGER DEFAULT 0 CHECK(archive IN (0,1)),
                        color TEXT NOT NULL,
                        needs_sync INTEGER DEFAULT 1 CHECK(needs_sync IN (0,1)),
                        deleted_at TEXT DEFAULT NULL,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (tag_id) REFERENCES tags(local_id) ON DELETE SET NULL
                    )
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_habits_server_id ON habits(server_id)
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS daily_habits (
                        local_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        habit_id TEXT NOT NULL,
                        user_id INTEGER NOT NULL,
                        server_id INTEGER DEFAULT NULL,
                        date TEXT NOT NULL,
                        value INTEGER DEFAULT 0,
                        needs_sync INTEGER DEFAULT 1 CHECK(needs_sync IN (0,1)),
                        deleted_at TEXT DEFAULT NULL,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (habit_id) REFERENCES habits(local_id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        UNIQUE (user_id, habit_id, date)
                    )
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_daily_habits_date ON daily_habits(date)
                """)
                
        except sqlite3.Error as e:
            print(f"Error initializing database: {e}")
            raise

    # ==================== USERS ====================

    def addOfflineUser(self, nickname: str) -> bool:
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (nickname)
                    VALUES (?)
                """, (nickname,))
                return True
        except sqlite3.Error as e:
            print(f"Error adding offline user: {e}")
            return False


    def addOnlineUser(self, user_id: int, nickname: str, token: str, f_name: str, 
                 l_name: str, email: str) -> bool:
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (user_id, nickname, token, f_name, l_name, email)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, nickname, token, f_name, l_name, email))
                return True
        except sqlite3.Error as e:
            print(f"Error adding user: {e}")
            return False


    def getListOfUsers(self) -> List[Dict]:
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error fetching users: {e}")
            return []

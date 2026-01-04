import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Optional
from datetime import datetime
import uuid


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
                        user_id INTEGER NOT NULL,
                        name TEXT NOT NULL UNIQUE,
                        needs_sync INTEGER DEFAULT 1 CHECK(needs_sync IN (0,1)),
                        deleted_at TEXT DEFAULT NULL,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        UNIQUE (user_id, name)
                    )
                """)

                cursor.execute("""
                        CREATE TABLE IF NOT EXISTS tasks (
                            local_id TEXT PRIMARY KEY NOT NULL,
                            server_id INTEGER DEFAULT NULL,
                            user_id INTEGER NOT NULL,
                            title TEXT NOT NULL,
                            is_complete INTEGER DEFAULT 0 CHECK(is_complete IN (0,1)),
                            description TEXT,
                            priority INTEGER DEFAULT 1 CHECK(priority IN (0,1,2)),
                            date_time TEXT,
                            tag_id TEXT DEFAULT NULL,
                            needs_sync INTEGER DEFAULT 1 CHECK(needs_sync IN (0,1)),
                            deleted_at TEXT DEFAULT NULL,
                            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (tag_id) REFERENCES tags(local_id) ON DELETE SET NULL,
                            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                        )
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_tasks_server_id ON tasks(server_id);
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_tasks_sync ON tasks(needs_sync);
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS habits (
                        local_id TEXT PRIMARY KEY NOT NULL,
                        server_id INTEGER DEFAULT NULL,
                        user_id INTEGER NOT NULL,
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
                        FOREIGN KEY (tag_id) REFERENCES tags(local_id) ON DELETE SET NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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

    def addOfflineUser(self, nickname: str, f_name: str, l_name: str) -> bool:
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (nickname, f_name, l_name)
                    VALUES (?, ?, ?)
                """, (nickname, f_name, l_name))
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

    # ==================== TASKS ====================

    def addTask(self, title: str, user_id, description: str = None, priority: int = 1,
                 date_time: str = None, tag_id: str = None) -> Optional[str]:
        local_id = str(uuid.uuid4())
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO tasks (local_id, title, description, priority, date_time, tag_id, user_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (local_id, title, description, priority, date_time, tag_id, user_id))
                return local_id
        except sqlite3.Error as e:
            print(f"Error adding task: {e}")
            return None


    def getTasksByDate(self, date: str, user_id: int) -> List[Dict]:
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM tasks WHERE date_time = ? AND deleted_at IS NULL AND user_id = ?
                """, (date, user_id))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error fetching tasks by date: {e}")
            return []


    def toggleTask(self, task_id, value) -> bool:
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"UPDATE tasks SET is_complete = ? WHERE local_id = ?", (value, task_id))
                return True
        except sqlite3.Error as e:
            print(f"Error updating specified task: {e}")
            return False


    def getUserTaskDates(self, user_id) ->  Optional[list]:
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT DISTINCT date_time FROM tasks WHERE user_id = ? AND deleted_at IS NULL", (user_id,))
                rows = cursor.fetchall()
                return [str(row[0]) for row in rows]
        except sqlite3.Error as e:
            print(f"Error fetching task dates: {e}")
            return []


    def deleteTask(self, local_id: str) -> bool:
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE tasks SET deleted_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP, needs_sync = 1
                    WHERE local_id = ?
                """, (local_id,))
                return True
        except sqlite3.Error as e:
            print(f"Error deleting task: {e}")
            return False


    def updateTask(self, local_id: str, **kwargs) -> bool:
        allowed_fields = {'title', 'description', 'priority'}
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_fields:
            return False

        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                update_fields['updated_at'] = datetime.now().isoformat()
                update_fields['needs_sync'] = 1
                
                set_clause = ", ".join([f"{k} = ?" for k in update_fields.keys()])
                values = list(update_fields.values()) + [local_id]
                cursor.execute(f"UPDATE tasks SET {set_clause} WHERE local_id = ?", values)
                return True
        except sqlite3.Error as e:
            print(f"Error updating task: {e}")
            return False

import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Optional
from datetime import datetime
import uuid
import pandas as pd
import json


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

                # Indexes improve search speed for synchronization and date-based filtering
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_server_id ON tasks(server_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_sync ON tasks(needs_sync)")

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS habits (
                        local_id TEXT PRIMARY KEY NOT NULL,
                        server_id INTEGER DEFAULT NULL,
                        user_id INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        question TEXT NOT NULL,
                        unit INTEGER NOT NULL,
                        target INTEGER NOT NULL,
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
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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
        """Generates a UUID for local_id and saves the task. Returns the UUID for further UI reference."""
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
        """Retrieves tasks for a specific date, excluding those marked for deletion."""
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


    def toggleTask(self, task_id: str, value: bool) -> bool:
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"UPDATE tasks SET is_complete = ? WHERE local_id = ?", (value, task_id))
                return True
        except sqlite3.Error as e:
            print(f"Error updating specified task: {e}")
            return False


    def getUserTaskDates(self, user_id: str) ->  Optional[list]:
        """Returns a unique list of dates where the user has active tasks."""
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
        """Performs a soft delete by setting deleted_at."""
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
        """Updates specific fields and flags the row for synchronization."""
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

    # ==================== HABITS ====================

    def addHabit(self, user_id: str, title: str, question: str,
                 unit: int, target: int , color: str, description: str = None,
                 priority: int = 1) -> Optional[str]:
        local_id = str(uuid.uuid4())
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO habits (local_id, user_id, title, question, unit, color, target, description, priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (local_id, user_id, title, question, unit, color, target, description, priority))
                return local_id
        except sqlite3.Error as e:
            print(f"Error adding habit: {e}")
            return None


    def getAllHabits(self, user_id: str) -> List[Dict]:
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM habits WHERE user_id = ? AND deleted_at IS NULL", (user_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error fetching habits: {e}")
            return []


    def deleteHabit(self, local_id: str) -> bool:
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE habits SET deleted_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP, needs_sync = 1
                    WHERE local_id = ?
                """, (local_id,))
                return True
        except sqlite3.Error as e:
            print(f"Error deleting habit: {e}")
            return False


    def updateHabit(self, local_id: str, **kwargs) -> bool:
        allowed_fields = {'title', 'question', 'unit', 'description', 'priority', 'color', 'archive', 'target'}
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
                cursor.execute(f"UPDATE habits SET {set_clause} WHERE local_id = ?", values)
                return True
        except sqlite3.Error as e:
            print(f"Error updating habit: {e}")
            return False

    # ==================== DAILY HABITS ====================

    def addDailyHabit(self, habit_id: str, user_id: int, date: str, value: int = 0) -> Optional[int]:
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO daily_habits (habit_id, user_id, date, value)
                    VALUES (?, ?, ?, ?)
                """, (habit_id, user_id, date, value))
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding daily habit: {e}")
            return None


    def getDailyHabitRange(self, user_id: int, habit_id: str, start_date: str, end_date: str) -> List[Dict]:
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT dh.*, h.title, h.unit, h.color, h.target
                    FROM daily_habits dh
                    JOIN habits h ON dh.habit_id = h.local_id
                    WHERE dh.habit_id = ? AND dh.user_id = ? AND dh.date BETWEEN ? AND ? AND dh.deleted_at IS NULL
                    ORDER BY dh.date DESC, dh.updated_at DESC
                """, (user_id,  habit_id, start_date, end_date))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error fetching daily habit range: {e}")
            return []


    def updateDailyHabit(self, daily_habit_id: int, value: int) -> bool:
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute(f""" UPDATE daily_habits SET updated_at = CURRENT_TIMESTAMP, needs_sync = 1, value = ? WHERE local_id = ?""",(value, daily_habit_id))
                return True
        except sqlite3.Error as e:
            print(f"Error updating daily habit: {e}")
            return False


    def getDailyHabitById(self, daily_habit_id: int) -> Optional[Dict]:
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute(""" select * from daily_habits WHERE local_id = ? """,
                               (daily_habit_id,))
                row = cursor.fetchone()
                return dict(row)
        except sqlite3.Error as e:
            print(f"Error deleting daily habit: {e}")
            return None


    def deleteDailyHabit(self, daily_habit_id: int) -> bool:
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE daily_habits SET deleted_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP, needs_sync = 1
                    WHERE local_id = ?
                """, (daily_habit_id,))
                return True
        except sqlite3.Error as e:
            print(f"Error deleting daily habit: {e}")
            return False


    def getAllDailyHabits(self, habit_id: str) -> Optional[List]:
        try:
            with self.getConnection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM daily_habits WHERE habit_id = ? AND deleted_at IS NULL
                """, (habit_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error fetching habits: {e}")
            return None


    def exportUserData(self, user_id: int, output_file: str):
        try:
            with self.getConnection() as conn:
                tables = ['tags', 'tasks', 'habits', 'daily_habits']
                user_backup = {}

                for table in tables:
                    # Query only data for this specific user
                    query = f"SELECT * FROM {table} WHERE user_id = {user_id}"
                    df = pd.read_sql_query(query, conn)

                    # Convert to dictionary format for JSON
                    user_backup[table] = df.to_dict(orient='records')

                with open(output_file, "w") as file:
                    json.dump(user_backup, file, indent=4)

                return True
        except sqlite3.Error as e:
            print(f"Error fetching data: {e}")
            return None


    def importUserData(self, json_file: str, new_user_id: int):
        try:
            with self.getConnection() as conn:

                with open(json_file, 'r') as file:
                    data = json.load(file)

                # Dictionaries to store mapping of { 'old_uuid': 'new_uuid' }
                tag_id_map = {}
                habit_id_map = {}

                # --- PROCESS TAGS ---
                if 'tags' in data and data['tags']:
                    df_tags = pd.DataFrame(data['tags'])
                    for old_id in df_tags['local_id'].unique():
                        tag_id_map[old_id] = str(uuid.uuid4())
                    
                    df_tags['local_id'] = df_tags['local_id'].map(tag_id_map)
                    df_tags['user_id'] = new_user_id
                    df_tags = df_tags.fillna({'deleted_at': None, 'server_id': 0})
                    
                    df_tags.to_sql('tags', conn, if_exists='append', index=False)
                    print("Tags imported.")

                # --- PROCESS HABITS ---
                if 'habits' in data and data['habits']:
                    df_habits = pd.DataFrame(data['habits'])
                    for old_id in df_habits['local_id'].unique():
                        habit_id_map[old_id] = str(uuid.uuid4())
                        
                    df_habits['local_id'] = df_habits['local_id'].map(habit_id_map)
                    df_habits['user_id'] = new_user_id
                    
                    # Map foreign key: tag_id
                    if 'tag_id' in df_habits.columns:
                        df_habits['tag_id'] = df_habits['tag_id'].map(tag_id_map)
                        
                    df_habits = df_habits.fillna({
                        'description': '', 
                        'tag_id': None, 
                        'server_id': 0,
                        'deleted_at': None
                    })
                    df_habits.to_sql('habits', conn, if_exists='append', index=False)
                    print("Habits imported.")

                # --- PROCESS TASKS ---
                if 'tasks' in data and data['tasks']:
                    df_tasks = pd.DataFrame(data['tasks'])
                    df_tasks['local_id'] = [str(uuid.uuid4()) for _ in range(len(df_tasks))]
                    df_tasks['user_id'] = new_user_id
                    
                    # Map foreign key: tag_id
                    if 'tag_id' in df_tasks.columns:
                        df_tasks['tag_id'] = df_tasks['tag_id'].map(tag_id_map)
                        
                    df_tasks = df_tasks.fillna({
                        'description': '', 
                        'tag_id': None, 
                        'server_id': 0, 
                        'date_time': '',
                        'deleted_at': None
                    })
                    df_tasks.to_sql('tasks', conn, if_exists='append', index=False)
                    print("Tasks imported.")

                # --- PROCESS DAILY HABITS ---
                if 'daily_habits' in data and data['daily_habits']:
                    df_daily = pd.DataFrame(data['daily_habits'])
                    
                    # Map foreign key: habit_id
                    df_daily['habit_id'] = df_daily['habit_id'].map(habit_id_map)
                    df_daily['user_id'] = new_user_id
                    
                    # Remove old auto-increment integer ID
                    if 'local_id' in df_daily.columns:
                        df_daily = df_daily.drop(columns=['local_id'])
                        
                    # Clean up any orphaned rows that lost their parent habit
                    df_daily = df_daily.dropna(subset=['habit_id'])
                    
                    df_daily = df_daily.fillna({'value': 0, 'server_id': 0, 'deleted_at': None})
                    df_daily.to_sql('daily_habits', conn, if_exists='append', index=False)
                    print("Daily Habits imported.")

                return True

        except sqlite3.Error as e:
            print(f"Error adding data: {e}")
            return None

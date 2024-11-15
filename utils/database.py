import sqlite3

class MyDatabase:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        # self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS records (
                                id INTEGER PRIMARY KEY,
                                name TEXT UNIQUE,
                                video_state TEXT,
                                detect_state TEXT,
                                file_type TEXT,
                                game_name TEXT
                            )''')
        self.conn.commit()

    def insert_record(self, name, suffix, game_name, video_state, detect_state):
        try:
            self.cursor.execute("INSERT INTO records (name, video_state, detect_state, file_type, game_name) VALUES (?, ?, ?, ?, ?)", (name,video_state, detect_state, suffix, game_name))
            self.conn.commit()
            return True
            # print("Record inserted successfully.")
        except sqlite3.IntegrityError:
            return False
            # print("Error: User with the same name already exists.")

    def update_record_video_state(self, name, video_state):
        self.cursor.execute("UPDATE records SET video_state = ? WHERE name = ?", (video_state, name))
        self.conn.commit()
        print("Record updated successfully.")

    def update_record_detect_state(self, name, detect_state):
        self.cursor.execute("UPDATE records SET detect_state = ? WHERE name = ?", (detect_state, name))
        self.conn.commit()
        print("Record updated successfully.")

    def delete_record(self, name):
        self.cursor.execute("DELETE FROM records WHERE name = ?", (name,))
        self.conn.commit()
        print("Record deleted successfully.")

    def fetch_all_records(self):
        self.cursor.execute("SELECT * FROM records")
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def get_user_video_state(self, name):
        self.cursor.execute('SELECT video_state FROM records WHERE name = ?', (name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        
    def get_user_detect_state(self, name):
        self.cursor.execute('SELECT detect_state FROM records WHERE name = ?', (name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]

    def close_connection(self):
        self.conn.close()
        print("Database connection closed.")

    def add_column_text(self, column_name):
        self.cursor.execute(f'ALTER TABLE records ADD COLUMN {column_name} TEXT')
        self.conn.commit()
        print(f"Column '{column_name}' added successfully.")
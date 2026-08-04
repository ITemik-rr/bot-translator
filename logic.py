import sqlite3
from config import DATABASE


class BotTranslator():
    def __init__(self, database):
        self.database = database
        self.create_database()
        self.create_table()

    def create_database(self):
        """Создаёт файл базы данных, если его ещё нет"""
        try:
            conn = sqlite3.connect(self.database)
            conn.close()
            print(f"База данных '{self.database}' успешно создана или уже существует")
        except Exception as e:
            print(f"Ошибка при создании базы данных: {e}")

    def create_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS translate (
                    user_id INTEGER NOT NULL,
                    user_text TEXT NOT NULL,
                    translation TEXT NOT NULL,
                    date TEXT 
                )
            """)
            conn.commit()

    def save_translation(self, user_id, user_text, translation, date):
        conn = sqlite3.connect(self.database)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''INSERT INTO translate (user_id, user_text, translation, date)
                       VALUES (?, ?, ?, ?)''',
                    (user_id, user_text, translation, date)
                )
        except sqlite3.Error as e:
            print(f"Ошибка при сохранении в БД: {e}")

if __name__ == "__main__":
    bt = BotTranslator(DATABASE)
    print("База данных и таблица успешно созданы!")

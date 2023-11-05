import sqlite3


def initialize_database():
    try:
        with sqlite3.connect('db/database.db') as conn:
            cursor = conn.cursor()
            with open('db/schema.sql', 'r') as schema_file:
                schema_sql = schema_file.read()
            cursor.executescript(schema_sql)
            conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while creating database: {e}")
    finally:
        conn.close()


initialize_database()

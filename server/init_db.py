import sqlite3


def initialize_database():
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    with open('db/schema.sql', 'r') as schema_file:
        schema_sql = schema_file.read()
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()


initialize_database()

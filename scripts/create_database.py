import sqlite3
from sqlite3.dbapi2 import Connection

def create_connection(db_name):
    """Create a database connection to a SQLite database"""
    conn: Connection  = sqlite3.connect(db_name)
    return conn

def create_database(db_name):
    """Create Database"""
    conn = create_connection(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS code_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            code TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS doc_files(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                text TEXT NOT NULL
            )
        ''')
    conn.commit()
    print("Database created successfully")
    conn.close()

def main():
    create_database("code_files.db")


if __name__ == "__main__":
    main()
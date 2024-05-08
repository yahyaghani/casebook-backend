import sqlite3

def setup_database():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('web_content.db')
    # Create a cursor object using the cursor method
    cursor = conn.cursor()
    
    # Modify the content table to include filename and userid
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY,
            title TEXT,
            url TEXT,
            content TEXT,
            filename TEXT,
            userid TEXT
        )
    ''')
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

setup_database()

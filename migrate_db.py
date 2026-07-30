import sqlite3
import os

DB_PATH = "patient_data.db"

def migrate():
    print(f"Migrating database: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("Database not found, nothing to migrate (new one will be created correctly).")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("Attempting to add 'action' column to chat_history...")
        cursor.execute('ALTER TABLE chat_history ADD COLUMN action TEXT')
        print("SUCCESS: 'action' column added.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("INFO: 'action' column already exists.")
        else:
            print(f"ERROR: Failed to add column: {e}")
            
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()

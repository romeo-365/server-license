import sqlite3

def add_key(key):
    conn = sqlite3.connect("licenses.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO licenses (key, hwid, is_active) VALUES (?, NULL, 1)", (key,))
        conn.commit()
        print(f"Key '{key}' added successfully!")
    except Exception as e:
        print("Error:", e)
    finally:
        conn.close()

# Example usage:
add_key("USER1-KEY-9876")

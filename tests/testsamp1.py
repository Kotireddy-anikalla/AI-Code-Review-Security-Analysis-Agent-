
import sqlite3

# Hardcoded Secret
API_SECRET_KEY = "sk_live_998877665544332211"

def get_user_data(user_id):
    # SQL Injection Vulnerability
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = '" + user_id + "'"
    cursor.execute(query)
    return cursor.fetchall()

def process_data(data):
    # Code smell: Bare exception and broad handling
    try:
        for i in range(len(data)):
            for j in range(len(data[i])):
                print(data[i][j])
    except:
        pass

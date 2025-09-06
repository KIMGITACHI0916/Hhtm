import sqlite3

DB_PATH = "db/db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS harems (
            user_id INTEGER,
            waifu_name TEXT,
            UNIQUE(user_id, waifu_name)
        )
    ''')
    conn.commit()
    conn.close()

def add_user(user_id, username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
    conn.commit()
    conn.close()

def add_waifu_to_harem(user_id, waifu_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO harems (user_id, waifu_name) VALUES (?, ?)', (user_id, waifu_name))
    conn.commit()
    conn.close()

def get_harem(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT waifu_name FROM harems WHERE user_id=?', (user_id,))
    waifus = [row[0] for row in cursor.fetchall()]
    conn.close()
    return waifus

def get_leaderboard():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, COUNT(*) as count FROM harems GROUP BY user_id ORDER BY count DESC LIMIT 10')
    leaderboard = cursor.fetchall()
    conn.close()
    return leaderboard
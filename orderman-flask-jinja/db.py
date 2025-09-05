import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "orderman.sqlite3"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS menu_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            price REAL NOT NULL CHECK(price > 0)
        )"""
    )
    conn.commit()
    conn.close()

def seed_if_empty():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM menu_items")
    n = cur.fetchone()[0]
    if n == 0:
        cur.executemany(
            "INSERT INTO menu_items(name, description, price) VALUES(?,?,?)",
            [
                ("Маргарита","Томатний соус, моцарела, базилік", 189.00),
                ("Пепероні","Томатний соус, моцарела, пепероні", 209.00),
                ("Гавайська","Соус, моцарела, шинка, ананас", 199.00),
                ("Чотири сири","Моцарела, горгонзола, пармезан, ементаль", 239.00),
            ]
        )
        conn.commit()
    conn.close()

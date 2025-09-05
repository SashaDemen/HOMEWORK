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
    cur.execute(
        """CREATE TABLE IF NOT EXISTS lessons(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            lesson_date TEXT NOT NULL,
            note TEXT DEFAULT ''
        )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS votes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            menu_item_id INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE
        )"""
    )
    conn.commit()
    conn.close()

def seed_if_empty():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM menu_items")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO menu_items(name, description, price) VALUES(?,?,?)",
            [
                ("Маргарита","Томатний соус, моцарела, базилік", 189.00),
                ("Пепероні","Томатний соус, моцарела, пепероні", 209.00),
                ("Гавайська","Соус, моцарела, шинка, ананас", 199.00),
                ("Чотири сири","Моцарела, горгонзола, пармезан, ементаль", 239.00),
            ]
        )
    cur.execute("SELECT COUNT(*) FROM lessons")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO lessons(title, lesson_date, note) VALUES(?,?,?)",
            [
                ("Основи тіста","2025-09-10","М'яке і тонке тісто"),
                ("Сирні секрети","2025-09-12","Як поєднувати чотири сири"),
            ]
        )
    conn.commit()
    conn.close()

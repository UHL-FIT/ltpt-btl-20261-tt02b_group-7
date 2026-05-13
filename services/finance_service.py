import pandas as pd
from models.database import get_connection
import time

class FinanceService:
    def __init__(self):
        pass

    def get_categories(self) -> list:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories ORDER BY id")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r)['name'] for r in rows]

    def add_category(self, name: str):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            conn.commit()
        except Exception:
            pass
        conn.close()


    def add_transaction(self, date: str, amount: float, category: str, t_type: str, note: str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (date, amount, category, type, note)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, amount, category, t_type, note))
        conn.commit()
        conn.close()

    def delete_transactions(self, ids: list):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.executemany('DELETE FROM transactions WHERE id=?', [(i,) for i in ids])
        conn.commit()
        
        cursor.execute('SELECT COUNT(*) FROM transactions')
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='transactions'")
            conn.commit()
            
        conn.close()


    def get_recent_transactions(self, limit=1000, keyword="") -> list:
        conn = get_connection()
        cursor = conn.cursor()
        if keyword:
            query = "SELECT * FROM transactions WHERE category LIKE ? OR note LIKE ? ORDER BY date DESC, id DESC LIMIT ?"
            cursor.execute(query, (f"%{keyword}%", f"%{keyword}%", limit))
        else:
            cursor.execute("SELECT * FROM transactions ORDER BY date DESC, id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

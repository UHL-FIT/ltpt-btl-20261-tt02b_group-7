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

    def update_category_name(self, old_name: str, new_name: str):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE categories SET name=? WHERE name=?", (new_name, old_name))
            cursor.execute("UPDATE transactions SET category=? WHERE category=?", (new_name, old_name))
            conn.commit()
        except Exception:
            pass
        conn.close()

    def delete_category(self, name: str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE name=?", (name,))
        conn.commit()
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

    def update_transaction(self, t_id: int, date: str, amount: float, category: str, t_type: str, note: str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE transactions
            SET date=?, amount=?, category=?, type=?, note=?
            WHERE id=?
        ''', (date, amount, category, t_type, note, t_id))
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

    def import_from_csv(self, filepath: str):
        time.sleep(3.5) # Mô phỏng tác vụ nặng trên 3 giây
        df = pd.read_csv(filepath)
        conn = get_connection()
        df.to_sql('transactions', conn, if_exists='append', index=False)
        conn.close()

    def export_to_csv(self, filepath: str):
        time.sleep(3.5) # Mô phỏng tác vụ nặng trên 3 giây
        df = self.get_all_transactions()
        df.to_csv(filepath, index=False)

    def get_all_transactions(self) -> pd.DataFrame:
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        conn.close()
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'], format='mixed')
            df = df.sort_values(by='date')
        return df

    def get_expenses_by_category(self) -> pd.DataFrame:
        df = self.get_all_transactions()
        if df.empty:
            return pd.DataFrame()
            
        expenses = df[df['type'] == 'Chi tiêu']
        if expenses.empty:
            return pd.DataFrame()
            
        return expenses.groupby('category')['amount'].sum().reset_index()

    def get_spending_trend(self) -> pd.DataFrame:
        time.sleep(3.5) # Mô phỏng tác vụ nặng trên 3 giây
        df = self.get_all_transactions()
        if df.empty:
            return pd.DataFrame()
            
        expenses = df[df['type'] == 'Chi tiêu'].copy()
        if expenses.empty:
            return pd.DataFrame()
            
        # Resample by month
        expenses.set_index('date', inplace=True)
        monthly_expenses = expenses.resample('ME')['amount'].sum().reset_index()
        
        # Calculate Moving Average (3 months)
        monthly_expenses['moving_avg'] = monthly_expenses['amount'].rolling(window=3, min_periods=1).mean()
        
        return monthly_expenses

    def get_recent_transactions(self, limit=None, keyword="") -> list:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM transactions"
        params = []
        
        if keyword:
            query += " WHERE category LIKE ? OR note LIKE ?"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
            
        query += " ORDER BY date DESC, id DESC"
        
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # ─── BUDGET MANAGEMENT ────────────────────────────────────────────────────

    def set_budget(self, category: str, month: str, limit_amount: float, overwrite: bool = False) -> dict:
        """Đặt hoặc cập nhật hạn mức cho danh mục trong tháng.
        Trả về {'status': 'created'|'updated'|'exists', 'old_limit': float|None}
        """
        if limit_amount <= 0:
            raise ValueError("Hạn mức phải lớn hơn 0")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT limit_amount FROM budgets WHERE category=? AND month=?",
            (category, month)
        )
        row = cursor.fetchone()

        if row:
            old_limit = row['limit_amount']
            if not overwrite:
                conn.close()
                return {'status': 'exists', 'old_limit': old_limit}
            cursor.execute(
                "UPDATE budgets SET limit_amount=? WHERE category=? AND month=?",
                (limit_amount, category, month)
            )
            conn.commit()
            conn.close()
            return {'status': 'updated', 'old_limit': old_limit}
        else:
            cursor.execute(
                "INSERT INTO budgets (category, month, limit_amount) VALUES (?, ?, ?)",
                (category, month, limit_amount)
            )
            conn.commit()
            conn.close()
            return {'status': 'created', 'old_limit': None}

    def get_budget(self, category: str, month: str) -> float | None:
        """Trả về hạn mức của danh mục trong tháng, hoặc None nếu chưa đặt."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT limit_amount FROM budgets WHERE category=? AND month=?",
            (category, month)
        )
        row = cursor.fetchone()
        conn.close()
        return row['limit_amount'] if row else None

    def get_all_budgets(self, month: str) -> list:
        """Trả về tất cả hạn mức trong một tháng dưới dạng list dict."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT category, month, limit_amount FROM budgets WHERE month=? ORDER BY category",
            (month,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_budget_history(self, category: str) -> list:
        """Trả về lịch sử hạn mức của một danh mục theo các tháng."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT category, month, limit_amount FROM budgets WHERE category=? ORDER BY month DESC",
            (category,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def copy_budget_from_last_month(self, target_month: str) -> int:
        """Copy toàn bộ hạn mức từ tháng trước sang target_month.
        Trả về số lượng bản ghi đã copy.
        """
        from datetime import datetime, timedelta
        dt = datetime.strptime(target_month, "%Y-%m")
        first_of_target = dt.replace(day=1)
        last_month_dt = first_of_target - timedelta(days=1)
        last_month = last_month_dt.strftime("%Y-%m")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT category, limit_amount FROM budgets WHERE month=?",
            (last_month,)
        )
        rows = cursor.fetchall()
        count = 0
        for r in rows:
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO budgets (category, month, limit_amount) VALUES (?, ?, ?)",
                    (r['category'], target_month, r['limit_amount'])
                )
                if cursor.rowcount > 0:
                    count += 1
            except Exception:
                pass
        conn.commit()
        conn.close()
        return count

    # ─── USAGE & ALERTS ───────────────────────────────────────────────────────

    def get_spent_by_category(self, month: str) -> dict:
        """Tính tổng chi tiêu theo danh mục trong một tháng. Trả về {category: spent}."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT category, SUM(amount) as spent
               FROM transactions
               WHERE type='Chi tiêu' AND strftime('%Y-%m', date) = ?
               GROUP BY category""",
            (month,)
        )
        rows = cursor.fetchall()
        conn.close()
        return {r['category']: r['spent'] for r in rows}

    def get_usage(self, month: str) -> list:
        """Trả về bảng so sánh Hạn mức vs Đã dùng cho một tháng.
        Mỗi phần tử: {category, limit, spent, remaining, pct, status}
        """
        budgets = self.get_all_budgets(month)
        spent_map = self.get_spent_by_category(month)

        rows = []
        for b in budgets:
            cat = b['category']
            limit = b['limit_amount']
            spent = spent_map.get(cat, 0.0)
            remaining = limit - spent
            pct = (spent / limit * 100) if limit > 0 else 0.0

            if pct >= 100:
                status = "🔴 VƯỢT HẠN"
            elif pct >= 80:
                status = "🟡 SẮP VƯỢT"
            else:
                status = "🟢 AN TOÀN"

            rows.append({
                'category': cat,
                'limit': limit,
                'spent': spent,
                'remaining': remaining,
                'pct': pct,
                'status': status,
            })

        # Sắp xếp: vượt hạn → sắp vượt → an toàn
        priority = {"🔴 VƯỢT HẠN": 0, "🟡 SẮP VƯỢT": 1, "🟢 AN TOÀN": 2}
        rows.sort(key=lambda x: (priority.get(x['status'], 3), -x['pct']))
        return rows

    def check_alerts(self, month: str, category: str = None) -> list:
        """Kiểm tra cảnh báo cho một hoặc tất cả danh mục trong tháng.
        Trả về list các alert dict có status != AN TOÀN.
        """
        usage = self.get_usage(month)
        alerts = []
        for row in usage:
            if category and row['category'] != category:
                continue
            if row['pct'] >= 80:
                alerts.append(row)
        return alerts

    # ─── SAVINGS GOALS ────────────────────────────────────────────────────────

    def set_savings_goal(self, month: str, goal_amount: float):
        """Đặt hoặc cập nhật mục tiêu tiết kiệm cho tháng."""
        if goal_amount < 0:
            raise ValueError("Mục tiêu tiết kiệm không thể âm")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO savings_goals (month, goal_amount) VALUES (?, ?) "
            "ON CONFLICT(month) DO UPDATE SET goal_amount=excluded.goal_amount",
            (month, goal_amount)
        )
        conn.commit()
        conn.close()

    def get_savings_goal(self, month: str) -> float:
        """Trả về mục tiêu tiết kiệm của tháng, mặc định 0 nếu chưa đặt."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT goal_amount FROM savings_goals WHERE month=?", (month,))
        row = cursor.fetchone()
        conn.close()
        return row['goal_amount'] if row else 0.0

    def get_savings_progress(self, month: str) -> dict:
        """Tính toán tiến độ tiết kiệm trong tháng.
        Trả về dict: {goal, total_income, total_expense, actual_saving, gap, pct_achieved, status}
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT type, SUM(amount) as total
               FROM transactions
               WHERE strftime('%Y-%m', date) = ?
               GROUP BY type""",
            (month,)
        )
        rows = cursor.fetchall()
        conn.close()

        total_income = 0.0
        total_expense = 0.0
        for r in rows:
            if r['type'] == 'Thu nhập':
                total_income = r['total']
            elif r['type'] == 'Chi tiêu':
                total_expense = r['total']

        goal = self.get_savings_goal(month)
        actual_saving = total_income - total_expense
        gap = actual_saving - goal
        pct_achieved = (actual_saving / goal * 100) if goal > 0 else 0.0

        if goal == 0:
            status = "⚠ Chưa đặt mục tiêu"
        elif actual_saving <= 0:
            status = "❌ Chi vượt thu"
        elif actual_saving >= goal:
            status = "🎉 Đạt mục tiêu"
        else:
            status = "📈 Đang tiến tới"

        return {
            'goal': goal,
            'total_income': total_income,
            'total_expense': total_expense,
            'actual_saving': actual_saving,
            'gap': gap,
            'pct_achieved': pct_achieved,
            'status': status,
        }

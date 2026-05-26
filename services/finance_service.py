import pandas as pd
from models.database import db_session
from utils.logger import logger

# ==========================================
# Tên file: finance_service.py (nằm trong thư mục services)
# Danh sách lớp và chức năng OOP:
# Lớp: FinanceService
# - Chức năng: Đóng vai trò lớp nghiệp vụ (Service Layer) trong mô hình MVC. Thực hiện toàn bộ logic tính toán, quản lý cơ sở dữ liệu (CRUD danh mục, giao dịch, hạn mức ngân sách, mục tiêu tiết kiệm) và tích hợp các thao tác nặng như xuất nhập CSV bằng Pandas.
# Khái niệm OOP sử dụng:
# - Tính trừu tượng (Abstraction): Ẩn giấu cấu trúc truy vấn SQL phức tạp và thuật toán tính toán/xử lý file CSV bằng các phương thức nghiệp vụ rõ ràng, trực quan (như get_usage, check_alerts, export_to_csv).
# - Nguyên tắc đơn nhiệm (Single Responsibility Principle - SRP): Lớp này chỉ chịu trách nhiệm duy nhất về logic nghiệp vụ tài chính và lưu trữ dữ liệu của hệ thống, hoàn toàn độc lập với giao diện người dùng.
# - Quản lý trạng thái và đóng gói (Encapsulation): Các thao tác kết nối, thực thi và ngắt kết nối SQLite được thực hiện khép kín và an toàn trong nội bộ từng phương thức thông qua cơ chế db_session.
# ==========================================


class FinanceService:
    def __init__(self):
        logger.debug("Khởi tạo FinanceService thành công.")

    def get_categories(self) -> list:
        logger.debug("Gọi get_categories()")
        try:
            with db_session(commit=False) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM categories ORDER BY id")
                rows = cursor.fetchall()
                categories = [dict(r)['name'] for r in rows]
            logger.debug(f"Kết quả get_categories(): Lấy ra {len(categories)} danh mục.")
            return categories
        except Exception as e:
            logger.error(f"Lỗi khi lấy danh sách danh mục: {str(e)}", exc_info=True)
            raise

    def add_category(self, name: str):
        logger.info(f"Yêu cầu thêm danh mục mới: name='{name}'")
        try:
            with db_session(commit=True) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            logger.info(f"Đã thêm thành công danh mục: '{name}'")
        except Exception as e:
            logger.error(f"Lỗi khi thêm danh mục '{name}': {str(e)}", exc_info=True)

    def update_category_name(self, old_name: str, new_name: str):
        logger.info(f"Yêu cầu cập nhật danh mục: '{old_name}' -> '{new_name}'")
        try:
            with db_session(commit=True) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE categories SET name=? WHERE name=?", (new_name, old_name))
                cursor.execute("UPDATE transactions SET category=? WHERE category=?", (new_name, old_name))
            logger.info(f"Cập nhật thành công danh mục từ '{old_name}' thành '{new_name}'")
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật tên danh mục: {str(e)}", exc_info=True)

    def delete_category(self, name: str):
        logger.info(f"Yêu cầu xóa danh mục: name='{name}'")
        try:
            with db_session(commit=True) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM categories WHERE name=?", (name,))
            logger.info(f"Đã xóa thành công danh mục: '{name}'")
        except Exception as e:
            logger.error(f"Lỗi khi xóa danh mục '{name}': {str(e)}", exc_info=True)
            raise

    def add_transaction(self, date: str, amount: float, category: str, t_type: str, note: str):
        logger.info(f"Yêu cầu thêm giao dịch: date='{date}', amount={amount}, category='{category}', type='{t_type}', note='{note}'")
        try:
            with db_session(commit=True) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO transactions (date, amount, category, type, note)
                    VALUES (?, ?, ?, ?, ?)
                ''', (date, amount, category, t_type, note))
            logger.info("Đã thêm thành công giao dịch vào cơ sở dữ liệu.")
        except Exception as e:
            logger.error(f"Lỗi khi thêm giao dịch: {str(e)}", exc_info=True)
            raise

    def update_transaction(self, t_id: int, date: str, amount: float, category: str, t_type: str, note: str):
        logger.info(f"Yêu cầu sửa giao dịch: date='{date}', amount={amount}, category='{category}', type='{t_type}', note='{note}'")
        try:
            with db_session(commit=True) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE transactions
                    SET date=?, amount=?, category=?, type=?, note=?
                    WHERE id=?
                ''', (date, amount, category, t_type, note, t_id))
            logger.info(f"Đã cập nhật thành công giao dịch")
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật giao dịch: {str(e)}", exc_info=True)
            raise

    def delete_transactions(self, ids: list):
        logger.info(f"Yêu cầu xóa các giao dịch")
        try:
            with db_session(commit=True) as conn:
                cursor = conn.cursor()
                cursor.executemany('DELETE FROM transactions WHERE id=?', [(i,) for i in ids])
                
                cursor.execute('SELECT COUNT(*) FROM transactions')
                count = cursor.fetchone()[0]
                if count == 0:
                    logger.warning("Bảng transactions đã trống hoàn toàn. Reset autoincrement sequence...")
                    cursor.execute("DELETE FROM sqlite_sequence WHERE name='transactions'")
            logger.info(f"Đã xóa thành công {len(ids)} giao dịch.")
        except Exception as e:
            logger.error(f"Lỗi khi xóa các giao dịch {ids}: {str(e)}", exc_info=True)
            raise

    def import_from_csv(self, filepath: str):
        logger.info(f"Bắt đầu nhập giao dịch từ file CSV: {filepath}")
        try:
            # Hỗ trợ tự động nhận diện separator và xử lý BOM
            df = pd.read_csv(filepath, sep=None, engine='python', encoding='utf-8-sig')
            logger.debug(f"Đã đọc file CSV. Số dòng dữ liệu thô: {len(df)}")

            # Xóa các dòng trống hoàn toàn
            df = df.dropna(how='all')
            
            # Chuẩn hóa tên cột: loại bỏ khoảng trắng và in thường để dễ khớp
            df = df.rename(columns={col: col.strip().lower() for col in df.columns})

            if 'id' in df.columns:
                df = df.drop(columns=['id'])
                logger.debug("Đã loại bỏ cột 'id' để DB tự động sinh khóa chính.")

            required_columns = ['date', 'amount', 'category', 'type']
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                raise ValueError(f"File CSV thiếu cột bắt buộc: {', '.join(missing_cols)}")

            if df.empty:
                raise ValueError("File CSV không chứa dữ liệu giao dịch nào hợp lệ.")

            # Đảm bảo cột note tồn tại và không chứa giá trị NaN
            if 'note' not in df.columns:
                df['note'] = ''
            else:
                df['note'] = df['note'].fillna('').astype(str)

            # Làm sạch dữ liệu trước khi chuyển đổi
            # Loại bỏ dấu phẩy trong số tiền (nếu có do export từ Excel)
            if df['amount'].dtype == object:
                df['amount'] = df['amount'].astype(str).str.replace(',', '', regex=False)

            # Chuẩn hóa dữ liệu trước khi ghi vào DB
            # Hỗ trợ hỗn hợp định dạng ngày và tránh dùng dayfirst=True vì nó làm sai lệch YYYY-MM-DD thành YYYY-DD-MM
            df['date'] = pd.to_datetime(df['date'], format='mixed', errors='coerce')
            if df['date'].isnull().any():
                raise ValueError("Cột 'date' chứa định dạng ngày tháng không hợp lệ.")
            df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')

            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            if df['amount'].isnull().any():
                raise ValueError("Cột 'amount' chứa dữ liệu không phải là số hợp lệ.")

            df['category'] = df['category'].astype(str).str.strip()
            df['type'] = df['type'].astype(str).str.strip()

            rows = df[['date', 'amount', 'category', 'type', 'note']].values.tolist()
            with db_session(commit=True) as conn:
                cursor = conn.cursor()
                cursor.executemany(
                    '''INSERT INTO transactions (date, amount, category, type, note)
                       VALUES (?, ?, ?, ?, ?)''',
                    rows
                )

            logger.info(f"Nhập dữ liệu thành công! Đã thêm {len(rows)} dòng dữ liệu từ CSV vào bảng transactions.")
        except Exception as e:
            logger.error(f"Lỗi khi nhập dữ liệu từ file CSV: {str(e)}", exc_info=True)
            raise

    def export_to_csv(self, filepath: str):
        logger.info(f"Bắt đầu xuất giao dịch ra file CSV: {filepath}")
        try:
            df = self.get_all_transactions()
            if df.empty:
                logger.warning("Không có dữ liệu giao dịch nào để xuất ra file CSV.")
                # Vẫn ghi file CSV trống có headers
                df_headers = pd.DataFrame(columns=['date', 'amount', 'category', 'type', 'note'])
                df_headers.to_csv(filepath, index=False)
                logger.info(f"Đã xuất file CSV trống có headers tại {filepath}")
                return
                
            if 'id' in df.columns:
                df = df.drop(columns=['id'])
                
            df.to_csv(filepath, index=False)
            logger.info(f"Xuất file CSV thành công! Đã ghi {len(df)} giao dịch vào {filepath}")
        except Exception as e:
            logger.error(f"Lỗi khi xuất dữ liệu ra file CSV: {str(e)}", exc_info=True)
            raise

    def export_selected_to_csv(self, filepath: str, selected_ids: list):
        logger.info(f"Bắt đầu xuất các giao dịch được chọn ra file CSV: {filepath}")
        try:
            with db_session(commit=False) as conn:
                placeholders = ",".join("?" for _ in selected_ids)
                query = f"SELECT * FROM transactions WHERE id IN ({placeholders})"
                df = pd.read_sql_query(query, conn, params=selected_ids)
            
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'], format='mixed')
                df = df.sort_values(by='date')
                
            if 'id' in df.columns:
                df = df.drop(columns=['id'])
                
            df.to_csv(filepath, index=False)
            logger.info(f"Xuất file CSV các giao dịch được chọn thành công! Đã ghi {len(df)} giao dịch vào {filepath}")
        except Exception as e:
            logger.error(f"Lỗi khi xuất dữ liệu được chọn ra file CSV: {str(e)}", exc_info=True)
            raise

    def get_all_transactions(self) -> pd.DataFrame:
        logger.debug("Gọi get_all_transactions()")
        try:
            with db_session(commit=False) as conn:
                df = pd.read_sql_query("SELECT * FROM transactions", conn)
            
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'], format='mixed')
                df = df.sort_values(by='date')
            logger.debug(f"Kết quả get_all_transactions(): Lấy ra {len(df)} giao dịch.")
            return df
        except Exception as e:
            logger.error(f"Lỗi khi lấy toàn bộ danh sách giao dịch: {str(e)}", exc_info=True)
            return pd.DataFrame()

    def get_expenses_by_category(self) -> pd.DataFrame:
        logger.debug("Gọi get_expenses_by_category()")
        try:
            df = self.get_all_transactions()
            if df.empty:
                logger.debug("Không có dữ liệu giao dịch nào để tính toán cơ cấu chi tiêu.")
                return pd.DataFrame()
                
            expenses = df[df['type'] == 'Chi tiêu']
            if expenses.empty:
                logger.debug("Không có dữ liệu giao dịch dạng 'Chi tiêu'.")
                return pd.DataFrame()
                
            res = expenses.groupby('category')['amount'].sum().reset_index()
            logger.debug(f"Tính cơ cấu chi tiêu thành công. Số nhóm chi tiêu: {len(res)}")
            return res
        except Exception as e:
            logger.error(f"Lỗi khi tính cơ cấu chi tiêu theo nhóm: {str(e)}", exc_info=True)
            return pd.DataFrame()

    def get_spending_trend(self) -> pd.DataFrame:
        logger.debug("Gọi get_spending_trend() - chạy biểu đồ xu hướng chi tiêu")
        try:
            df = self.get_all_transactions()
            if df.empty:
                logger.debug("Không có dữ liệu giao dịch để lập biểu đồ xu hướng.")
                return pd.DataFrame()
                
            expenses = df[df['type'] == 'Chi tiêu'].copy()
            if expenses.empty:
                logger.debug("Không có giao dịch 'Chi tiêu' nào để lập biểu đồ xu hướng.")
                return pd.DataFrame()
                
            # Resample by month
            expenses.set_index('date', inplace=True)
            monthly_expenses = expenses.resample('ME')['amount'].sum().reset_index()
            
            # Calculate Moving Average (3 months)
            monthly_expenses['moving_avg'] = monthly_expenses['amount'].rolling(window=3, min_periods=1).mean()
            logger.debug(f"Tính toán xu hướng chi tiêu thành công. Số tháng: {len(monthly_expenses)}")
            return monthly_expenses
        except Exception as e:
            logger.error(f"Lỗi khi tính toán xu hướng chi tiêu: {str(e)}", exc_info=True)
            return pd.DataFrame()

    def get_recent_transactions(self, limit=None, keyword="") -> list:
        logger.debug(f"Gọi get_recent_transactions(limit={limit}, keyword='{keyword}')")
        try:
            with db_session(commit=False) as conn:
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
                transactions = [dict(row) for row in rows]
            logger.debug(f"Lấy danh sách giao dịch gần đây thành công: Tìm thấy {len(transactions)} bản ghi.")
            return transactions
        except Exception as e:
            logger.error(f"Lỗi khi truy vấn danh sách giao dịch gần đây: {str(e)}", exc_info=True)
            return []

    # ─── BUDGET MANAGEMENT ────────────────────────────────────────────────────

    def set_budget(self, category: str, month: str, limit_amount: float, overwrite: bool = False) -> dict:
        logger.info(f"Yêu cầu đặt hạn mức ngân sách: category='{category}', month='{month}', limit_amount={limit_amount}, overwrite={overwrite}")
        if limit_amount <= 0:
            logger.error("Hạn mức phải lớn hơn 0")
            raise ValueError("Hạn mức phải lớn hơn 0")
            
        try:
            with db_session(commit=True) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT limit_amount FROM budgets WHERE category=? AND month=?",
                    (category, month)
                )
                row = cursor.fetchone()

                if row:
                    old_limit = row['limit_amount']
                    if not overwrite:
                        logger.warning(f"Ngân sách cho '{category}' trong tháng {month} đã tồn tại: {old_limit}. Trả về trạng thái exists.")
                        return {'status': 'exists', 'old_limit': old_limit}
                    cursor.execute(
                        "UPDATE budgets SET limit_amount=? WHERE category=? AND month=?",
                        (limit_amount, category, month)
                    )
                    logger.info(f"Đã cập nhật đè hạn mức ngân sách cho '{category}' ({month}) từ {old_limit} sang {limit_amount}")
                    return {'status': 'updated', 'old_limit': old_limit}
                else:
                    cursor.execute(
                        "INSERT INTO budgets (category, month, limit_amount) VALUES (?, ?, ?)",
                        (category, month, limit_amount)
                    )
                    logger.info(f"Đã thêm mới hạn mức ngân sách cho '{category}' ({month}): {limit_amount}")
                    return {'status': 'created', 'old_limit': None}
        except Exception as e:
            logger.error(f"Lỗi khi thiết lập ngân sách: {str(e)}", exc_info=True)
            raise

    def delete_budget(self, category: str, month: str):
        logger.info(f"Yêu cầu xóa hạn mức ngân sách: category='{category}', month='{month}'")
        try:
            with db_session(commit=True) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM budgets WHERE category=? AND month=?",
                    (category, month)
                )
            logger.info(f"Đã xóa thành công hạn mức ngân sách cho '{category}' ({month})")
        except Exception as e:
            logger.error(f"Lỗi khi xóa hạn mức ngân sách: {str(e)}", exc_info=True)
            raise

    def get_budget(self, category: str, month: str) -> float | None:
        logger.debug(f"Gọi get_budget(category='{category}', month='{month}')")
        try:
            with db_session(commit=False) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT limit_amount FROM budgets WHERE category=? AND month=?",
                    (category, month)
                )
                row = cursor.fetchone()
                res = row['limit_amount'] if row else None
            logger.debug(f"Kết quả get_budget(): Hạn mức={res}")
            return res
        except Exception as e:
            logger.error(f"Lỗi khi lấy hạn mức ngân sách: {str(e)}", exc_info=True)
            return None

    def get_all_budgets(self, month: str) -> list:
        logger.debug(f"Gọi get_all_budgets(month='{month}')")
        try:
            with db_session(commit=False) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT category, month, limit_amount FROM budgets WHERE month=? ORDER BY category",
                    (month,)
                )
                rows = cursor.fetchall()
                budgets = [dict(r) for r in rows]
            logger.debug(f"Kết quả get_all_budgets(): Tìm thấy {len(budgets)} hạn mức.")
            return budgets
        except Exception as e:
            logger.error(f"Lỗi khi lấy toàn bộ ngân sách tháng {month}: {str(e)}", exc_info=True)
            return []

    def get_budget_history(self, category: str) -> list:
        logger.debug(f"Gọi get_budget_history(category='{category}')")
        try:
            with db_session(commit=False) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT category, month, limit_amount FROM budgets WHERE category=? ORDER BY month DESC",
                    (category,)
                )
                rows = cursor.fetchall()
                history = [dict(r) for r in rows]
            logger.debug(f"Kết quả get_budget_history(): Lấy ra {len(history)} dòng lịch sử.")
            return history
        except Exception as e:
            logger.error(f"Lỗi khi lấy lịch sử ngân sách nhóm '{category}': {str(e)}", exc_info=True)
            return []

    def copy_budget_from_last_month(self, target_month: str) -> int:
        logger.info(f"Yêu cầu sao chép ngân sách từ tháng trước sang tháng {target_month}")
        try:
            from datetime import datetime, timedelta
            dt = datetime.strptime(target_month, "%Y-%m")
            first_of_target = dt.replace(day=1)
            last_month_dt = first_of_target - timedelta(days=1)
            last_month = last_month_dt.strftime("%Y-%m")
            
            logger.debug(f"Xác định tháng trước là: {last_month}")

            with db_session(commit=True) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT category, limit_amount FROM budgets WHERE month=?",
                    (last_month,)
                )
                rows = cursor.fetchall()
                
                if not rows:
                    logger.warning(f"Tháng trước ({last_month}) chưa được thiết lập ngân sách. Kết thúc tác vụ copy.")
                    return 0
                    
                count = 0
                for r in rows:
                    try:
                        cursor.execute(
                            "INSERT OR IGNORE INTO budgets (category, month, limit_amount) VALUES (?, ?, ?)",
                            (r['category'], target_month, r['limit_amount'])
                        )
                        if cursor.rowcount > 0:
                            count += 1
                            logger.debug(f"Đã copy ngân sách cho nhóm '{r['category']}': {r['limit_amount']}")
                    except Exception as ex:
                        logger.error(f"Lỗi khi sao chép dòng ngân sách nhóm '{r['category']}': {str(ex)}", exc_info=True)
            logger.info(f"Hoàn thành sao chép ngân sách. Đã copy thành công {count} bản ghi.")
            return count
        except Exception as e:
            logger.error(f"Lỗi hệ thống khi sao chép ngân sách từ tháng trước: {str(e)}", exc_info=True)
            return 0

    # ─── USAGE & ALERTS ───────────────────────────────────────────────────────

    def get_spent_by_category(self, month: str) -> dict:
        logger.debug(f"Gọi get_spent_by_category(month='{month}')")
        try:
            with db_session(commit=False) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT category, SUM(amount) as spent
                       FROM transactions
                       WHERE type='Chi tiêu' AND strftime('%Y-%m', date) = ?
                       GROUP BY category""",
                    (month,)
                )
                rows = cursor.fetchall()
                res = {r['category']: r['spent'] for r in rows}
            logger.debug(f"Kết quả get_spent_by_category(): {res}")
            return res
        except Exception as e:
            logger.error(f"Lỗi khi tính toán thực chi theo nhóm trong tháng {month}: {str(e)}", exc_info=True)
            return {}

    def get_usage(self, month: str) -> list:
        logger.debug(f"Gọi get_usage(month='{month}')")
        try:
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

            # Sắp xếp: vượt hạn -> sắp vượt -> an toàn
            priority = {"🔴 VƯỢT HẠN": 0, "🟡 SẮP VƯỢT": 1, "🟢 AN TOÀN": 2}
            rows.sort(key=lambda x: (priority.get(x['status'], 3), -x['pct']))
            logger.debug(f"Lấy biểu đồ sử dụng ngân sách tháng {month} thành công. Số danh mục: {len(rows)}")
            return rows
        except Exception as e:
            logger.error(f"Lỗi khi tính toán ngân sách sử dụng trong tháng {month}: {str(e)}", exc_info=True)
            return []

    def check_alerts(self, month: str, category: str = None) -> list:
        logger.debug(f"Gọi check_alerts(month='{month}', category={category})")
        try:
            usage = self.get_usage(month)
            alerts = []
            for row in usage:
                if category and row['category'] != category:
                    continue
                if row['pct'] >= 80:
                    alerts.append(row)
            logger.debug(f"Kết quả check_alerts(): Có {len(alerts)} cảnh báo vượt/sắp vượt hạn mức.")
            return alerts
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra cảnh báo hạn mức: {str(e)}", exc_info=True)
            return []

    # ─── SAVINGS GOALS ────────────────────────────────────────────────────────

    def set_savings_goal(self, month: str, goal_amount: float):
        logger.info(f"Yêu cầu đặt mục tiêu tiết kiệm: month='{month}', goal_amount={goal_amount}")
        if goal_amount < 0:
            logger.error("Mục tiêu tiết kiệm không thể âm")
            raise ValueError("Mục tiêu tiết kiệm không thể âm")
            
        try:
            with db_session(commit=True) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO savings_goals (month, goal_amount) VALUES (?, ?) "
                    "ON CONFLICT(month) DO UPDATE SET goal_amount=excluded.goal_amount",
                    (month, goal_amount)
                )
            logger.info(f"Lưu mục tiêu tiết kiệm thành công cho tháng {month}.")
        except Exception as e:
            logger.error(f"Lỗi khi lưu mục tiêu tiết kiệm: {str(e)}", exc_info=True)
            raise

    def get_savings_goal(self, month: str) -> float:
        logger.debug(f"Gọi get_savings_goal(month='{month}')")
        try:
            with db_session(commit=False) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT goal_amount FROM savings_goals WHERE month=?", (month,))
                row = cursor.fetchone()
                res = row['goal_amount'] if row else 0.0
            logger.debug(f"Kết quả get_savings_goal(): Mục tiêu={res} ₫")
            return res
        except Exception as e:
            logger.error(f"Lỗi khi lấy mục tiêu tiết kiệm: {str(e)}", exc_info=True)
            return 0.0

    def get_savings_progress(self, month: str) -> dict:
        logger.debug(f"Gọi get_savings_progress(month='{month}')")
        try:
            with db_session(commit=False) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT type, SUM(amount) as total
                       FROM transactions
                       WHERE strftime('%Y-%m', date) = ?
                       GROUP BY type""",
                    (month,)
                )
                rows = cursor.fetchall()

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

            progress = {
                'goal': goal,
                'total_income': total_income,
                'total_expense': total_expense,
                'actual_saving': actual_saving,
                'gap': gap,
                'pct_achieved': pct_achieved,
                'status': status,
            }
            logger.debug(f"Tính toán tiến độ tiết kiệm thành công: {progress}")
            return progress
        except Exception as e:
            logger.error(f"Lỗi khi tính toán tiến trình tiết kiệm tháng {month}: {str(e)}", exc_info=True)
            return {}



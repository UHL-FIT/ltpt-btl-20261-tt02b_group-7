import sqlite3
import os
from contextlib import contextmanager
from utils.logger import logger

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'finance.db')

# ==========================================
# Tên file: database.py (nằm trong thư mục models)
# Chức năng: Quản lý kết nối SQLite và khởi tạo cấu trúc cơ sở dữ liệu cho ứng dụng.
# Khái niệm OOP sử dụng:
# - Đóng gói cấp Module (Module-level Encapsulation): Các chức năng thiết lập kết nối và tạo bảng được đóng gói trong một file riêng biệt để các đối tượng Model/Service sử dụng mà không cần biết chi tiết triển khai cụ thể bên dưới.
# ==========================================


def get_connection():
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        logger.debug(f"Đang kết nối tới SQLite Database: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        logger.debug("Kết nối SQLite thành công.")
        return conn
    except Exception as e:
        logger.error(f"Lỗi khi thiết lập kết nối Database: {str(e)}", exc_info=True)
        raise

@contextmanager
def db_session(commit: bool = False):
    """
    Context manager để quản lý kết nối và phiên làm việc với SQLite Database.
    Tự động đóng kết nối (close) và thực hiện commit/rollback nếu yêu cầu.
    """
    conn = get_connection()
    try:
        yield conn
        if commit:
            conn.commit()
            logger.debug("Database transaction committed thành công.")
    except Exception as e:
        if commit:
            try:
                conn.rollback()
                logger.warning("Đã rollback database transaction do phát sinh lỗi.")
            except Exception:
                pass
        raise e
    finally:
        conn.close()
        logger.debug("Đã đóng kết nối Database an toàn qua db_session.")

def initialize_db():
    logger.info("Bắt đầu khởi tạo các bảng cơ sở dữ liệu...")
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        logger.debug("Đang tạo bảng transactions nếu chưa tồn tại...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                type TEXT NOT NULL,
                note TEXT
            )
        ''')
        
        logger.debug("Đang tạo bảng categories nếu chưa tồn tại...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        
        logger.debug("Đang tạo bảng budgets nếu chưa tồn tại...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                month TEXT NOT NULL,
                limit_amount REAL NOT NULL,
                UNIQUE(category, month)
            )
        ''')
        
        logger.debug("Đang tạo bảng savings_goals nếu chưa tồn tại...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT NOT NULL UNIQUE,
                goal_amount REAL NOT NULL
            )
        ''')
        
        logger.debug("Kiểm tra và nạp danh mục mặc định...")
        cursor.execute('SELECT COUNT(*) FROM categories')
        if cursor.fetchone()[0] == 0:
            default_cats = ["Ăn uống", "Di chuyển", "Tiền thuê", "Giải trí", "Tiền lương", "Khác"]
            logger.info(f"Nạp danh mục mặc định: {default_cats}")
            cursor.executemany('INSERT INTO categories (name) VALUES (?)', [(c,) for c in default_cats])
            
        conn.commit()
        logger.info("Tất cả các bảng DB đã được khởi tạo và commit thành công.")
    except Exception as e:
        logger.error(f"Lỗi trong quá trình khởi tạo cấu trúc DB: {str(e)}", exc_info=True)
        if conn:
            conn.rollback()
            logger.warning("Đã thực hiện rollback giao dịch do phát sinh lỗi DB.")
        raise
    finally:
        if conn:
            conn.close()
            logger.debug("Đã đóng kết nối Database an toàn.")

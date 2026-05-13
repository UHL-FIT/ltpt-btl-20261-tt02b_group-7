import threading
from services.finance_service import FinanceService

class MainController:
    # Khởi tạo MainController, kết nối View và Service
    def __init__(self, view):
        self.view = view
        self.service = FinanceService()
        
    # Thêm một giao dịch mới vào cơ sở dữ liệu
    def add_transaction(self, date: str, amount: float, category: str, t_type: str, note: str):
        db_date = self._parse_date(date)
        if not db_date: return
            
        try:
            self.service.add_transaction(db_date, amount, category, t_type, note)
            self.view.show_message("Thành công", "Đã thêm giao dịch thành công!")
            self.refresh_history()
        except Exception as e:
            self.view.show_error("Lỗi", f"Không thể thêm giao dịch: {str(e)}")

    def delete_transactions(self, ids: list):
        if not ids: return
        try:
            self.service.delete_transactions(ids)
            self.view.show_message("Thành công", "Xóa thành công!")
            self.refresh_history()
        except Exception as e:
            self.view.show_error("Lỗi", f"Không thể xóa: {str(e)}")


    # Chuyển đổi định dạng ngày tháng từ chuỗi (DD/MM/YYYY HH:MM) sang dạng chuẩn cho Database
    def _parse_date(self, date: str):
        from datetime import datetime
        try:
            parsed_date = datetime.strptime(date, "%d/%m/%Y %H:%M")
            return parsed_date.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            self.view.show_error("Lỗi", "Ngày giờ không đúng định dạng DD/MM/YYYY HH:MM.")
            return None
            
        
    # Làm mới danh sách lịch sử giao dịch
    def refresh_history(self):
        transactions = self.service.get_recent_transactions()
        self.view.update_history(transactions)

    # Tải dữ liệu ban đầu khi khởi động ứng dụng
    def load_initial_data(self):
        self.refresh_history()

    # Lấy danh sách tất cả các danh mục
    def get_categories(self):
        return self.service.get_categories()

    # Thêm một danh mục mới
    def add_category(self, name):
        if not name.strip(): return
        self.service.add_category(name.strip())


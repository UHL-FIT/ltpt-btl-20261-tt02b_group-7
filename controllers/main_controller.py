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
            self.refresh_dashboard()
            self.refresh_history()
            # Auto-check alerts sau khi thêm giao dịch chi tiêu
            if t_type == "Chi tiêu":
                from datetime import datetime
                month = datetime.strptime(db_date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m")
                alerts = self.service.check_alerts(month, category=category)
                for a in alerts:
                    if a['pct'] >= 100:
                        self.view.show_error("⚠ Vượt hạn", f"🔴 {category}: đã dùng {a['pct']:.1f}% hạn mức!")
                    elif a['pct'] >= 80:
                        self.view.show_message("⚠ Sắp vượt", f"🟡 {category}: đã dùng {a['pct']:.1f}% — còn {a['remaining']:,.0f} ₫")
        except Exception as e:
            self.view.show_error("Lỗi", f"Không thể thêm giao dịch: {str(e)}")

    # Cập nhật thông tin của một giao dịch đã tồn tại
    def update_transaction(self, t_id: int, date: str, amount: float, category: str, t_type: str, note: str):
        db_date = self._parse_date(date)
        if not db_date: return
        
        try:
            self.service.update_transaction(t_id, db_date, amount, category, t_type, note)
            self.view.show_message("Thành công", "Cập nhật thành công!")
            self.refresh_dashboard()
            self.refresh_history()
        except Exception as e:
            self.view.show_error("Lỗi", f"Lỗi cập nhật: {str(e)}")
            
    # Xóa nhiều giao dịch theo danh sách ID
    def delete_transactions(self, ids: list):
        if not ids: return
        try:
            self.service.delete_transactions(ids)
            self.view.show_message("Thành công", "Xóa thành công!")
            self.refresh_dashboard()
            self.refresh_history()
        except Exception as e:
            self.view.show_error("Lỗi", f"Không thể xóa: {str(e)}")
            
    # Nhập dữ liệu giao dịch từ file CSV (chạy nền)
    def import_csv(self, filepath: str):
        self.view.show_loading("Đang nhập dữ liệu...")
        def task():
            try:
                self.service.import_from_csv(filepath)
                self.view.after(0, lambda: self._on_import_success())
            except Exception as e:
                self.view.after(0, lambda err=e: self._on_import_error(err))
        threading.Thread(target=task, daemon=True).start()

    # Xử lý khi nhập dữ liệu CSV thành công
    def _on_import_success(self):
        self.view.hide_loading()
        self.view.show_message("Thành công", "Nhập dữ liệu thành công!")
        self.refresh_dashboard()
        self.refresh_history()

    # Xử lý khi nhập dữ liệu CSV thất bại
    def _on_import_error(self, e):
        self.view.hide_loading()
        self.view.show_error("Lỗi", f"Lỗi nhập dữ liệu: {str(e)}")

    # Xuất dữ liệu giao dịch ra file CSV (chạy nền)
    def export_csv(self, filepath: str):
        self.view.show_loading("Đang xuất dữ liệu...")
        def task():
            try:
                self.service.export_to_csv(filepath)
                self.view.after(0, lambda: self._on_export_success())
            except Exception as e:
                self.view.after(0, lambda err=e: self._on_export_error(err))
        threading.Thread(target=task, daemon=True).start()

    # Xử lý khi xuất dữ liệu CSV thành công
    def _on_export_success(self):
        self.view.hide_loading()
        self.view.show_message("Thành công", "Xuất dữ liệu thành công!")

    # Xử lý khi xuất dữ liệu CSV thất bại
    def _on_export_error(self, e):
        self.view.hide_loading()
        self.view.show_error("Lỗi", f"Lỗi xuất dữ liệu: {str(e)}")
            
    # Tìm kiếm giao dịch theo từ khóa
    def search_transactions(self, keyword: str):
        transactions = self.service.get_recent_transactions(keyword=keyword)
        self.view.update_history(transactions)

    # Sắp xếp danh sách giao dịch
    def sort_transactions(self, sort_by: str):
        # We can implement simple client side sorting or DB sorting. For now we use get_recent_transactions and sort it.
        transactions = self.service.get_recent_transactions()
        if sort_by == "Mới nhất":
            transactions.sort(key=lambda x: x['date'], reverse=True)
        elif sort_by == "Cũ nhất":
            transactions.sort(key=lambda x: x['date'], reverse=False)
        elif sort_by == "Số tiền giảm dần":
            transactions.sort(key=lambda x: x['amount'], reverse=True)
        elif sort_by == "Số tiền tăng dần":
            transactions.sort(key=lambda x: x['amount'], reverse=False)
            
        self.view.update_history(transactions)

    # Chuyển đổi định dạng ngày tháng từ chuỗi (DD/MM/YYYY HH:MM) sang dạng chuẩn cho Database
    def _parse_date(self, date: str):
        from datetime import datetime
        try:
            parsed_date = datetime.strptime(date, "%d/%m/%Y %H:%M")
            return parsed_date.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            self.view.show_error("Lỗi", "Ngày giờ không đúng định dạng DD/MM/YYYY HH:MM.")
            return None
            
    # Làm mới dữ liệu biểu đồ trên Dashboard (chạy nền)
    def refresh_dashboard(self):
        if hasattr(self.view, 'dashboard_window') and self.view.dashboard_window and self.view.dashboard_window.winfo_exists():
            self.view.show_loading("Đang tải biểu đồ...")
            def task():
                try:
                    category_data = self.service.get_expenses_by_category()
                    trend_data = self.service.get_spending_trend()
                    self.view.after(0, lambda: self._on_dashboard_success(category_data, trend_data))
                except Exception as e:
                    self.view.after(0, lambda err=e: self._on_dashboard_error(err))
            threading.Thread(target=task, daemon=True).start()

    # Xử lý khi tải dữ liệu biểu đồ Dashboard thành công
    def _on_dashboard_success(self, category_data, trend_data):
        self.view.hide_loading()
        if hasattr(self.view, 'dashboard_window') and self.view.dashboard_window and self.view.dashboard_window.winfo_exists():
            self.view.update_charts(category_data, trend_data)
            
    # Xử lý khi tải dữ liệu biểu đồ Dashboard thất bại
    def _on_dashboard_error(self, e):
        self.view.hide_loading()
        self.view.show_error("Lỗi", f"Lỗi tải biểu đồ: {str(e)}")
        
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

    # Cập nhật tên của một danh mục
    def update_category(self, old_name, new_name):
        if not new_name.strip(): return
        self.service.update_category_name(old_name, new_name.strip())
        self.refresh_history()

    # Xóa một danh mục
    def delete_category(self, name):
        self.service.delete_category(name)

    # ─── BUDGET MANAGEMENT ────────────────────────────────────────────────────

    def set_budget(self, category: str, month: str, limit_amount: float, overwrite: bool = False) -> dict:
        """Đặt hạn mức cho danh mục trong tháng. Trả về result dict từ service."""
        return self.service.set_budget(category, month, limit_amount, overwrite)

    def get_all_budgets(self, month: str) -> list:
        return self.service.get_all_budgets(month)

    def get_budget_history(self, category: str) -> list:
        return self.service.get_budget_history(category)

    def copy_budget_from_last_month(self, target_month: str) -> int:
        return self.service.copy_budget_from_last_month(target_month)

    # ─── USAGE & ALERTS ───────────────────────────────────────────────────────

    def get_usage(self, month: str) -> list:
        return self.service.get_usage(month)

    def check_alerts(self, month: str, category: str = None) -> list:
        return self.service.check_alerts(month, category)

    # ─── SAVINGS GOALS ────────────────────────────────────────────────────────

    def set_savings_goal(self, month: str, goal_amount: float):
        self.service.set_savings_goal(month, goal_amount)

    def get_savings_progress(self, month: str) -> dict:
        return self.service.get_savings_progress(month)

    def get_savings_goal(self, month: str) -> float:
        return self.service.get_savings_goal(month)

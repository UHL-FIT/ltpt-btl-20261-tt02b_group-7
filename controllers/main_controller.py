import threading
from services.finance_service import FinanceService
from utils.logger import logger

# ==========================================
# Tên file: main_controller.py (nằm trong thư mục controllers)
# Danh sách lớp và chức năng OOP:
# Lớp: MainController
# - Chức năng: Đóng vai trò bộ điều phối trung tâm (Controller) trong mô hình MVC. Lớp này tiếp nhận các sự kiện, yêu cầu của người dùng từ View (MainWindow), ủy quyền xử lý nghiệp vụ cho FinanceService, và cập nhật dữ liệu phản hồi lại View.
# Khái niệm OOP sử dụng:
# - Mô hình kiến trúc MVC (Model-View-Controller): Tách biệt mối quan tâm giữa phần hiển thị (View) và phần xử lý logic/dữ liệu (Model/Service).
# - Tính đóng gói (Encapsulation): Thuộc tính self.view và self.service được bảo vệ bên trong đối tượng. Các phương thức trợ giúp nội bộ như _parse_date, _on_import_success,... được khai báo bắt đầu bằng dấu gạch dưới (_) thể hiện cơ chế đóng gói bảo mật thông tin (Information Hiding/Private methods).
# - Giao tiếp đối tượng (Object Collaboration): Phối hợp hành vi linh hoạt giữa các đối tượng luồng nền (threading.Thread) và các callback bất đồng bộ để tương tác mượt mà với giao diện Tkinter.
# ==========================================


class MainController:
    # Khởi tạo MainController, kết nối View và Service
    def __init__(self, view):
        self.view = view
        self.service = FinanceService()
        logger.debug("Khởi tạo MainController kết nối với View và FinanceService.")
        
    # Thêm một giao dịch mới vào cơ sở dữ liệu
    def add_transaction(self, date: str, amount: float, category: str, t_type: str, note: str):
        logger.info(f"Controller nhận yêu cầu thêm giao dịch: date='{date}', amount={amount}, category='{category}', type='{t_type}'")
        db_date = self._parse_date(date)
        if not db_date: 
            logger.warning("Thêm giao dịch thất bại: Định dạng ngày tháng không hợp lệ.")
            return
            
        try:
            self.service.add_transaction(db_date, amount, category, t_type, note)
            self.view.show_message("Thành công", "Đã thêm giao dịch thành công!")
            self.refresh_dashboard()
            self.refresh_history()
            
            # Auto-check alerts sau khi thêm giao dịch chi tiêu
            if t_type == "Chi tiêu":
                from datetime import datetime
                month = datetime.strptime(db_date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m")
                logger.debug(f"Tự động kiểm tra cảnh báo hạn mức tháng {month} cho nhóm '{category}'")
                alerts = self.service.check_alerts(month, category=category)
                for a in alerts:
                    if a['pct'] >= 100:
                        logger.warning(f"Cảnh báo vượt hạn: {category} đã dùng {a['pct']:.1f}% hạn mức!")
                        self.view.show_error("⚠ Vượt hạn", f"🔴 {category}: đã dùng {a['pct']:.1f}% hạn mức!")
                    elif a['pct'] >= 80:
                        logger.info(f"Cảnh báo sắp vượt hạn: {category} đã dùng {a['pct']:.1f}% hạn mức.")
                        self.view.show_message("⚠ Sắp vượt", f"🟡 {category}: đã dùng {a['pct']:.1f}% — còn {a['remaining']:,.0f} ₫")
        except Exception as e:
            logger.error(f"Không thể thêm giao dịch: {str(e)}", exc_info=True)
            self.view.show_error("Lỗi", f"Không thể thêm giao dịch: {str(e)}")

    # Cập nhật thông tin của một giao dịch đã tồn tại
    def update_transaction(self, t_id: int, date: str, amount: float, category: str, t_type: str, note: str):
        logger.info(f"Controller nhận yêu cầu sửa giao dịch: date='{date}', amount={amount}, category='{category}', type='{t_type}'")
        db_date = self._parse_date(date)
        if not db_date:
            logger.warning(f"Sửa giao dịch thất bại: Định dạng ngày tháng không hợp lệ.")
            return
        
        try:
            self.service.update_transaction(t_id, db_date, amount, category, t_type, note)
            self.view.show_message("Thành công", "Cập nhật thành công!")
            self.refresh_dashboard()
            self.refresh_history()
        except Exception as e:
            logger.error(f"Lỗi cập nhật giao dịch: {str(e)}", exc_info=True)
            self.view.show_error("Lỗi", f"Lỗi cập nhật: {str(e)}")
            
    # Xóa nhiều giao dịch theo danh sách
    def delete_transactions(self, ids: list):
        logger.info(f"Controller nhận yêu cầu xóa các giao dịch")
        if not ids: 
            logger.warning("Yêu cầu xóa giao dịch bị bỏ qua vì danh sách chọn rỗng.")
            return
        try:
            self.service.delete_transactions(ids)
            self.view.show_message("Thành công", "Xóa thành công!")
            self.refresh_dashboard()
            self.refresh_history()
        except Exception as e:
            logger.error(f"Lỗi khi xóa các giao dịch {ids}: {str(e)}", exc_info=True)
            self.view.show_error("Lỗi", f"Không thể xóa: {str(e)}")
            
    # Nhập dữ liệu giao dịch từ file CSV (chạy nền)
    def import_csv(self, filepath: str):
        logger.info(f"Controller nhận yêu cầu nhập CSV từ: {filepath}")
        self.view.show_loading("Đang nhập dữ liệu...")
        def task():
            try:
                self.service.import_from_csv(filepath)
                self.view.after(0, lambda: self._on_import_success())
            except Exception as e:
                logger.error(f"Lỗi chạy nền nhập dữ liệu CSV: {str(e)}", exc_info=True)
                self.view.after(0, lambda err=e: self._on_import_error(err))
        threading.Thread(target=task, daemon=True).start()

    # Xử lý khi nhập dữ liệu CSV thành công
    def _on_import_success(self):
        logger.info("Nhập dữ liệu CSV thành công từ background thread.")
        self.view.hide_loading()
        self.view.show_message("Thành công", "Nhập dữ liệu thành công!")
        self.refresh_dashboard()
        self.refresh_history()

    # Xử lý khi nhập dữ liệu CSV thất bại
    def _on_import_error(self, e):
        logger.error(f"Lỗi nhập dữ liệu CSV trả về View: {str(e)}")
        self.view.hide_loading()
        self.view.show_error("Lỗi", f"Lỗi nhập dữ liệu: {str(e)}")

    # Xuất dữ liệu giao dịch ra file CSV (chạy nền)
    def export_csv(self, filepath: str):
        logger.info(f"Controller nhận yêu cầu xuất dữ liệu ra file CSV: {filepath}")
        self.view.show_loading("Đang xuất dữ liệu...")
        def task():
            try:
                self.service.export_to_csv(filepath)
                self.view.after(0, lambda: self._on_export_success())
            except Exception as e:
                logger.error(f"Lỗi chạy nền xuất dữ liệu CSV: {str(e)}", exc_info=True)
                self.view.after(0, lambda err=e: self._on_export_error(err))
        threading.Thread(target=task, daemon=True).start()

    # Xử lý khi xuất dữ liệu CSV thành công
    def _on_export_success(self):
        logger.info("Xuất dữ liệu CSV thành công từ background thread.")
        self.view.hide_loading()
        self.view.show_message("Thành công", "Xuất dữ liệu thành công!")

    # Xử lý khi xuất dữ liệu CSV thất bại
    def _on_export_error(self, e):
        logger.error(f"Lỗi xuất dữ liệu CSV trả về View: {str(e)}")
        self.view.hide_loading()
        self.view.show_error("Lỗi", f"Lỗi xuất dữ liệu: {str(e)}")

    # Xuất các giao dịch được chọn ra file CSV (chạy nền)
    def export_selected_csv(self, filepath: str, selected_ids: list):
        logger.info(f"Controller nhận yêu cầu xuất {len(selected_ids)} giao dịch được chọn ra: {filepath}")
        if not selected_ids:
            logger.warning("Danh sách giao dịch được chọn rỗng, bỏ qua xuất file.")
            return
        self.view.show_loading("Đang xuất dữ liệu đã chọn...")
        def task():
            try:
                self.service.export_selected_to_csv(filepath, selected_ids)
                self.view.after(0, lambda: self._on_export_success())
            except Exception as e:
                logger.error(f"Lỗi chạy nền xuất dữ liệu CSV được chọn: {str(e)}", exc_info=True)
                self.view.after(0, lambda err=e: self._on_export_error(err))
        threading.Thread(target=task, daemon=True).start()

    # Tìm kiếm giao dịch theo từ khóa
    def search_transactions(self, keyword: str):
        logger.info(f"Controller gọi tìm kiếm giao dịch với từ khóa: '{keyword}'")
        try:
            transactions = self.service.get_recent_transactions(keyword=keyword)
            self.view.update_history(transactions)
        except Exception as e:
            logger.error(f"Lỗi tìm kiếm giao dịch với từ khóa '{keyword}': {str(e)}", exc_info=True)
            self.view.show_error("Lỗi", f"Lỗi tìm kiếm: {str(e)}")

    # Sắp xếp danh sách giao dịch
    def sort_transactions(self, sort_by: str):
        logger.info(f"Controller nhận yêu cầu sắp xếp giao dịch theo: '{sort_by}'")
        try:
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
            logger.info(f"Sắp xếp hoàn tất theo '{sort_by}'.")
        except Exception as e:
            logger.error(f"Lỗi sắp xếp giao dịch: {str(e)}", exc_info=True)
            self.view.show_error("Lỗi", f"Lỗi sắp xếp: {str(e)}")

    # Chuyển đổi định dạng ngày tháng từ chuỗi (DD/MM/YYYY HH:MM) sang dạng chuẩn cho Database
    def _parse_date(self, date: str):
        logger.debug(f"Đang phân tích ngày giờ từ chuỗi: '{date}'")
        from datetime import datetime
        try:
            parsed_date = datetime.strptime(date, "%d/%m/%Y %H:%M")
            res = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
            logger.debug(f"Phân tích thành công ngày giờ: '{date}' -> '{res}'")
            return res
        except ValueError:
            logger.error(f"Ngày giờ nhập vào không đúng định dạng DD/MM/YYYY HH:MM: '{date}'")
            self.view.show_error("Lỗi", "Ngày giờ không đúng định dạng DD/MM/YYYY HH:MM.")
            return None
            
    # Làm mới dữ liệu biểu đồ trên Dashboard (chạy nền)
    def refresh_dashboard(self):
        if hasattr(self.view, 'dashboard_window') and self.view.dashboard_window and self.view.dashboard_window.winfo_exists():
            logger.info("Yêu cầu cập nhật biểu đồ Dashboard hệ thống.")
            self.view.show_loading("Đang tải biểu đồ...")
            def task():
                try:
                    category_data = self.service.get_expenses_by_category()
                    trend_data = self.service.get_spending_trend()
                    self.view.after(0, lambda: self._on_dashboard_success(category_data, trend_data))
                except Exception as e:
                    logger.error(f"Lỗi chạy nền tải dữ liệu biểu đồ Dashboard: {str(e)}", exc_info=True)
                    self.view.after(0, lambda err=e: self._on_dashboard_error(err))
            threading.Thread(target=task, daemon=True).start()

    # Xử lý khi tải dữ liệu biểu đồ Dashboard thành công
    def _on_dashboard_success(self, category_data, trend_data):
        logger.info("Tải dữ liệu biểu đồ Dashboard thành công.")
        self.view.hide_loading()
        if hasattr(self.view, 'dashboard_window') and self.view.dashboard_window and self.view.dashboard_window.winfo_exists():
            self.view.update_charts(category_data, trend_data)
            
    # Xử lý khi tải dữ liệu biểu đồ Dashboard thất bại
    def _on_dashboard_error(self, e):
        logger.error(f"Lỗi tải biểu đồ Dashboard: {str(e)}")
        self.view.hide_loading()
        self.view.show_error("Lỗi", f"Lỗi tải biểu đồ: {str(e)}")
        
    # Làm mới danh sách lịch sử giao dịch
    def refresh_history(self):
        logger.debug("Yêu cầu refresh danh sách lịch sử giao dịch hiển thị.")
        try:
            transactions = self.service.get_recent_transactions()
            self.view.update_history(transactions)
        except Exception as e:
            logger.error(f"Lỗi refresh danh sách lịch sử: {str(e)}", exc_info=True)

    # Tải dữ liệu ban đầu khi khởi động ứng dụng
    def load_initial_data(self):
        logger.info("Bắt đầu nạp dữ liệu ban đầu khi khởi động ứng dụng...")
        try:
            self.refresh_history()
            logger.info("Nạp dữ liệu ban đầu hoàn tất.")
        except Exception as e:
            logger.error(f"Lỗi nạp dữ liệu ban đầu: {str(e)}", exc_info=True)

    # Lấy danh sách tất cả các danh mục
    def get_categories(self):
        logger.debug("Gọi get_categories() từ View.")
        try:
            return self.service.get_categories()
        except Exception as e:
            logger.error(f"Lỗi lấy danh mục từ controller: {str(e)}", exc_info=True)
            return []

    # Thêm một danh mục mới
    def add_category(self, name):
        logger.info(f"Yêu cầu thêm danh mục: '{name}'")
        if not name.strip(): 
            logger.warning("Bỏ qua thêm danh mục vì chuỗi rỗng.")
            return
        try:
            self.service.add_category(name.strip())
        except Exception as e:
            logger.error(f"Lỗi thêm danh mục '{name}': {str(e)}", exc_info=True)

    # Cập nhật tên của một danh mục
    def update_category(self, old_name, new_name):
        logger.info(f"Yêu cầu cập nhật danh mục: '{old_name}' -> '{new_name}'")
        if not new_name.strip(): 
            logger.warning("Bỏ qua cập nhật danh mục vì tên mới rỗng.")
            return
        try:
            self.service.update_category_name(old_name, new_name.strip())
            self.refresh_history()
        except Exception as e:
            logger.error(f"Lỗi cập nhật danh mục từ '{old_name}' thành '{new_name}': {str(e)}", exc_info=True)

    # Xóa một danh mục
    def delete_category(self, name):
        logger.info(f"Yêu cầu xóa danh mục: '{name}'")
        try:
            self.service.delete_category(name)
        except Exception as e:
            logger.error(f"Lỗi xóa danh mục '{name}': {str(e)}", exc_info=True)

    # ─── BUDGET MANAGEMENT ────────────────────────────────────────────────────

    def set_budget(self, category: str, month: str, limit_amount: float, overwrite: bool = False) -> dict:
        logger.info(f"Đặt hạn mức ngân sách: category='{category}', month='{month}', amount={limit_amount}")
        try:
            return self.service.set_budget(category, month, limit_amount, overwrite)
        except Exception as e:
            logger.error(f"Lỗi khi đặt ngân sách từ Controller: {str(e)}", exc_info=True)
            raise

    def delete_budget(self, category: str, month: str):
        logger.info(f"Xóa hạn mức ngân sách: category='{category}', month='{month}'")
        try:
            self.service.delete_budget(category, month)
        except Exception as e:
            logger.error(f"Lỗi khi xóa ngân sách từ Controller: {str(e)}", exc_info=True)
            raise

    def get_all_budgets(self, month: str) -> list:
        logger.debug(f"Lấy danh sách ngân sách tháng {month}")
        try:
            return self.service.get_all_budgets(month)
        except Exception as e:
            logger.error(f"Lỗi get_all_budgets từ Controller: {str(e)}", exc_info=True)
            return []

    def get_budget_history(self, category: str) -> list:
        logger.debug(f"Lấy lịch sử ngân sách nhóm '{category}'")
        try:
            return self.service.get_budget_history(category)
        except Exception as e:
            logger.error(f"Lỗi get_budget_history từ Controller: {str(e)}", exc_info=True)
            return []

    def copy_budget_from_last_month(self, target_month: str) -> int:
        logger.info(f"Copy ngân sách sang tháng {target_month}")
        try:
            return self.service.copy_budget_from_last_month(target_month)
        except Exception as e:
            logger.error(f"Lỗi copy ngân sách từ Controller: {str(e)}", exc_info=True)
            return 0

    # ─── USAGE & ALERTS ───────────────────────────────────────────────────────

    def get_usage(self, month: str) -> list:
        logger.debug(f"Lấy bảng ngân sách sử dụng tháng {month}")
        try:
            return self.service.get_usage(month)
        except Exception as e:
            logger.error(f"Lỗi get_usage từ Controller: {str(e)}", exc_info=True)
            return []

    def check_alerts(self, month: str, category: str = None) -> list:
        logger.debug(f"Kiểm tra cảnh báo hạn mức: month='{month}', category={category}")
        try:
            return self.service.check_alerts(month, category)
        except Exception as e:
            logger.error(f"Lỗi check_alerts từ Controller: {str(e)}", exc_info=True)
            return []

    # ─── SAVINGS GOALS ────────────────────────────────────────────────────────

    def set_savings_goal(self, month: str, goal_amount: float):
        logger.info(f"Đặt mục tiêu tiết kiệm: month='{month}', amount={goal_amount}")
        try:
            self.service.set_savings_goal(month, goal_amount)
        except Exception as e:
            logger.error(f"Lỗi set_savings_goal từ Controller: {str(e)}", exc_info=True)
            raise

    def get_savings_progress(self, month: str) -> dict:
        logger.debug(f"Lấy tiến độ tiết kiệm tháng {month}")
        try:
            return self.service.get_savings_progress(month)
        except Exception as e:
            logger.error(f"Lỗi get_savings_progress từ Controller: {str(e)}", exc_info=True)
            return {}

    def get_savings_goal(self, month: str) -> float:
        logger.debug(f"Lấy hạn mức mục tiêu tiết kiệm tháng {month}")
        try:
            return self.service.get_savings_goal(month)
        except Exception as e:
            logger.error(f"Lỗi get_savings_goal từ Controller: {str(e)}", exc_info=True)
            return 0.0



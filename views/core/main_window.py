# Nhập các thư viện hệ thống và giao diện chuẩn
import os
import datetime
import tkinter as tk
from tkinter import filedialog
import tkinter.messagebox as mb
from PIL import Image, ImageTk
import customtkinter as ctk

# Nhập các hằng số cấu hình kiểu dáng dùng chung
from views.core.theme_styles import *

# Nhập các thành phần giao diện mô đun hóa và hộp thoại con
from views.common.summary_card import SummaryCard
from views.transactions.transaction_table import TransactionTable
from views.core.header_view import HeaderView
from views.common.toast_notification import ToastNotification
from views.transactions.time_filter_dropdown import ViewByDropdown
from views.common.loading_dialog import LoadingDialog
from views.dashboard.dashboard_window import DashboardWindow
from views.transactions.transaction_dialog import TransactionWindow
from views.transactions.filter_dialog import FilterWindow
from views.categories.category_manager_dialog import CategoryManagerWindow

# Nhập tiện ích ghi nhật ký log hệ thống
from views.core.ui_decorators import safe_execution
from utils.logger import logger

# ==========================================
# Tên file: main_window.py (nằm trong thư mục views)
# Danh sách lớp và chức năng OOP:
# Lớp: MainWindow
# - Chức năng: Cửa sổ điều phối trung tâm của Giao diện (View chính) kế thừa ctk.CTk, chịu trách nhiệm khởi dựng bố cục ứng dụng, tải tài nguyên icons, lưu trữ trạng thái tìm kiếm/lọc/phân trang giao dịch, quản lý vòng đời và tương tác của các cửa sổ con phụ trợ.
# Khái niệm OOP sử dụng:
# - Tính kế thừa (Inheritance): MainWindow kế thừa trực tiếp lớp ctk.CTk để đóng vai trò là cửa sổ ứng dụng gốc điều phối toàn hệ thống.
# - Quan hệ chứa trong / Tích hợp đối tượng (Composition / Aggregation): Tích hợp trực tiếp các widget chuyên biệt (HeaderView, SummaryCard, TransactionTable, v.v.) làm các thành phần con cấu thành nên giao diện tổng thể.
# - Tính đóng gói trạng thái (State Encapsulation): Đóng gói toàn bộ thông tin cấu hình bộ lọc nâng cao, từ khóa tìm kiếm, phân trang và danh sách dòng đang được chọn (self.selected_row_ids) để quản lý tương tác đồng bộ.
# - Giao tiếp đối tượng (Object Collaboration & Dependency Injection): Nhận đối tượng MainController qua phương thức set_controller để chuyển giao các sự kiện nghiệp vụ người dùng, đồng thời đóng vai trò làm master điều khiển hiển thị cho tất cả các hộp thoại con CTkToplevel.
# ==========================================


# Khai báo lớp MainWindow điều phối toàn bộ luồng hoạt động giao diện của ứng dụng
class MainWindow(ctk.CTk):
    # Khởi tạo cửa sổ chính điều phối
    def __init__(self):
        """
        Cửa sổ điều phối chính của ứng dụng. Khởi tạo trạng thái, giao diện và các phím tắt.
        """
        super().__init__()
        
        self.title("Quản Lý Chi Tiêu Cá Nhân")
        self.geometry("1200x700")
        self.configure(fg_color=BG_COLOR)
        ctk.set_appearance_mode("dark")
        
        # Thuộc tính quản lý cửa sổ con
        self.controller = None
        self.dashboard_window = None
        self.help_window = None
        self.loading_window = None
        self.calendar_window = None
        self.transaction_window = None
        self.category_window = None
        self.filter_window = None
        
        # Biến lưu trữ trạng thái giao dịch và phân trang
        self.transactions = []
        self.filtered_transactions = []
        self.current_page = 1
        self.rows_per_page = 15
        
        self.selected_row_ids = set()
        self.select_all_var = tk.BooleanVar(value=False)
        self.sort_by = "Thời gian"
        self.sort_order = "desc"
        
        # Tiêu chí lọc giao dịch nâng cao
        self.filter_categories = []
        self.filter_type = "Tất cả"
        self.filter_min_amt = ""
        self.filter_max_amt = ""
        
        # Mặc định bộ lọc thời gian ban đầu là Tất cả
        self.filter_min_date = ""
        self.filter_max_date = ""
        self.active_time_preset = "Tất cả"
        self.view_by_dropdown = None
        
        self.search_query = ""  # Từ khóa tìm kiếm phi thời gian thực
        
        # Tải tài nguyên hình ảnh biểu tượng và xây dựng giao diện
        self.load_icons()
        self.setup_ui()
        self.bind_shortcuts()
        
        logger.info("MainWindow initialized and UI components rendered.")

    # Tải các biểu tượng icon từ thư mục assets phục vụ hiển thị
    def load_icons(self):
        """Tải các biểu tượng icon từ thư mục assets."""
        icon_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "icons")
        self.icons = {}
        self.menu_icons = {}
        icon_names = [
            'import', 'export', 'stats', 'help', 'edit', 'delete', 'add', 'search', 'tx', 'exp', 'inc', 
            'net', 'success', 'error', 'money', 'empty', 'copy', 'calendar', 'budget', 'alert', 'savings', 
            'safe', 'danger', 'warning', 'sort', 'sort_up', 'sort_down', 'left', 'right', 'app_logo', 
            'nav_budget', 'dialog_budget', 'filter'
        ]
        for name in icon_names:
            path = os.path.join(icon_dir, f"{name}.png")
            if os.path.exists(path):
                img = Image.open(path)
                self.icons[name] = ctk.CTkImage(light_image=img, dark_image=img, size=(20, 20))
                
                size = CONTEXT_MENU_ICON_SIZE
                pad = CONTEXT_MENU_ICON_PADX
                new_width = size + pad
                new_img = Image.new("RGBA", (new_width, size), (255, 255, 255, 0))
                resized = img.resize((size, size))
                new_img.paste(resized, (pad, 0))
                self.menu_icons[name] = ImageTk.PhotoImage(new_img)

    # Thiết lập bộ điều khiển controller kết nối dữ liệu giữa view và database
    def set_controller(self, controller):
        """Thiết lập controller kết nối với view và nạp dữ liệu ban đầu."""
        self.controller = controller
        self.controller.load_initial_data()

    # Khởi tạo cấu trúc lưới bố cục và kết xuất toàn bộ khu vực chính trên UI
    def setup_ui(self):
        """Khởi tạo và bố trí toàn bộ các thành phần giao diện chính."""
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.setup_topbar() # Khởi tạo thanh tiêu đề trên cùng (Header)
        self.setup_summary_strip() # Khởi tạo dải thẻ tóm tắt tổng quan
        self.setup_action_bar() # Khởi tạo thanh thao tác phụ với nút thêm giao dịch và bộ lọc
        self.setup_main_table() # Khởi tạo bảng hiển thị danh sách giao dịch chính
        self.setup_bottom_bar() # Khởi tạo thanh trạng thái chân trang với thao tác hàng loạt và phân trang

    # Tập trung tiêu điểm con trỏ vào cửa sổ nếu cửa sổ đó đang mở
    def _focus_if_exists(self, window_attr):
        """Kiểm tra xem cửa sổ đã tồn tại chưa, nếu có thì focus và trả về True."""
        win = getattr(self, window_attr, None)
        if win and win.winfo_exists():
            win.focus()
            return True
        return False

    # Lấy danh sách toàn bộ danh mục chi tiêu hiện tại
    def _get_categories(self):
        """Lấy danh sách danh mục một cách an toàn."""
        return self.controller.get_categories() if self.controller else []

    # Hàm tiện ích hỗ trợ tạo nhanh và căn giữa các cửa sổ popup phụ
    def create_toplevel_window(self, title, width, height, grab=True):
        """Hàm hỗ trợ tạo và cấu hình một cửa sổ con (Toplevel)."""
        win = ctk.CTkToplevel(self)
        win.title(title)
        win.geometry(f"{width}x{height}")
        win.transient(self)
        if grab:
            win.grab_set()
        win.configure(fg_color=PANEL_BG)
        
        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (width // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (height // 2)
        win.geometry(f"+{x}+{y}")
        return win

    # Khởi tạo thanh tiêu đề trên cùng (Header) chứa tìm kiếm, CSV và trợ giúp
    def setup_topbar(self):
        """Premium Header section containing logo, search bar, and utility action buttons."""
        self.header = HeaderView(
            self, self.icons,
            search_cb=self.perform_search,
            import_cb=self.on_import,
            export_cb=self.on_export,
            stats_cb=self.show_dashboard,
            help_cb=self.show_help
        )
        self.header.grid(row=0, column=0, sticky="ew")

    # Khởi tạo khu vực hiển thị các thẻ tóm tắt tài chính tổng quan
    def setup_summary_strip(self):
        """Metric Strip displaying summary cards (Total Tx, Total Exp, Total Inc, Balance)."""
        self.summary_strip = ctk.CTkFrame(self, height=64, fg_color="transparent")
        self.summary_strip.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        self.card_tx = SummaryCard(self.summary_strip, "TỔNG GIAO DỊCH", "0", self.icons.get('tx'))
        self.card_tx.pack(side="left", fill="x", expand=True, padx=5)
        
        self.card_exp = SummaryCard(self.summary_strip, "TỔNG CHI TIÊU", "0", self.icons.get('exp'), ACCENT_RED)
        self.card_exp.pack(side="left", fill="x", expand=True, padx=5)
        
        self.card_inc = SummaryCard(self.summary_strip, "TỔNG THU NHẬP", "0", self.icons.get('inc'), ACCENT_GREEN)
        self.card_inc.pack(side="left", fill="x", expand=True, padx=5)
        
        self.card_net = SummaryCard(self.summary_strip, "SỐ DƯ", "0", self.icons.get('net'), ACCENT_BLUE)
        self.card_net.pack(side="left", fill="x", expand=True, padx=5)

    # Khởi tạo thanh thao tác phụ gồm nút thêm giao dịch và nút kích hoạt bộ lọc
    def setup_action_bar(self):
        """Action Bar containing primary CRUD triggers (Add Transaction, Filters)."""
        self.action_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.action_bar.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        btn_add = ctk.CTkButton(
            self.action_bar, text=" Thêm giao dịch", image=self.icons.get('add'), 
            fg_color=PANEL_BG, hover_color=PANEL_BG_HOVER, font=FONT_BUTTON, 
            corner_radius=16, height=36, border_width=1, border_color=BORDER_COLOR, 
            command=self.open_transaction_window
        )
        btn_add.pack(side="left")
        
        btn_filter = ctk.CTkButton(
            self.action_bar, text=" Lọc", image=self.icons.get('filter'), 
            fg_color=PANEL_BG, hover_color=PANEL_BG_HOVER, font=FONT_BUTTON, 
            corner_radius=16, height=36, width=90, border_width=1, border_color=BORDER_COLOR, 
            command=self.open_filter_window
        )
        btn_filter.pack(side="left", padx=(10, 0))
        
        # Nút lọc thời gian nhanh "Xem theo"
        self.btn_view_by = ctk.CTkButton(
            self.action_bar, text="Xem theo: Tất cả", image=self.icons.get('calendar'), 
            fg_color=PANEL_BG, hover_color=PANEL_BG_HOVER, font=FONT_BUTTON, 
            corner_radius=16, height=36, border_width=1, border_color=BORDER_COLOR, 
            command=self.toggle_view_by_dropdown
        )
        self.btn_view_by.pack(side="left", padx=(10, 0))

    # Khởi tạo bảng danh sách giao dịch chính cùng các nút sắp xếp, chỉnh sửa
    def setup_main_table(self):
        """Table display and list controller."""
        self.table = TransactionTable(
            self, self.icons, self.select_all_var,
            toggle_select_all_cb=self.toggle_select_all,
            toggle_row_selection_cb=self.toggle_row_selection,
            sort_cb=self.sort_by_column,
            edit_cb=self.open_transaction_window,
            delete_cb=self.delete_single_transaction,
            context_menu_cb=self.show_context_menu
        )
        self.table.grid(row=3, column=0, sticky="nsew", padx=20, pady=0)

    # Khởi tạo thanh trạng thái chân trang quản lý xóa/xuất hàng loạt và phân trang
    def setup_bottom_bar(self):
        """Bottom bar housing bulk selection operators and pagination buttons."""
        self.bottom_bar = ctk.CTkFrame(self, height=48, fg_color=PANEL_BG, corner_radius=10)
        self.bottom_bar.grid(row=4, column=0, sticky="ew", padx=20, pady=(5, 10))
        self.bottom_bar.grid_columnconfigure(0, weight=1)
        self.bottom_bar.grid_rowconfigure(0, weight=1)
        self.bottom_bar.grid_propagate(False)
        
        # Bố cục khu vực thao tác hàng loạt
        self.bulk_frame = ctk.CTkFrame(self.bottom_bar, fg_color="transparent")
        self.bulk_frame.grid(row=0, column=0, sticky="w", padx=10, pady=6)
        
        for text, icon, color, cmd in [
            (" Xoá đã chọn", 'delete', ACCENT_RED, self.on_delete_selected), 
            (" Xuất đã chọn", 'export', PANEL_BG_HOVER, self.on_export_selected)
        ]:
            ctk.CTkButton(
                self.bulk_frame, text=text, image=self.icons.get(icon), fg_color=color, 
                width=130, height=28, command=cmd
            ).pack(side="left", padx=4)
        self.bulk_frame.grid_remove()
        
        right_frame = ctk.CTkFrame(self.bottom_bar, fg_color="transparent")
        right_frame.grid(row=0, column=1, padx=10, pady=4, sticky="e")
        
        # Khung phân trang chính
        self.pagination_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        self.pagination_frame.pack(side="left", padx=5)

    # Đăng ký các phím tắt hệ thống trên bàn phím phục vụ thao tác nhanh
    def bind_shortcuts(self):
        """Đăng ký các phím tắt cho ứng dụng (Ctrl+N, Ctrl+F, Delete) và sự kiện click ra ngoài."""
        self.bind("<Control-n>", lambda e: self.open_transaction_window())
        self.bind("<Control-f>", lambda e: self.header.focus_search())
        self.bind("<Delete>", lambda e: self.on_delete_selected())
        self.bind("<Button-1>", self.unfocus_search)

    # Chọn hoặc bỏ chọn tất cả các dòng giao dịch hiện thị trên bảng
    @safe_execution("Lỗi chọn tất cả")
    def toggle_select_all(self):
        """Chọn hoặc bỏ chọn tất cả các giao dịch đang hiển thị."""
        is_selected = self.select_all_var.get()
        if is_selected:
            for t in self.filtered_transactions:
                self.selected_row_ids.add(t['id'])
        else:
            self.selected_row_ids.clear()
        self.update_bulk_actions_visibility()
        self.render_table_page()

    # Thực hiện thay đổi chiều sắp xếp dữ liệu theo cột chỉ định
    @safe_execution("Lỗi sắp xếp dữ liệu")
    def sort_by_column(self, col_name):
        """Sắp xếp dữ liệu theo cột được chọn."""
        if self.sort_by == col_name:
            if self.sort_order == "desc":
                self.sort_order = "asc"
            else:
                self.sort_by = None
                self.sort_order = None
        else:
            self.sort_by = col_name
            self.sort_order = "desc"
        
        self.table.update_header_arrows(self.sort_by, self.sort_order)
        self.apply_filters()

    # Đọc từ khóa ô tìm kiếm và yêu cầu áp dụng bộ lọc dữ liệu
    @safe_execution("Lỗi thực hiện tìm kiếm")
    def perform_search(self):
        """Thực hiện tìm kiếm khi người dùng bấm nút Tìm kiếm hoặc nhấn Enter."""
        self.search_query = self.header.get_search_text()
        logger.info(f"Người dùng xác nhận tìm kiếm với từ khóa: '{self.search_query}'")
        self.apply_filters()

    # Áp dụng bộ lọc tìm kiếm ngầm bằng đa luồng (threading) tránh đơ ứng dụng
    def apply_filters(self):
        """Lọc danh sách giao dịch sử dụng Threading để tránh đơ giao diện khi tập dữ liệu lớn."""
        logger.info("Bắt đầu thực hiện tìm kiếm / lọc giao dịch...")
        
        # Đồng bộ hóa text trên nút công cụ "Xem theo"
        self.update_view_by_button_text()
        
        # 1. Trích xuất các tiêu chí lọc từ GUI trên main thread trước khi chuyển sang thread phụ
        try:
            kw = self.search_query.lower().strip()
        except Exception:
            kw = ""
            
        filter_categories = list(self.filter_categories)
        filter_type = self.filter_type
        filter_min_amt = self.filter_min_amt
        filter_max_amt = self.filter_max_amt
        filter_min_date = self.filter_min_date
        filter_max_date = self.filter_max_date
        transactions_copy = list(self.transactions)
        sort_by = self.sort_by
        sort_order = self.sort_order
        
        # 2. Hiển thị trạng thái chờ (loading indicator) trên main thread
        self.show_loading("Đang tìm kiếm...", show_dialog=False)
        
        # 3. Định nghĩa tác vụ chạy nền
        def task():
            import threading
            import time
            try:
                logger.debug(f"Đang chạy thread lọc dữ liệu ngầm. Từ khóa: '{kw}', Loại: '{filter_type}', Số lượng thô: {len(transactions_copy)}")
                res = []
                for t in transactions_copy:
                    # Kiểm tra từ khóa tìm kiếm
                    if kw:
                        val_str = (str(t.get('note', '')).lower() + " " + 
                                   str(t.get('category', '')).lower() + " " + 
                                   str(t.get('amount', '')))
                        if kw not in val_str:
                            continue
                            
                    # Kiểm tra danh mục
                    if filter_categories and t.get('category') not in filter_categories:
                         continue
                         
                    # Kiểm tra loại
                    if filter_type != "Tất cả" and t.get('type') != filter_type:
                         continue
                         
                    # Kiểm tra khoảng số tiền
                    try:
                        amt = float(t.get('amount', 0))
                        if filter_min_amt:
                            if amt < float(filter_min_amt.replace(',', '')):
                                continue
                        if filter_max_amt:
                            if amt > float(filter_max_amt.replace(',', '')):
                                continue
                    except ValueError:
                        pass
                        
                    # Kiểm tra khoảng thời gian
                    try:
                        dt_str = str(t.get('date', ''))
                        fmt = "%d/%m/%Y %H:%M" if ":" in dt_str else "%d/%m/%Y"
                        dt = datetime.datetime.strptime(dt_str, fmt)
                        if filter_min_date:
                            min_dt = datetime.datetime.strptime(filter_min_date, "%d/%m/%Y")
                            if dt.date() < min_dt.date():
                                continue
                        if filter_max_date:
                            max_dt = datetime.datetime.strptime(filter_max_date, "%d/%m/%Y")
                            if dt.date() > max_dt.date():
                                continue
                    except ValueError:
                        pass
                        
                    res.append(t)
                
                # Áp dụng sắp xếp trong background
                if res and sort_by:
                    logger.debug(f"Đang sắp xếp ngầm danh sách đã lọc theo: '{sort_by}' ({sort_order})")
                    if sort_by == "Thời gian":
                        def get_date(item):
                            try:
                                return datetime.datetime.strptime(item['date'], "%d/%m/%Y %H:%M")
                            except ValueError:
                                try:
                                    return datetime.datetime.strptime(item['date'], "%d/%m/%Y")
                                except ValueError:
                                    return datetime.datetime.min
                        res.sort(key=get_date, reverse=(sort_order == "desc"))
                    elif sort_by == "Số tiền":
                        res.sort(key=lambda item: float(item['amount']), reverse=(sort_order == "desc"))
                
                # Thêm mô phỏng trễ cực ngắn 0.35 giây để bộ chỉ báo chờ mượt mà
                time.sleep(0.35)
                
                logger.debug(f"Thread lọc ngầm hoàn tất thành công. Số kết quả: {len(res)}")
                # Trả kết quả về main thread an toàn
                self.after(0, lambda: self._on_filter_success(res))
            except Exception as ex:
                logger.error(f"Lỗi trong quá trình chạy thread lọc: {str(ex)}", exc_info=True)
                self.after(0, lambda err=ex: self._on_filter_error(err))
                
        import threading
        threading.Thread(target=task, daemon=True).start()

    # Phản hồi lên giao diện chính sau khi luồng ngầm thực hiện lọc dữ liệu thành công
    def _on_filter_success(self, res):
        """Callback trên main thread khi lọc dữ liệu thành công."""
        self.filtered_transactions = res
        self.current_page = 1
        self.hide_loading()
        self.update_summary_cards()
        logger.info(f"Đã cập nhật kết quả lọc lên giao diện. Tìm thấy {len(res)} bản ghi.")

    # Hiển thị thông báo Toast lỗi nếu tiến trình lọc ngầm phát sinh ngoại lệ
    def _on_filter_error(self, err):
        """Callback trên main thread khi lọc dữ liệu bị lỗi."""
        self.hide_loading()
        self.show_error("Lỗi tìm kiếm", f"Lỗi xảy ra khi tìm kiếm/lọc: {str(err)}")
        logger.error(f"Lỗi lọc dữ liệu trả về giao diện: {str(err)}")

    # Tính toán lại tổng thu nhập, chi tiêu, số dư và cập nhật lên thẻ hiển thị
    def update_summary_cards(self):
        """Cập nhật các thẻ tổng quan dựa trên danh sách giao dịch đang được hiển thị (đã lọc)."""
        txs = self.filtered_transactions
        total_tx = len(txs)
        total_inc = sum(float(t['amount']) for t in txs if t['type'] == TX_TYPE_INCOME_VN)
        total_exp = sum(float(t['amount']) for t in txs if t['type'] == TX_TYPE_EXPENSE_VN)
        net = total_inc - total_exp
        
        self.card_tx.configure_value(str(total_tx))
        self.card_exp.configure_value(f"{total_exp:,.0f} đ")
        self.card_inc.configure_value(f"{total_inc:,.0f} đ")
        self.card_net.configure_value(f"{net:,.0f} đ", text_color=ACCENT_GREEN if net >= 0 else ACCENT_RED)

    # Định dạng lại danh sách giao dịch gốc từ controller và kích hoạt lọc dữ liệu
    def update_history(self, transactions):
        """Cập nhật danh sách giao dịch mới nhất vào bộ nhớ và tính toán lại các thông số tổng quan."""
        formatted_txs = []
        for t in transactions:
            t_copy = dict(t)
            try:
                if len(t['date']) > 10:
                    dt = datetime.datetime.strptime(t['date'], "%Y-%m-%d %H:%M:%S")
                else:
                    dt = datetime.datetime.strptime(t['date'], "%Y-%m-%d")
                t_copy['date'] = dt.strftime("%d/%m/%Y %H:%M")
            except Exception:
                pass
            formatted_txs.append(t_copy)
            
        self.transactions = formatted_txs
        self.apply_filters()

    # Tính toán chỉ số phân trang và vẽ các hàng giao dịch lên giao diện bảng
    def render_table_page(self):
        """Hiển thị dữ liệu các giao dịch lên bảng theo trang hiện tại."""
        self.table.clear_table()
        
        if not self.filtered_transactions:
            self.select_all_var.set(False)
            self.table.show_empty_state()
            self.render_pagination(1)
            return
            
        if len(self.selected_row_ids) > 0 and len(self.selected_row_ids) == len(self.filtered_transactions):
            self.select_all_var.set(True)
            if hasattr(self.table, 'header_checkbox'): 
                self.table.header_checkbox.select()
        else:
            self.select_all_var.set(False)
            if hasattr(self.table, 'header_checkbox'): 
                self.table.header_checkbox.deselect()
            
        start_idx = (self.current_page - 1) * self.rows_per_page
        end_idx = start_idx + self.rows_per_page
        page_data = self.filtered_transactions[start_idx:end_idx]
        
        total_pages = max(1, (len(self.filtered_transactions) + self.rows_per_page - 1) // self.rows_per_page)
        self.render_pagination(total_pages)
        
        for idx, t in enumerate(page_data):
            self.table.add_row(t, start_idx + idx, t['id'] in self.selected_row_ids, self.toggle_row_selection)
            
        self.update_bulk_actions_visibility()

    # Đổi trạng thái chọn của dòng giao dịch khi người dùng click ô checkbox
    @safe_execution("Lỗi chọn hàng giao dịch")
    def toggle_row_selection(self, t_id, state, row_widget=None, chk_var=None):
        """Xử lý thao tác chọn/bỏ chọn một giao dịch bằng ô checkbox."""
        if state:
            self.selected_row_ids.add(t_id)
            if row_widget: row_widget.configure(fg_color="#1E3A8A")
            if chk_var: chk_var.set(True)
        else:
            self.selected_row_ids.discard(t_id)
            if row_widget: row_widget.configure(fg_color="transparent")
            if chk_var: chk_var.set(False)
            
        self.update_bulk_actions_visibility()
        
        # Cập nhật trạng thái ô checkbox 'Select All'
        if len(self.selected_row_ids) > 0 and len(self.selected_row_ids) == len(self.filtered_transactions):
            self.select_all_var.set(True)
            if hasattr(self.table, 'header_checkbox'): 
                self.table.header_checkbox.select()
        else:
            self.select_all_var.set(False)
            if hasattr(self.table, 'header_checkbox'): 
                self.table.header_checkbox.deselect()

    # Ẩn/hiển thị khung tác vụ hàng loạt dựa trên số dòng đang chọn
    def update_bulk_actions_visibility(self):
        """Hiển thị hoặc ẩn khung các nút thao tác hàng loạt tùy thuộc vào số lượng dòng được chọn."""
        if self.selected_row_ids:
            self.bulk_frame.grid()
        else:
            self.bulk_frame.grid_remove()

    # Điều hướng lùi lại một trang giao dịch
    def prev_page(self):
        """Chuyển về trang trước đó trong danh sách giao dịch."""
        if self.current_page > 1:
            self.current_page -= 1
            self.render_table_page()
            
    # Điều hướng tiến thêm một trang giao dịch
    def next_page(self):
        """Chuyển sang trang tiếp theo trong danh sách giao dịch."""
        total_pages = max(1, (len(self.filtered_transactions) + self.rows_per_page - 1) // self.rows_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self.render_table_page()

    # Khởi tạo dải nút số trang (1, 2, 3...) và chấm lửng phân trang
    def render_pagination(self, total_pages):
        """Hiển thị dãy nút phân trang."""
        for widget in self.pagination_frame.winfo_children():
            widget.destroy()
            
        if total_pages <= 1:
            return
            
        # Nút prev
        btn_prev = ctk.CTkButton(
            self.pagination_frame, text="", image=self.icons.get('left'), 
            width=28, height=28, fg_color="transparent", text_color=TEXT_MUTED, 
            hover_color=PANEL_BG_HOVER, command=self.prev_page
        )
        btn_prev.pack(side="left", padx=2)
        
        # Danh sách các trang cần hiển thị
        pages_to_show = []
        if total_pages <= 7:
            pages_to_show = list(range(1, total_pages + 1))
        else:
            if self.current_page <= 4:
                pages_to_show = [1, 2, 3, 4, 5, None, total_pages]
            elif self.current_page >= total_pages - 3:
                pages_to_show = [1, None, total_pages - 4, total_pages - 3, total_pages - 2, total_pages - 1, total_pages]
            else:
                pages_to_show = [1, None, self.current_page - 1, self.current_page, self.current_page + 1, None, total_pages]
                
        for p in pages_to_show:
            if p is None:
                ctk.CTkLabel(self.pagination_frame, text="...", font=("Consolas", 11), text_color=TEXT_MAIN).pack(side="left", padx=3)
            else:
                is_curr = (p == self.current_page)
                fg_col = "#3B82F6" if is_curr else "transparent"
                txt_col = "#FFFFFF" if is_curr else TEXT_MAIN
                hov_col = "#2563EB" if is_curr else PANEL_BG_HOVER
                ctk.CTkButton(
                    self.pagination_frame, text=str(p), width=30, height=30, corner_radius=6, 
                    fg_color=fg_col, text_color=txt_col, hover_color=hov_col, 
                    font=("Consolas", 12, "bold"), command=lambda page=p: self.go_to_page(page)
                ).pack(side="left", padx=2)
                
        # Nút next
        btn_next = ctk.CTkButton(
            self.pagination_frame, text="", image=self.icons.get('right'), 
            width=28, height=28, fg_color="transparent", text_color=TEXT_MUTED, 
            hover_color=PANEL_BG_HOVER, command=self.next_page
        )
        btn_next.pack(side="left", padx=2)

    # Nhảy trực tiếp đến số trang chỉ định trong phân trang
    def go_to_page(self, page):
        """Chuyển đến một trang cụ thể khi click vào nút số."""
        if self.current_page != page:
            self.current_page = page
            self.render_table_page()

    # Hiển thị menu chuột phải khi người dùng bấm chuột phải lên dòng giao dịch
    def show_context_menu(self, event, t):
        """Hiển thị menu ngữ cảnh (chuột phải) cho một dòng giao dịch."""
        menu = tk.Menu(self, tearoff=0, bg=PANEL_BG, fg=TEXT_MAIN, activebackground=ACCENT_BLUE, font=FONT_CONTEXT_MENU)
        menu.add_command(
            label=" Sửa".ljust(CONTEXT_MENU_WIDTH), image=self.menu_icons.get('edit'), compound="left", 
            command=lambda: self.open_transaction_window(edit_t=t)
        )
        menu.add_command(
            label=" Xóa".ljust(CONTEXT_MENU_WIDTH), image=self.menu_icons.get('delete'), compound="left", 
            command=lambda: self.delete_single_transaction(t)
        )
        menu.add_command(
            label=" Nhân bản".ljust(CONTEXT_MENU_WIDTH), image=self.menu_icons.get('copy'), compound="left", 
            command=lambda: self.duplicate_transaction(t)
        )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    # Thực hiện nhân bản sao chép thông tin một giao dịch sang dòng mới
    @safe_execution("Lỗi nhân bản giao dịch")
    def duplicate_transaction(self, t):
        """Tạo một bản sao của giao dịch đang chọn."""
        if not self.controller: return
        logger.info(f"Yêu cầu nhân bản giao dịch mã {t.get('id')}")
        self.controller.add_transaction(t['date'], float(t['amount']), t['category'], t['type'], t['note'] + " (Bản sao)")

    # Gửi yêu cầu xóa một giao dịch đơn lẻ sau khi người dùng xác nhận
    @safe_execution("Lỗi xóa giao dịch")
    def delete_single_transaction(self, t):
        """Xóa một giao dịch đơn lẻ sau khi xác nhận."""
        logger.info(f"Yêu cầu xóa giao dịch đơn lẻ mã {t.get('id')}")
        if mb.askyesno("Xác nhận", "Bạn muốn xoá giao dịch đã chọn không?", icon="warning", parent=self):
            self.controller.delete_transactions([t['id']])

    # Gửi yêu cầu xóa đồng thời nhiều dòng giao dịch đã chọn
    @safe_execution("Lỗi xóa giao dịch hàng loạt")
    def on_delete_selected(self):
        """Xóa nhiều giao dịch đã được chọn."""
        if not self.selected_row_ids: return
        logger.info(f"Yêu cầu xóa các giao dịch được chọn: {self.selected_row_ids}")
        if mb.askyesno("Xác nhận", f"Xóa {len(self.selected_row_ids)} giao dịch đã chọn?", icon="warning", parent=self):
            self.controller.delete_transactions(list(self.selected_row_ids))
            self.selected_row_ids.clear()

    # Xuất dữ liệu của các giao dịch đang được chọn ra file CSV
    @safe_execution("Lỗi xuất dữ liệu giao dịch")
    def on_export_selected(self):
        """Xuất dữ liệu của các giao dịch đã chọn ra file CSV."""
        if not self.selected_row_ids:
            self.show_message("Thông báo", "Vui lòng chọn ít nhất một giao dịch để xuất.")
            return
        logger.info(f"Yêu cầu xuất {len(self.selected_row_ids)} giao dịch đã chọn")
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Lưu file CSV giao dịch đã chọn"
        )
        if filepath:
            self.controller.export_selected_csv(filepath, list(self.selected_row_ids))

    # Hiển thị hộp thoại nâng cao tinh chỉnh các tiêu chí lọc
    @safe_execution("Lỗi mở bộ lọc")
    def open_filter_window(self):
        """Mở cửa sổ popup lọc giao dịch."""
        if self._focus_if_exists('filter_window'): return
        self.filter_window = FilterWindow(self, self.icons)

    # Hiển thị hộp thoại quản lý thêm/sửa/xóa danh mục chi tiêu
    @safe_execution("Lỗi mở danh mục")
    def open_category_manager(self):
        """Mở cửa sổ popup quản lý danh mục."""
        if self._focus_if_exists('category_window'): return
        self.category_window = CategoryManagerWindow(self, self.controller)

    # Hiển thị hộp thoại nhập thông tin chi tiết thêm hoặc sửa một giao dịch
    @safe_execution("Lỗi mở giao dịch")
    def open_transaction_window(self, edit_t=None):
        """Mở cửa sổ form giao dịch mới hoặc cập nhật giao dịch."""
        if self._focus_if_exists('transaction_window'): return
        self.transaction_window = TransactionWindow(self, self.controller, self.icons, edit_t=edit_t)

    # Hiển thị cửa sổ thống kê phân tích trực quan hóa biểu đồ
    @safe_execution("Lỗi mở biểu đồ")
    def show_dashboard(self):
        """Mở cửa sổ popup thống kê & biểu đồ."""
        if self._focus_if_exists('dashboard_window'):
            self.dashboard_window._switch_tab("stats")
            return
        self.dashboard_window = DashboardWindow(self, self.controller, initial_tab="stats")
        if self.controller:
            self.controller.refresh_dashboard()

    # Chuyển tiếp dữ liệu phân tích xuống cửa sổ thống kê biểu đồ hoạt động
    def update_charts(self, category_data, trend_data):
        """Cập nhật dữ liệu cho các biểu đồ trong bảng thống kê."""
        if self.dashboard_window and self.dashboard_window.winfo_exists():
            self.dashboard_window.update_charts(category_data, trend_data)

    # Hiển thị popup hướng dẫn sử dụng và kích hoạt mở tệp tài liệu PDF
    @safe_execution("Lỗi mở tài liệu hướng dẫn")
    def show_help(self):
        """Mở trực tiếp tệp tài liệu hướng dẫn sử dụng PDF."""
        pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'huong_dan_su_dung.pdf')
        try:
            os.startfile(os.path.abspath(pdf_path))
        except Exception as e:
            self.show_error("Lỗi", f"Không thể mở file PDF: {str(e)}")


    # Kích hoạt hộp thoại chọn file CSV và chuyển tiếp cho controller nạp dữ liệu
    @safe_execution("Lỗi tải CSV")
    def on_import(self):
        """Hộp thoại chọn file và gọi controller nhập dữ liệu CSV."""
        if not self.controller: return
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filepath:
            self.controller.import_csv(filepath)

    # Kích hoạt hộp thoại lưu file CSV và yêu cầu controller xuất dữ liệu
    @safe_execution("Lỗi xuất CSV")
    def on_export(self):
        """Hộp thoại lưu file và gọi controller xuất dữ liệu CSV."""
        if not self.controller: return
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if filepath:
            self.controller.export_csv(filepath)

    # Hiển thị thanh chờ xoay tròn hoặc hộp thoại tiến trình xử lý
    def show_loading(self, message="Đang xử lý...", show_dialog=True):
        """Hiển thị trạng thái chờ và mở popup tiến trình."""
        self.table.show_loading_placeholder()
        if not show_dialog:
            return
        if self._focus_if_exists('loading_window'): return
        self.loading_window = LoadingDialog(self, message)

    # Đóng hộp thoại tiến trình chờ và vẽ lại bảng dữ liệu giao dịch
    def hide_loading(self):
        """Đóng popup tiến trình và nạp dữ liệu hoàn tất."""
        if self.loading_window and self.loading_window.winfo_exists():
            self.loading_window.stop()
            self.loading_window = None
        self.render_table_page()

    # Kích hoạt hiển thị một thông báo Toast thành công góc màn hình
    def show_message(self, title, msg):
        """Hiển thị một thông báo thành công (Toast)."""
        ToastNotification(self, msg, type="info", image=self.icons.get('success')).show()
        
    # Kích hoạt hiển thị một thông báo Toast cảnh báo lỗi góc màn hình
    def show_error(self, title, msg):
        """Hiển thị một thông báo lỗi (Toast)."""
        ToastNotification(self, msg, type="error", image=self.icons.get('error')).show()

    # Làm mới danh sách danh mục trong ô chọn dropdown của biểu mẫu giao dịch
    def refresh_category_dropdown(self):
        """Cập nhật lại danh sách danh mục trong ô chọn (dropdown) sau khi có thay đổi."""
        if self.transaction_window and self.transaction_window.winfo_exists():
            if hasattr(self.transaction_window, 'inp_cat') and self.transaction_window.inp_cat.winfo_exists():
                cats = self._get_categories()
                cats.append(ADD_NEW_CAT_TEXT)
                self.transaction_window.inp_cat.configure(values=cats)
                val = self.transaction_window.inp_cat.get()
                if val not in cats:
                    self.transaction_window.inp_cat.set(cats[0] if cats else "")

    # Tự động bỏ focus ô tìm kiếm khi click ra ngoài
    def unfocus_search(self, event):
        """Bỏ con trỏ nhấp nháy ở ô tìm kiếm khi click vào các khu vực hoặc thành phần khác."""
        if not event.widget:
            return
            
        clicked_widget = event.widget
        # Chuyển đổi từ string path sang widget object nếu cần
        if isinstance(clicked_widget, str):
            try:
                clicked_widget = self.nametowidget(clicked_widget)
            except Exception:
                pass
                
        # Tự động đóng dropdown Xem theo nếu click chuột ra ngoài
        if self.view_by_dropdown and self.view_by_dropdown.winfo_exists():
            in_dropdown = False
            curr = clicked_widget
            while curr:
                if curr == self.view_by_dropdown or curr == self.btn_view_by:
                    in_dropdown = True
                    break
                try:
                    parent_name = curr.winfo_parent()
                    curr = self.nametowidget(parent_name) if parent_name else None
                except:
                    curr = None
            
            if not in_dropdown:
                self.view_by_dropdown.destroy()
                self.view_by_dropdown = None
                
        # Lấy ô tìm kiếm từ header
        search_entry = None
        if hasattr(self, 'header') and self.header:
            search_entry = getattr(self.header, 'entry_search', None)
            
        if search_entry:
            # Nếu click vào ô tìm kiếm hoặc phần tử bên trong của nó, giữ nguyên focus
            if clicked_widget == search_entry or clicked_widget == getattr(search_entry, '_entry', None):
                return
            # Đề phòng click vào các phần phụ bên trong của CustomTkinter entry
            if str(clicked_widget).startswith(str(search_entry)):
                return
                
        # Chuyển focus về main window
        self.focus()

    @safe_execution("Lỗi đóng mở menu xem theo")
    def toggle_view_by_dropdown(self):
        """Đóng hoặc mở dropdown lọc thời gian dưới nút kích hoạt."""
        if self.view_by_dropdown and self.view_by_dropdown.winfo_exists():
            self.view_by_dropdown.destroy()
            self.view_by_dropdown = None
            return
            
        scaling = self._get_window_scaling()
        btn_width = self.btn_view_by.winfo_width() / scaling
        btn_height = self.btn_view_by.winfo_height() / scaling
        
        x = (self.btn_view_by.winfo_rootx() - self.winfo_rootx()) / scaling
        y = (self.btn_view_by.winfo_rooty() - self.winfo_rooty()) / scaling + btn_height
        
        self.view_by_dropdown = ViewByDropdown(
            self, self.btn_view_by, self.apply_time_filter, self.active_time_preset
        )
        self.view_by_dropdown.place(x=x, y=y)
        self.view_by_dropdown.lift()

    @safe_execution("Lỗi áp dụng lọc thời gian")
    def apply_time_filter(self, min_date, max_date, preset_name):
        """Callback nhận kết quả từ dropdown, lưu cấu hình và kích hoạt lọc dữ liệu bảng."""
        self.filter_min_date = min_date
        self.filter_max_date = max_date
        self.active_time_preset = preset_name
        
        self.update_view_by_button_text()
        
        if self.view_by_dropdown and self.view_by_dropdown.winfo_exists():
            self.view_by_dropdown.destroy()
            self.view_by_dropdown = None
            
        self.apply_filters()

    def update_view_by_button_text(self):
        """Cập nhật nhãn hiển thị trên nút công cụ dựa trên khoảng thời gian hiện đang lọc."""
        preset = self.detect_time_preset(self.filter_min_date, self.filter_max_date)
        self.active_time_preset = preset
        
        if preset:
            btn_text = f"Xem theo: {preset}"
        elif self.filter_min_date and self.filter_max_date:
            short_range = self.get_short_range_str(self.filter_min_date, self.filter_max_date)
            btn_text = f"Xem theo: {short_range}"
        else:
            btn_text = "Xem theo: Tất cả"
            
        if hasattr(self, 'btn_view_by') and self.btn_view_by.winfo_exists():
            self.btn_view_by.configure(text=btn_text)

    def detect_time_preset(self, min_date, max_date):
        """Nhận diện xem khoảng thời gian (min_date, max_date) có khớp với Preset nào không."""
        if not min_date and not max_date:
            return "Tất cả"
        if not min_date or not max_date:
            return None
            
        today = datetime.date.today()
        
        # 1. Hôm nay
        today_str = today.strftime("%d/%m/%Y")
        if min_date == today_str and max_date == today_str:
            return "Hôm nay"
            
        # 2. Hôm qua
        yesterday_str = (today - datetime.timedelta(days=1)).strftime("%d/%m/%Y")
        if min_date == yesterday_str and max_date == yesterday_str:
            return "Hôm qua"
            
        # 3. Tuần này
        weekday = today.weekday()
        this_week_start = today - datetime.timedelta(days=weekday)
        this_week_end = this_week_start + datetime.timedelta(days=6)
        if min_date == this_week_start.strftime("%d/%m/%Y") and max_date == this_week_end.strftime("%d/%m/%Y"):
            return "Tuần này"
            
        # 4. Tuần trước
        last_week_start = today - datetime.timedelta(days=weekday + 7)
        last_week_end = last_week_start + datetime.timedelta(days=6)
        if min_date == last_week_start.strftime("%d/%m/%Y") and max_date == last_week_end.strftime("%d/%m/%Y"):
            return "Tuần trước"
            
        # 5. Tháng này
        this_month_start = today.replace(day=1)
        next_month = this_month_start.replace(day=28) + datetime.timedelta(days=4)
        this_month_end = next_month - datetime.timedelta(days=next_month.day)
        if min_date == this_month_start.strftime("%d/%m/%Y") and max_date == this_month_end.strftime("%d/%m/%Y"):
            return "Tháng này"
            
        # 6. Tháng trước
        first_of_this_month = today.replace(day=1)
        last_month_end = first_of_this_month - datetime.timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        if min_date == last_month_start.strftime("%d/%m/%Y") and max_date == last_month_end.strftime("%d/%m/%Y"):
            return "Tháng trước"
            
        # 7. Chips lùi ngày nhanh
        today_str = today.strftime("%d/%m/%Y")
        if max_date == today_str:
            for preset_name, days in [("7 ngày", 7), ("14 ngày", 14), ("30 ngày", 30), ("2 tháng", 60), ("3 tháng", 90)]:
                expected_start = (today - datetime.timedelta(days=days - 1)).strftime("%d/%m/%Y")
                if min_date == expected_start:
                    return preset_name
            
        return None

    def get_short_range_str(self, start_str, end_str):
        """Rút gọn hiển thị khoảng ngày để tránh làm tràn text nút bấm."""
        try:
            s_dt = datetime.datetime.strptime(start_str, "%d/%m/%Y")
            e_dt = datetime.datetime.strptime(end_str, "%d/%m/%Y")
            if s_dt.year == e_dt.year:
                return f"{s_dt.strftime('%d/%m')} – {e_dt.strftime('%d/%m/%Y')}"
            return f"{start_str} – {end_str}"
        except:
            return f"{start_str} – {end_str}"


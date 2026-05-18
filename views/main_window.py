import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import tkinter.messagebox as mb
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import os
from PIL import Image, ImageTk

# --- CONSTANTS ---
TX_TYPE_EXPENSE_VN = "Chi tiêu"
TX_TYPE_INCOME_VN = "Thu nhập"
ADD_NEW_CAT_TEXT = "Thêm mới..."

# --- COLORS & FONTS ---
BG_COLOR = "#0F172A"
PANEL_BG = "#1E293B"
PANEL_BG_HOVER = "#334155"
ACCENT_BLUE = "#323546"
ACCENT_GREEN = "#10B981"
ACCENT_RED = "#EF4444"
ACCENT_AMBER = "#F59E0B"
TEXT_MAIN = "#F8FAFC"
TEXT_MUTED = "#94A3B8"
BORDER_COLOR = "#334155"

FONT_MAIN = ("Consolas", 13)
FONT_TITLE = ("Consolas", 16, "bold")
FONT_AMOUNT = ("Consolas", 14, "bold")
FONT_SUMMARY = ("Consolas", 20, "bold")

FONT_BUTTON = ("Consolas", 13, "bold")
FONT_TABLE_HEADER = ("Consolas", 14, "bold")
FONT_BADGE = ("Consolas", 10, "bold")
FONT_BUTTON_LARGE = ("Consolas", 14, "bold")
FONT_TEXT_LARGE = ("Consolas", 14)
FONT_LABEL = ("Consolas", 11, "bold")
FONT_CONTEXT_MENU = ("Consolas", 14)
CONTEXT_MENU_WIDTH = 15
CONTEXT_MENU_ICON_SIZE = 16 # Tuỳ chỉnh cỡ icon trong popup
CONTEXT_MENU_ICON_PADX = 10 # Tuỳ chỉnh khoảng cách lề trái của icon

class ToastNotification(ctk.CTkFrame):
    def __init__(self, master, message, type="info", image=None, **kwargs):
        """Khởi tạo cửa sổ chính và các biến cơ bản."""
        bcolor = ACCENT_RED if type == "error" else ACCENT_GREEN
        super().__init__(master, fg_color=PANEL_BG, corner_radius=8, border_width=1, border_color=bcolor, **kwargs)
        self.lbl = ctk.CTkLabel(self, text=f"  {message}", image=image, compound="left", text_color=TEXT_MAIN, font=FONT_MAIN)
        self.lbl.pack(padx=20, pady=12)
        
    def show(self, ms=3000):
        """Hiển thị thông báo (Toast) và tự động ẩn sau một khoảng thời gian."""
        self.place(relx=0.98, rely=0.95, anchor="se")
        self.after(ms, self.destroy)

class MainWindow(ctk.CTk):
    def __init__(self):
        """Khởi tạo cửa sổ chính và các biến cơ bản."""
        super().__init__()
        
        self.title("Quản Lý Chi Tiêu Cá Nhân")
        self.geometry("1200x700")
        self.configure(fg_color=BG_COLOR)
        ctk.set_appearance_mode("dark")
        
        self.controller = None
        self.dashboard_window = None
        self.help_window = None
        self.loading_window = None
        self.calendar_window = None
        self.budget_window = None
        self.transaction_window = None
        self.category_window = None
        self.filter_window = None
        
        self.transactions = []
        self.filtered_transactions = []
        self.current_page = 1
        self.rows_per_page = 15
        
        self.selected_row_ids = set()
        self.select_all_var = tk.BooleanVar(value=False)
        self.sort_by = "Thời gian"
        self.sort_order = "desc"
        
        self.filter_category = "Tất cả"
        self.filter_type = "Tất cả"
        self.filter_min_amt = ""
        self.filter_max_amt = ""
        self.filter_min_date = ""
        self.filter_max_date = ""
        
        self.load_icons()
        
        self.setup_ui()
        self.bind_shortcuts()

    def load_icons(self):
        """Tải các biểu tượng icon từ thư mục assets."""
        icon_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icons")
        self.icons = {}
        self.menu_icons = {}
        icon_names = ['import', 'export', 'stats', 'help', 'edit', 'delete', 'add', 'search', 'tx', 'exp', 'inc', 'net', 'success', 'error', 'money', 'empty', 'copy', 'calendar', 'budget', 'alert', 'savings', 'safe', 'danger', 'warning', 'sort', 'sort_up', 'sort_down', 'left', 'right', 'app_logo', 'nav_budget', 'dialog_budget', 'filter']
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
        
    def set_controller(self, controller):
        """Thiết lập controller kết nối với view và nạp dữ liệu ban đầu."""
        self.controller = controller
        self.controller.load_initial_data()
        
    def setup_ui(self):
        """Khởi tạo và bố trí toàn bộ các thành phần giao diện chính."""
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.setup_topbar()
        self.setup_summary_strip()
        self.setup_action_bar()
        self.setup_main_table()
        self.setup_bottom_bar()

    def _focus_if_exists(self, window_attr):
        """Kiểm tra xem cửa sổ đã tồn tại chưa, nếu có thì focus và trả về True."""
        win = getattr(self, window_attr, None)
        if win and win.winfo_exists():
            win.focus()
            return True
        return False

    def _create_form_label(self, parent, text, top_pady=15):
        """Hàm hỗ trợ tạo label cho form."""
        ctk.CTkLabel(parent, text=text, font=FONT_LABEL, text_color=TEXT_MUTED).pack(anchor="w", pady=(top_pady, 5))

    def _create_checkbox(self, parent, variable, command):
        """Hàm hỗ trợ tạo checkbox giao diện đồng nhất."""
        return ctk.CTkCheckBox(
            parent, text="", variable=variable, width=40,
            checkbox_width=20, checkbox_height=20, border_width=2, corner_radius=5,
            border_color="#64748B", fg_color="#3B82F6", hover_color="#2563EB",
            command=command
        )

    def _get_categories(self):
        """Lấy danh sách danh mục một cách an toàn."""
        return self.controller.get_categories() if self.controller else []

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

    def setup_topbar(self):
        """Khởi tạo thanh công cụ trên cùng (Tìm kiếm, Nhập/Xuất CSV, Hướng dẫn)."""
        self.topbar = ctk.CTkFrame(self, height=48, fg_color=PANEL_BG, corner_radius=0)
        self.topbar.grid(row=0, column=0, sticky="ew")
        self.topbar.grid_columnconfigure(1, weight=1)
        
        left_frame = ctk.CTkFrame(self.topbar, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=20, sticky="w")
        ctk.CTkLabel(left_frame, text="", image=self.icons.get('app_logo')).pack(side="left", padx=(0,10))
        ctk.CTkLabel(left_frame, text="Quản Lý Chi Tiêu Cá Nhân", font=FONT_TITLE, text_color=TEXT_MAIN).pack(side="left")
        
        center_frame = ctk.CTkFrame(self.topbar, fg_color="transparent")
        center_frame.grid(row=0, column=1, pady=8)
        self.entry_search = ctk.CTkEntry(center_frame, placeholder_text="Tìm kiếm giao dịch...", width=400, height=32, corner_radius=16, border_width=1, fg_color=BG_COLOR, border_color=BORDER_COLOR, font=FONT_MAIN)
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<KeyRelease>", self.on_search_typing)
        
        right_frame = ctk.CTkFrame(self.topbar, fg_color="transparent")
        right_frame.grid(row=0, column=2, padx=20, sticky="e")
        
        for text, icon, cmd in [(" Nhập CSV", 'import', self.on_import), (" Xuất CSV", 'export', self.on_export),
                                (" Thống kê", 'stats', self.show_dashboard), (" Ngân sách", 'nav_budget', self.show_budget_window), (" Hướng dẫn", 'help', self.show_help)]:
            ctk.CTkButton(right_frame, text=text, image=self.icons.get(icon), height=36, fg_color="transparent", hover_color=PANEL_BG_HOVER, font=FONT_BUTTON, command=cmd).pack(side="left", padx=2)

    def setup_summary_strip(self):
        """Khởi tạo khu vực hiển thị các thẻ tổng quan (Tổng giao dịch, Chi tiêu, Thu nhập, Số dư)."""
        self.summary_strip = ctk.CTkFrame(self, height=64, fg_color="transparent")
        self.summary_strip.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        self.card_tx = self.create_summary_card(self.summary_strip, "TỔNG GIAO DỊCH", "0", self.icons.get('tx'))
        self.card_exp = self.create_summary_card(self.summary_strip, "TỔNG CHI TIÊU", "0", self.icons.get('exp'), ACCENT_RED)
        self.card_inc = self.create_summary_card(self.summary_strip, "TỔNG THU NHẬP", "0", self.icons.get('inc'), ACCENT_GREEN)
        self.card_net = self.create_summary_card(self.summary_strip, "SỐ DƯ", "0", self.icons.get('net'), ACCENT_BLUE)
        
    def create_summary_card(self, parent, label, value, icon, value_color=TEXT_MAIN):
        """Tạo một thẻ hiển thị thông tin tóm tắt."""
        card = ctk.CTkFrame(parent, fg_color=PANEL_BG, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        card.pack(side="left", fill="x", expand=True, padx=5)
        
        top_frame = ctk.CTkFrame(card, fg_color="transparent")
        top_frame.pack(fill="x", padx=15, pady=(10, 0))
        if icon:
            ctk.CTkLabel(top_frame, text="", image=icon).pack(side="left", padx=(0,5))
        ctk.CTkLabel(top_frame, text=label, font=FONT_LABEL, text_color=TEXT_MUTED).pack(side="left")
        
        val_lbl = ctk.CTkLabel(card, text=value, font=FONT_SUMMARY, text_color=value_color)
        val_lbl.pack(anchor="w", padx=15, pady=(0, 10))
        return val_lbl

    def setup_action_bar(self):
        """Khởi tạo thanh hành động (chứa nút Thêm giao dịch)."""
        self.action_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.action_bar.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Nút Thêm giao dịch (Màu xanh nổi bật): Trượt mở bảng Side Drawer bên phải để nhập thông tin
        btn_add = ctk.CTkButton(self.action_bar, text=" Thêm giao dịch", image=self.icons.get('add'), fg_color=ACCENT_BLUE, font=FONT_BUTTON, corner_radius=16, height=36, command=self.open_transaction_window)
        btn_add.pack(side="left")
        
        # Nút Lọc
        btn_filter = ctk.CTkButton(self.action_bar, text=" Lọc", image=self.icons.get('filter'), fg_color=PANEL_BG, hover_color=PANEL_BG_HOVER, font=FONT_BUTTON, corner_radius=16, height=36, width=90, border_width=1, border_color=BORDER_COLOR, command=self.open_filter_window)
        btn_filter.pack(side="left", padx=(10, 0))

    def setup_main_table(self):
        """Khởi tạo cấu trúc bảng hiển thị danh sách giao dịch."""
        self.table_container = ctk.CTkFrame(self, fg_color="transparent")
        self.table_container.grid(row=3, column=0, sticky="nsew", padx=20, pady=0)
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(1, weight=1)
        
        header_frame = ctk.CTkFrame(self.table_container, height=36, fg_color=PANEL_BG, corner_radius=8)
        header_frame.pack_propagate(False)
        header_frame.grid(row=0, column=0, sticky="ew")
        
        self.header_labels = {}
        self.cols = [("☐", 40), ("#", 40), ("Thời gian", 160), ("Danh mục", 150), ("Loại", 100), ("Số tiền", 140), ("Ghi chú", 200), ("Thao tác", 80)]
        for text, width in self.cols:
            anchor = "e" if text == "Số tiền" else "w"
            if text in ["☐", "#", "Thao tác", "Loại"]: anchor = "center"
            
            if text == "☐":
                self.header_checkbox = self._create_checkbox(header_frame, self.select_all_var, self.toggle_select_all)
                self.header_checkbox.pack(side="left", padx=(16,0))
            else:
                cursor = "hand2" if text in ["Thời gian", "Số tiền"] else ""
                col_frame = ctk.CTkFrame(header_frame, fg_color="transparent", width=width, height=36)
                col_frame.pack_propagate(False)
                
                custom_padx = (20, 5) if text == "Ghi chú" else 5
                col_frame.pack(side="left", padx=custom_padx, fill="y")
                
                inner = ctk.CTkFrame(col_frame, fg_color="transparent", height=36)
                if anchor == "w": inner.pack(side="left", fill="y")
                elif anchor == "e": inner.pack(side="right", fill="y")
                else: inner.pack(expand=True, fill="y")
                
                lbl = ctk.CTkLabel(inner, text=text, font=FONT_TABLE_HEADER, text_color=TEXT_MUTED, cursor=cursor)
                lbl.pack(side="left")
                
                if text in ["Thời gian", "Số tiền"]:
                    lbl_arr = ctk.CTkLabel(inner, text="", image=self.icons.get('sort'), cursor=cursor)
                    lbl_arr.pack(side="left", padx=(5, 0))
                    self.header_labels[text] = lbl_arr
                    
                    lbl.bind("<Button-1>", lambda e, c=text: self.sort_by_column(c))
                    lbl_arr.bind("<Button-1>", lambda e, c=text: self.sort_by_column(c))
                    col_frame.bind("<Button-1>", lambda e, c=text: self.sort_by_column(c))
                    
        self.update_header_arrows()
                    
        self.table_scroll = ctk.CTkScrollableFrame(self.table_container, fg_color=BG_COLOR)
        self.table_scroll.grid(row=1, column=0, sticky="nsew", pady=(5,0))

    def setup_bottom_bar(self):
        """Khởi tạo thanh điều hướng phân trang và các nút thao tác hàng loạt (bulk actions) ở dưới cùng."""
        self.bottom_bar = ctk.CTkFrame(self, height=48, fg_color=PANEL_BG, corner_radius=10)
        self.bottom_bar.grid(row=4, column=0, sticky="ew", padx=20, pady=(5, 10))
        self.bottom_bar.grid_columnconfigure(0, weight=1)
        self.bottom_bar.grid_rowconfigure(0, weight=1)
        self.bottom_bar.grid_propagate(False)
        
        self.bulk_frame = ctk.CTkFrame(self.bottom_bar, fg_color="transparent")
        self.bulk_frame.grid(row=0, column=0, sticky="w", padx=10, pady=6)
        for text, icon, color, cmd in [(" Xoá đã chọn", 'delete', ACCENT_RED, self.on_delete_selected), 
                                       (" Xuất đã chọn", 'export', PANEL_BG_HOVER, self.on_export_selected)]:
            ctk.CTkButton(self.bulk_frame, text=text, image=self.icons.get(icon), fg_color=color, 
                          width=130, height=28, command=cmd).pack(side="left", padx=4)
        self.bulk_frame.grid_remove()
        
        right_frame = ctk.CTkFrame(self.bottom_bar, fg_color="transparent")
        right_frame.grid(row=0, column=1, padx=10, pady=4, sticky="e")
        
        # Khu vực chứa các nút phân trang
        self.pagination_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        self.pagination_frame.pack(side="left", padx=5)

    def bind_shortcuts(self):
        """Đăng ký các phím tắt cho ứng dụng (Ctrl+N, Ctrl+F, Delete)."""
        self.bind("<Control-n>", lambda e: self.open_transaction_window())
        self.bind("<Control-f>", lambda e: self.entry_search.focus())
        self.bind("<Delete>", lambda e: self.on_delete_selected())

    # --- ACTIONS & LOGIC ---

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
        
        self.update_header_arrows()
        self.on_search_typing(None)

    def update_header_arrows(self):
        """Cập nhật hiển thị mũi tên ở tiêu đề bảng theo trạng thái sắp xếp hiện tại."""
        if not hasattr(self, 'header_labels'): return
        for col, lbl_arr in self.header_labels.items():
            if self.sort_by == col:
                if self.sort_order == "desc":
                    lbl_arr.configure(image=self.icons.get('sort_down'))
                else:
                    lbl_arr.configure(image=self.icons.get('sort_up'))
            else:
                lbl_arr.configure(image=self.icons.get('sort'))

    def apply_sort(self):
        """Áp dụng sắp xếp vào danh sách filtered_transactions."""
        if not self.filtered_transactions: return
        
        if self.sort_by == "Thời gian":
            def get_date(t):
                try:
                    return datetime.datetime.strptime(t['date'], "%d/%m/%Y %H:%M")
                except ValueError:
                    try:
                        return datetime.datetime.strptime(t['date'], "%d/%m/%Y")
                    except ValueError:
                        return datetime.datetime.min
            self.filtered_transactions.sort(key=get_date, reverse=(self.sort_order == "desc"))
        elif self.sort_by == "Số tiền":
            self.filtered_transactions.sort(key=lambda t: float(t['amount']), reverse=(self.sort_order == "desc"))

    def on_search_typing(self, event):
        """Xử lý sự kiện khi người dùng gõ từ khóa vào thanh tìm kiếm."""
        self.apply_filters()

    def apply_filters(self):
        kw = self.entry_search.get().lower()
        res = []
        for t in self.transactions:
            if kw and kw not in str(t['note']).lower() and kw not in str(t['category']).lower() and kw not in str(t['amount']):
                continue
            if self.filter_category != "Tất cả" and t['category'] != self.filter_category:
                continue
            if self.filter_type != "Tất cả" and t['type'] != self.filter_type:
                continue
            
            try:
                amt = float(t['amount'])
                if self.filter_min_amt:
                    if amt < float(self.filter_min_amt.replace(',', '')):
                        continue
                if self.filter_max_amt:
                    if amt > float(self.filter_max_amt.replace(',', '')):
                        continue
            except ValueError:
                pass
                
            try:
                dt_str = str(t['date'])
                fmt = "%d/%m/%Y %H:%M" if ":" in dt_str else "%d/%m/%Y"
                dt = datetime.datetime.strptime(dt_str, fmt)
                if self.filter_min_date:
                    min_dt = datetime.datetime.strptime(self.filter_min_date, "%d/%m/%Y")
                    if dt.date() < min_dt.date():
                        continue
                if self.filter_max_date:
                    max_dt = datetime.datetime.strptime(self.filter_max_date, "%d/%m/%Y")
                    if dt.date() > max_dt.date():
                        continue
            except ValueError:
                pass
                
            res.append(t)
            
        self.filtered_transactions = res
        self.apply_sort()
        self.current_page = 1
        self.render_table_page()
        self.update_summary_cards()

    def update_summary_cards(self):
        """Cập nhật các thẻ tổng quan dựa trên danh sách giao dịch đang được hiển thị (đã lọc)."""
        txs = self.filtered_transactions
        total_tx = len(txs)
        total_inc = sum(float(t['amount']) for t in txs if t['type'] == TX_TYPE_INCOME_VN)
        total_exp = sum(float(t['amount']) for t in txs if t['type'] == TX_TYPE_EXPENSE_VN)
        net = total_inc - total_exp
        
        self.card_tx.configure(text=str(total_tx))
        self.card_exp.configure(text=f"{total_exp:,.0f} đ")
        self.card_inc.configure(text=f"{total_inc:,.0f} đ")
        self.card_net.configure(text=f"{net:,.0f} đ", text_color=ACCENT_GREEN if net >= 0 else ACCENT_RED)

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

    def render_table_page(self):
        """Hiển thị dữ liệu các giao dịch lên bảng theo trang hiện tại."""
        for widget in self.table_scroll.winfo_children():
            widget.destroy()
            
        if not self.filtered_transactions:
            self.select_all_var.set(False)
            ctk.CTkLabel(self.table_scroll, text=" Không tìm thấy giao dịch nào", image=self.icons.get('empty'), compound="left", font=FONT_TITLE, text_color=TEXT_MUTED).pack(pady=50)
            self.render_pagination(1)
            return
            
        if len(self.selected_row_ids) == len(self.filtered_transactions):
            self.select_all_var.set(True)
            if hasattr(self, 'header_checkbox'): self.header_checkbox.select()
        else:
            self.select_all_var.set(False)
            if hasattr(self, 'header_checkbox'): self.header_checkbox.deselect()
            
        start_idx = (self.current_page - 1) * self.rows_per_page
        end_idx = start_idx + self.rows_per_page
        page_data = self.filtered_transactions[start_idx:end_idx]
        
        total_pages = max(1, (len(self.filtered_transactions) + self.rows_per_page - 1) // self.rows_per_page)
        self.render_pagination(total_pages)
        
        for idx, t in enumerate(page_data):
            self.create_table_row(t, start_idx + idx)
            
        self.update_bulk_actions_visibility()

    def create_table_row(self, t, index):
        """Tạo một hàng dữ liệu cho một giao dịch cụ thể trong bảng."""
        bg_color = "transparent"
        
        outer_row = ctk.CTkFrame(self.table_scroll, fg_color="transparent")
        outer_row.pack(fill="x")
        
        row = ctk.CTkFrame(outer_row, height=44, fg_color=bg_color, corner_radius=0)
        row.pack(fill="x")
        row.pack_propagate(False)
        
        # Thêm đường kẻ ngang ngăn cách giữa các dòng (Separator)
        separator = tk.Frame(outer_row, bg=BORDER_COLOR, height=1)
        separator.pack(fill="x", padx=10)
        
        action_frame = ctk.CTkFrame(row, fg_color="transparent", width=80)
        
        def on_enter(e, r=row, af=action_frame):
            r.configure(fg_color=PANEL_BG_HOVER)
            
        def on_leave(e, r=row, orig=bg_color, af=action_frame):
            if t['id'] not in self.selected_row_ids:
                r.configure(fg_color=orig)
            else:
                r.configure(fg_color="#1E3A8A")
            
        chk_var = tk.BooleanVar(value=t['id'] in self.selected_row_ids)
        chk = self._create_checkbox(row, chk_var, lambda id=t['id'], v=chk_var, r=row: self.toggle_row_selection(id, v.get(), r, v))
        chk.pack(side="left", padx=(10,0))
        
        ctk.CTkLabel(row, text=str(t['id']), width=40, anchor="center", font=FONT_MAIN, text_color=TEXT_MUTED).pack(side="left", padx=5)
        
        date_str = str(t['date'])
        if " " not in date_str: date_str += " 00:00"
        ctk.CTkLabel(row, text=date_str, width=160, anchor="w", font=FONT_MAIN).pack(side="left", padx=5)
        
        ctk.CTkLabel(row, text=t['category'], width=150, anchor="w", font=FONT_MAIN).pack(side="left", padx=5)
        
        type_color = ACCENT_RED if t['type'] == TX_TYPE_EXPENSE_VN else ACCENT_GREEN
        display_type = t['type']
        
        type_frame = ctk.CTkFrame(row, width=100, height=36, fg_color="transparent")
        type_frame.pack_propagate(False)
        type_frame.pack(side="left", padx=5)
        badge = ctk.CTkFrame(type_frame, fg_color=type_color, corner_radius=10, width=80, height=24)
        badge.pack_propagate(False)
        badge.pack(expand=True)
        ctk.CTkLabel(badge, text=display_type, font=FONT_BADGE, text_color="white").pack(expand=True)
        
        amt_str = f"{float(t['amount']):,.0f} đ"
        ctk.CTkLabel(row, text=amt_str, width=140, anchor="e", font=FONT_AMOUNT, text_color=type_color).pack(side="left", padx=5)
        
        ctk.CTkLabel(row, text=str(t['note'])[:30], width=200, anchor="w", font=FONT_MAIN, text_color=TEXT_MUTED).pack(side="left", padx=(20, 5))
        
        action_frame.pack_propagate(False)
        action_frame.pack(side="left", padx=5)
        # Nút Sửa (Icon Edit): Sẽ trượt mở Side Drawer với các thông tin đã điền sẵn để người dùng chỉnh sửa
        btn_edit = ctk.CTkButton(action_frame, text="", image=self.icons.get('edit'), width=30, height=30, fg_color="transparent", hover_color=ACCENT_BLUE, command=lambda t=t: self.open_transaction_window(edit_t=t))
        btn_edit.pack(side="left", padx=2)
        # Nút Xóa (Icon Xóa): Mở cảnh báo, sau khi xác nhận thì xóa ngay giao dịch này
        btn_del = ctk.CTkButton(action_frame, text="", image=self.icons.get('delete'), width=30, height=30, fg_color="transparent", hover_color=ACCENT_RED, command=lambda t=t: self.delete_single_transaction(t))
        btn_del.pack(side="left", padx=2)

        row.bind("<Enter>", on_enter)
        row.bind("<Leave>", on_leave)
        for child in row.winfo_children():
            child.bind("<Button-3>", lambda e, t=t: self.show_context_menu(e, t))
            if not isinstance(child, ctk.CTkButton) and not isinstance(child, ctk.CTkCheckBox):
                child.bind("<Button-1>", lambda e, id=t['id'], v=chk_var, r=row: self.toggle_row_selection(id, not v.get(), r, v))

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
            if hasattr(self, 'header_checkbox'): self.header_checkbox.select()
        else:
            self.select_all_var.set(False)
            if hasattr(self, 'header_checkbox'): self.header_checkbox.deselect()

    def update_bulk_actions_visibility(self):
        """Hiển thị hoặc ẩn khung các nút thao tác hàng loạt tùy thuộc vào số lượng dòng được chọn."""
        if self.selected_row_ids:
            self.bulk_frame.grid()
        else:
            self.bulk_frame.grid_remove()

    def prev_page(self):
        """Chuyển về trang trước đó trong danh sách giao dịch."""
        if self.current_page > 1:
            self.current_page -= 1
            self.render_table_page()
            
    def next_page(self):
        """Chuyển sang trang tiếp theo trong danh sách giao dịch."""
        total_pages = max(1, (len(self.filtered_transactions) + self.rows_per_page - 1) // self.rows_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self.render_table_page()

    def render_pagination(self, total_pages):
        """Hiển thị dãy nút phân trang."""
        for widget in self.pagination_frame.winfo_children():
            widget.destroy()
            
        if total_pages <= 1:
            return
            
        # Nút prev
        btn_prev = ctk.CTkButton(self.pagination_frame, text="", image=self.icons.get('left'), width=28, height=28, fg_color="transparent", text_color=TEXT_MUTED, hover_color=PANEL_BG_HOVER, command=self.prev_page)
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
                ctk.CTkButton(self.pagination_frame, text=str(p), width=30, height=30, corner_radius=6, fg_color=fg_col, text_color=txt_col, hover_color=hov_col, font=("Consolas", 12, "bold"), command=lambda page=p: self.go_to_page(page)).pack(side="left", padx=2)
                
        # Nút next
        btn_next = ctk.CTkButton(self.pagination_frame, text="", image=self.icons.get('right'), width=28, height=28, fg_color="transparent", text_color=TEXT_MUTED, hover_color=PANEL_BG_HOVER, command=self.next_page)
        btn_next.pack(side="left", padx=2)

    def go_to_page(self, page):
        """Chuyển đến một trang cụ thể khi click vào nút số."""
        if self.current_page != page:
            self.current_page = page
            self.render_table_page()

    def show_context_menu(self, event, t):
        """Hiển thị menu ngữ cảnh (chuột phải) cho một dòng giao dịch."""
        menu = tk.Menu(self, tearoff=0, bg=PANEL_BG, fg=TEXT_MAIN, activebackground=ACCENT_BLUE, font=FONT_CONTEXT_MENU)
        menu.add_command(label=" Sửa".ljust(CONTEXT_MENU_WIDTH), image=self.menu_icons.get('edit'), compound="left", command=lambda: self.open_transaction_window(edit_t=t))
        menu.add_command(label=" Xóa".ljust(CONTEXT_MENU_WIDTH), image=self.menu_icons.get('delete'), compound="left", command=lambda: self.delete_single_transaction(t))
        menu.add_command(label=" Nhân bản".ljust(CONTEXT_MENU_WIDTH), image=self.menu_icons.get('copy'), compound="left", command=lambda: self.duplicate_transaction(t))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def duplicate_transaction(self, t):
        """Tạo một bản sao của giao dịch đang chọn."""
        if not self.controller: return
        self.controller.add_transaction(t['date'], float(t['amount']), t['category'], t['type'], t['note'] + " (Bản sao)")

    def delete_single_transaction(self, t):
        """Xóa một giao dịch đơn lẻ sau khi xác nhận."""
        if mb.askyesno("Xác nhận", f"Xóa giao dịch có ID {t['id']}?", icon="warning"):
            self.controller.delete_transactions([t['id']])

    def on_delete_selected(self):
        """Xóa nhiều giao dịch đã được chọn."""
        if not self.selected_row_ids: return
        if mb.askyesno("Xác nhận", f"Xóa {len(self.selected_row_ids)} giao dịch đã chọn?", icon="warning"):
            self.controller.delete_transactions(list(self.selected_row_ids))
            self.selected_row_ids.clear()

    def on_export_selected(self):
        """Xuất dữ liệu của các giao dịch đã chọn ra file CSV."""
        if not self.selected_row_ids: return
        self.show_message("Xuất file", f"Đang xuất {len(self.selected_row_ids)} giao dịch (Giả lập).")

    def open_filter_window(self):
        """Mở cửa sổ lọc các giao dịch theo tiêu chí giống thiết kế"""
        if self._focus_if_exists('filter_window'): return
        
        self.filter_window = self.create_toplevel_window("Lọc giao dịch", 550, 400)
        self.filter_window.configure(fg_color=PANEL_BG)
        
        # Header
        hdr = ctk.CTkFrame(self.filter_window, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(hdr, text="Bộ lọc", font=FONT_TITLE, text_color=TEXT_MAIN).pack(side="left")
        
        content = ctk.CTkFrame(self.filter_window, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20)
        
        def create_row(label_text):
            row = ctk.CTkFrame(content, fg_color="transparent")
            row.pack(fill="x", pady=8)
            lbl = ctk.CTkLabel(row, text=label_text, width=120, anchor="w", font=FONT_MAIN, text_color=TEXT_MUTED)
            lbl.pack(side="left")
            return row
            
        # Danh mục
        cats = ["Tất cả"] + self._get_categories()
        row_cat = create_row("Danh mục")
        self.cb_filter_cat = ctk.CTkOptionMenu(row_cat, values=cats, height=36, font=FONT_MAIN, fg_color=BG_COLOR, button_color=BG_COLOR, button_hover_color=PANEL_BG_HOVER)
        self.cb_filter_cat.pack(side="left", fill="x", expand=True)
        self.cb_filter_cat.set(self.filter_category)
        
        # Loại
        row_type = create_row("Loại")
        self.cb_filter_type = ctk.CTkOptionMenu(row_type, values=["Tất cả", TX_TYPE_EXPENSE_VN, TX_TYPE_INCOME_VN], height=36, font=FONT_MAIN, fg_color=BG_COLOR, button_color=BG_COLOR, button_hover_color=PANEL_BG_HOVER)
        self.cb_filter_type.pack(side="left", fill="x", expand=True)
        self.cb_filter_type.set(self.filter_type)
        
        # Số tiền
        row_amt = create_row("Số tiền")
        self.entry_min_amt = ctk.CTkEntry(row_amt, placeholder_text="Từ (đ)", height=36, font=FONT_MAIN, fg_color=BG_COLOR, border_color=BORDER_COLOR)
        self.entry_min_amt.pack(side="left", fill="x", expand=True)
        self.entry_min_amt.insert(0, self.filter_min_amt)
        ctk.CTkLabel(row_amt, text=" - ", font=FONT_MAIN).pack(side="left", padx=5)
        self.entry_max_amt = ctk.CTkEntry(row_amt, placeholder_text="Đến (đ)", height=36, font=FONT_MAIN, fg_color=BG_COLOR, border_color=BORDER_COLOR)
        self.entry_max_amt.pack(side="left", fill="x", expand=True)
        self.entry_max_amt.insert(0, self.filter_max_amt)
        
        # Thời gian
        row_date = create_row("Thời gian")
        self.entry_min_date = ctk.CTkEntry(row_date, placeholder_text="Từ (DD/MM/YYYY)", height=36, font=FONT_MAIN, fg_color=BG_COLOR, border_color=BORDER_COLOR)
        self.entry_min_date.pack(side="left", fill="x", expand=True)
        self.entry_min_date.insert(0, self.filter_min_date)
        ctk.CTkLabel(row_date, text=" - ", font=FONT_MAIN).pack(side="left", padx=5)
        self.entry_max_date = ctk.CTkEntry(row_date, placeholder_text="Đến (DD/MM/YYYY)", height=36, font=FONT_MAIN, fg_color=BG_COLOR, border_color=BORDER_COLOR)
        self.entry_max_date.pack(side="left", fill="x", expand=True)
        self.entry_max_date.insert(0, self.filter_max_date)
        
        # Footer buttons
        footer = ctk.CTkFrame(self.filter_window, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=20, side="bottom")
        
        btn_reset = ctk.CTkButton(footer, text="Đặt lại", width=100, height=40, fg_color="transparent", hover_color=PANEL_BG_HOVER, font=FONT_BUTTON, command=self.reset_filters)
        btn_reset.pack(side="left")
        
        btn_apply = ctk.CTkButton(footer, text="Áp dụng", width=100, height=40, fg_color="#3B82F6", hover_color="#2563EB", font=FONT_BUTTON, command=self.save_filters)
        btn_apply.pack(side="right")
        
    def reset_filters(self):
        self.cb_filter_cat.set("Tất cả")
        self.cb_filter_type.set("Tất cả")
        self.entry_min_amt.delete(0, "end")
        self.entry_max_amt.delete(0, "end")
        self.entry_min_date.delete(0, "end")
        self.entry_max_date.delete(0, "end")
        
    def save_filters(self):
        self.filter_category = self.cb_filter_cat.get()
        self.filter_type = self.cb_filter_type.get()
        self.filter_min_amt = self.entry_min_amt.get().strip()
        self.filter_max_amt = self.entry_max_amt.get().strip()
        self.filter_min_date = self.entry_min_date.get().strip()
        self.filter_max_date = self.entry_max_date.get().strip()
        self.filter_window.destroy()
        self.apply_filters()

    def open_transaction_window(self, edit_t=None):
        """Khởi tạo và hiển thị cửa sổ con để Thêm hoặc Sửa thông tin giao dịch."""
        if self._focus_if_exists('transaction_window'): return
            
        title = "Giao dịch mới" if not edit_t else "Sửa giao dịch"
        self.transaction_window = self.create_toplevel_window(title, 400, 580)
        
        self.current_edit_id = edit_t['id'] if edit_t else None
        
        form = ctk.CTkFrame(self.transaction_window, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=20)
        
        self._create_form_label(form, "THỜI GIAN", top_pady=10)
        
        datetime_frame = ctk.CTkFrame(form, fg_color="transparent")
        datetime_frame.pack(fill="x")
        
        self.inp_date = ctk.CTkEntry(datetime_frame, placeholder_text="DD/MM/YYYY", height=36)
        self.inp_date.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        btn_calendar = ctk.CTkButton(datetime_frame, text="", image=self.icons.get('calendar'), width=36, height=36, fg_color=PANEL_BG_HOVER, hover_color=ACCENT_BLUE, command=self.open_calendar_popup)
        btn_calendar.pack(side="left", padx=(0, 10))
        
        self.inp_time = ctk.CTkEntry(datetime_frame, placeholder_text="HH:MM", height=36, width=80)
        self.inp_time.pack(side="left")
        
        if edit_t:
            dt_parts = str(edit_t['date']).split()
            date_val = dt_parts[0]
            if '-' in date_val: # Convert YYYY-MM-DD to DD/MM/YYYY if needed
                p = date_val.split('-')
                if len(p) == 3 and len(p[0]) == 4:
                    date_val = f"{p[2]}/{p[1]}/{p[0]}"
            time_val = dt_parts[1] if len(dt_parts) > 1 else "00:00"
            if len(time_val.split(':')) == 3: time_val = time_val.rsplit(':', 1)[0]
        else:
            now = datetime.datetime.now()
            date_val = now.strftime("%d/%m/%Y")
            time_val = now.strftime("%H:%M")
            
        self.inp_date.insert(0, date_val)
        self.inp_time.insert(0, time_val)
        
        self._create_form_label(form, "SỐ TIỀN")
        self.inp_amount = ctk.CTkEntry(form, placeholder_text="0", height=40, font=FONT_AMOUNT)
        self.inp_amount.pack(fill="x")
        self.inp_amount.bind("<KeyRelease>", self.format_amount_input)
        if edit_t:
            amt_val = str(edit_t['amount'])
            try:
                amt_val = "{:,}".format(int(float(amt_val)))
            except: pass
            self.inp_amount.insert(0, amt_val)
        
        self._create_form_label(form, "LOẠI")
        self.inp_type = ctk.CTkSegmentedButton(form, values=[TX_TYPE_EXPENSE_VN, TX_TYPE_INCOME_VN], height=36, selected_color=ACCENT_BLUE)
        self.inp_type.pack(fill="x")
        if edit_t:
            self.inp_type.set(edit_t.get('type', TX_TYPE_EXPENSE_VN))
        else:
            self.inp_type.set(TX_TYPE_EXPENSE_VN)
        
        self._create_form_label(form, "DANH MỤC")
        cats = self._get_categories()
        cats.append(ADD_NEW_CAT_TEXT)
        self.inp_cat = ctk.CTkOptionMenu(form, values=cats, height=36, command=self.on_category_select)
        self.inp_cat.pack(fill="x")
        if edit_t:
            val = edit_t['category']
            if val not in cats:
                val = cats[0] if cats else ""
            self.inp_cat.set(val)
        else:
            self.inp_cat.set(cats[0] if cats else "")
            
        self._create_form_label(form, "GHI CHÚ")
        self.inp_note = ctk.CTkEntry(form, placeholder_text="Giao dịch này dùng để làm gì?", height=36)
        self.inp_note.pack(fill="x")
        if edit_t: self.inp_note.insert(0, edit_t['note'])
        
        btn_confirm = ctk.CTkButton(self.transaction_window, text="Xác nhận", fg_color=ACCENT_BLUE, height=48, font=FONT_BUTTON_LARGE, command=self.save_transaction)
        btn_confirm.pack(fill="x", padx=20, pady=20, side="bottom")

    def open_calendar_popup(self):
        """Mở popup chọn ngày."""
        if self._focus_if_exists('calendar_window'): return
        self.calendar_window = self.create_toplevel_window("Chọn ngày", 300, 300)
        
        import tkcalendar
        
        try:
            current_date_str = self.inp_date.get()
            fmt = "%d/%m/%Y" if "/" in current_date_str else "%Y-%m-%d"
            dt = datetime.datetime.strptime(current_date_str, fmt)
            year, month, day = dt.year, dt.month, dt.day
        except:
            now = datetime.datetime.now()
            year, month, day = now.year, now.month, now.day

        cal = tkcalendar.Calendar(self.calendar_window, selectmode='day', date_pattern='dd/mm/yyyy', year=year, month=month, day=day)
        cal.pack(pady=10, padx=10, fill="both", expand=True)
        
        def set_date():
            self.inp_date.delete(0, 'end')
            self.inp_date.insert(0, cal.get_date())
            self.calendar_window.destroy()
            self.calendar_window = None
            
        btn_ok = ctk.CTkButton(self.calendar_window, text="Chọn", command=set_date, height=36, fg_color=ACCENT_BLUE, font=FONT_BUTTON)
        btn_ok.pack(pady=10)

    def on_category_select(self, value):
        """Xử lý sự kiện khi người dùng chọn một mục trong danh sách Danh mục."""
        if value == ADD_NEW_CAT_TEXT:
            self.open_category_manager()
            cats = self._get_categories()
            if cats:
                self.inp_cat.set(cats[0])

    def open_category_manager(self):
        """Khởi tạo và hiển thị cửa sổ quản lý các danh mục tùy chỉnh."""
        if self._focus_if_exists('category_window'): return
            
        self.category_window = self.create_toplevel_window("Quản lý danh mục", 400, 500)
        
        lbl_title = ctk.CTkLabel(self.category_window, text="QUẢN LÝ DANH MỤC", font=FONT_TITLE)
        lbl_title.pack(pady=(20, 10))
        
        self.cat_scroll = ctk.CTkScrollableFrame(self.category_window, fg_color="transparent")
        self.cat_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.render_category_list()
        
        add_frame = ctk.CTkFrame(self.category_window, fg_color="transparent")
        add_frame.pack(fill="x", padx=20, pady=20, side="bottom")
        
        self.inp_new_cat = ctk.CTkEntry(add_frame, placeholder_text="Tên danh mục mới...", height=36)
        self.inp_new_cat.pack(side="left", fill="x", expand=True, padx=(0,10))
        
        btn_add = ctk.CTkButton(add_frame, text="Thêm", width=60, height=36, fg_color=ACCENT_BLUE, command=self.add_new_category)
        btn_add.pack(side="left")

    def render_category_list(self):
        """Hiển thị danh sách các danh mục hiện tại để người dùng có thể chỉnh sửa/xóa."""
        for widget in self.cat_scroll.winfo_children():
            widget.destroy()
            
        cats = self._get_categories()
        if not cats and not self.controller: return
        
        for cat in cats:
            row = ctk.CTkFrame(self.cat_scroll, fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            inp = ctk.CTkEntry(row, height=32)
            inp.insert(0, cat)
            inp.pack(side="left", fill="x", expand=True, padx=(0,5))
            
            btn_save = ctk.CTkButton(row, text="Lưu", width=50, height=32, fg_color=ACCENT_GREEN, command=lambda old=cat, i=inp: self.update_category(old, i.get()))
            btn_save.pack(side="left", padx=2)
            
            btn_del = ctk.CTkButton(row, text="Xóa", width=50, height=32, fg_color=ACCENT_RED, command=lambda c=cat: self.delete_category(c))
            btn_del.pack(side="left")

    def add_new_category(self):
        """Thêm một danh mục mới vào cơ sở dữ liệu."""
        new_cat = self.inp_new_cat.get()
        if new_cat and self.controller:
            self.controller.add_category(new_cat)
            self.inp_new_cat.delete(0, 'end')
            self.render_category_list()
            self.refresh_category_dropdown()

    def update_category(self, old_name, new_name):
        """Cập nhật thay đổi tên của một danh mục."""
        if old_name != new_name and new_name and self.controller:
            self.controller.update_category(old_name, new_name)
            self.render_category_list()
            self.refresh_category_dropdown()
            
    def delete_category(self, name):
        """Xóa một danh mục khỏi hệ thống sau khi xác nhận."""
        if mb.askyesno("Xác nhận", f"Xóa danh mục '{name}'?", icon="warning"):
            if self.controller:
                self.controller.delete_category(name)
                self.render_category_list()
                self.refresh_category_dropdown()

    def refresh_category_dropdown(self):
        """Cập nhật lại danh sách danh mục trong ô chọn (dropdown) sau khi có thay đổi."""
        if getattr(self, 'inp_cat', None) and self.inp_cat.winfo_exists():
            cats = self._get_categories()
            cats.append(ADD_NEW_CAT_TEXT)
            self.inp_cat.configure(values=cats)
            val = self.inp_cat.get()
            if val not in cats:
                self.inp_cat.set(cats[0] if cats else "")
    def format_amount_input(self, event):
        """Tự động định dạng số tiền nhập vào (thêm dấu phẩy phân cách hàng nghìn)."""
        if event.keysym in ('Left', 'Right', 'Up', 'Down', 'Home', 'End'):
            return
        content = self.inp_amount.get().replace(',', '')
        if not content: return
        try:
            if '.' in content:
                parts = content.split('.')
                int_part = "{:,}".format(int(parts[0])) if parts[0] and parts[0] != '-' else parts[0]
                formatted = int_part + '.' + parts[1]
            else:
                formatted = "{:,}".format(int(content))
            
            idx = self.inp_amount.index("insert")
            old_len = len(self.inp_amount.get())
            
            self.inp_amount.delete(0, 'end')
            self.inp_amount.insert(0, formatted)
            
            new_len = len(self.inp_amount.get())
            new_idx = idx + (new_len - old_len)
            self.inp_amount.icursor(new_idx)
        except ValueError:
            pass

    def save_transaction(self):
        """Kiểm tra dữ liệu nhập vào và lưu/cập nhật thông tin giao dịch vào cơ sở dữ liệu."""
        if not self.controller: return
        date = f"{self.inp_date.get()} {self.inp_time.get()}"
        amount_str = self.inp_amount.get().replace(',', '')
        category = self.inp_cat.get()
        t_type = self.inp_type.get()
        note = self.inp_note.get()
        
        try:
            amount = float(amount_str)
        except ValueError:
            self.show_error("Lỗi", "Số tiền phải là một con số hợp lệ.")
            return
            
        if self.current_edit_id:
            self.controller.update_transaction(self.current_edit_id, date, amount, category, t_type, note)
        else:
            self.controller.add_transaction(date, amount, category, t_type, note)
        
        if getattr(self, 'transaction_window', None) and self.transaction_window.winfo_exists():
            self.transaction_window.destroy()
            self.transaction_window = None

    # --- LOADING, DASHBOARD, HELP, IMPORT/EXPORT ---
    def show_loading(self, message="Đang xử lý..."):
        """Hiển thị cửa sổ chờ (loading) khi ứng dụng đang thực hiện các tác vụ nặng."""
        for widget in self.table_scroll.winfo_children():
            widget.destroy()
        
        for _ in range(5):
            row = ctk.CTkFrame(self.table_scroll, height=40, fg_color=PANEL_BG, corner_radius=6)
            row.pack(fill="x", pady=2)
            for w in [40, 100, 150, 80]:
                ctk.CTkFrame(row, width=w, height=20, fg_color=BORDER_COLOR).pack(side="left", padx=10)
            
        if self._focus_if_exists('loading_window'): return
        self.loading_window = self.create_toplevel_window("Đang xử lý", 300, 150)
        
        lbl = ctk.CTkLabel(self.loading_window, text=message, font=FONT_TITLE)
        lbl.pack(expand=True, pady=(20, 10))
        self.progressbar = ctk.CTkProgressBar(self.loading_window, mode="indeterminate", progress_color=ACCENT_BLUE)
        self.progressbar.pack(pady=10, padx=20, fill="x")
        self.progressbar.start()

    def hide_loading(self):
        """Đóng cửa sổ chờ sau khi hoàn tất tác vụ."""
        if hasattr(self, 'loading_window') and self.loading_window and self.loading_window.winfo_exists():
            if hasattr(self, 'progressbar'):
                self.progressbar.stop()
            self.loading_window.destroy()
            self.loading_window = None
        self.render_table_page()

    def show_message(self, title, msg):
        """Hiển thị một thông báo thành công (Toast)."""
        ToastNotification(self, msg, type="info", image=self.icons.get('success')).show()
        
    def show_error(self, title, msg):
        """Hiển thị một thông báo lỗi (Toast)."""
        ToastNotification(self, msg, type="error", image=self.icons.get('error')).show()

    def show_dashboard(self):
        """Mở cửa sổ bảng điều khiển chứa các biểu đồ thống kê tài chính."""
        if self._focus_if_exists('dashboard_window'): return
            
        self.dashboard_window = self.create_toplevel_window("Thống kê", 900, 500, grab=False)
        self.dashboard_window.configure(fg_color=BG_COLOR)
        
        plt.style.use('dark_background')
        self.figure, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4))
        self.figure.patch.set_facecolor(BG_COLOR)
        
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.dashboard_window)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        if self.controller:
            self.controller.refresh_dashboard()

    def update_charts(self, category_data, trend_data):
        """Vẽ và cập nhật dữ liệu cho các biểu đồ trong bảng thống kê."""
        if not hasattr(self, 'ax1') or not hasattr(self, 'ax2'): return
        
        self.ax1.clear()
        self.ax2.clear()
        
        if not category_data.empty:
            self.ax1.pie(category_data['amount'], labels=category_data['category'], autopct='%1.1f%%', startangle=140, colors=[ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED, ACCENT_AMBER, '#8B5CF6', '#EC4899'])
            self.ax1.set_title("Cơ cấu Chi tiêu", color=TEXT_MAIN)
        else:
            self.ax1.set_title("Chưa có dữ liệu Chi tiêu", color=TEXT_MUTED)
            
        if not trend_data.empty:
            self.ax2.plot(trend_data['date'], trend_data['amount'], marker='o', label="Thực tế", color=ACCENT_BLUE)
            if 'moving_avg' in trend_data.columns and not trend_data['moving_avg'].isna().all():
                self.ax2.plot(trend_data['date'], trend_data['moving_avg'], linestyle='--', color=ACCENT_RED, label="Dự báo (MA)")
            
            self.ax2.set_title("Xu hướng & Dự báo", color=TEXT_MAIN)
            self.ax2.tick_params(axis='x', rotation=45, colors=TEXT_MUTED)
            self.ax2.tick_params(axis='y', colors=TEXT_MUTED)
            self.ax2.legend()
        else:
            self.ax2.set_title("Chưa có dữ liệu Thời gian", color=TEXT_MUTED)
            
        self.figure.tight_layout()
        self.canvas.draw()

    def show_help(self):
        """Mở cửa sổ xem tài liệu hướng dẫn sử dụng (file PDF)."""
        if self._focus_if_exists('help_window'): return
            
        self.help_window = self.create_toplevel_window("Hướng dẫn", 400, 300, grab=False)
        
        lbl_title = ctk.CTkLabel(self.help_window, text="Hướng dẫn sử dụng", font=FONT_TITLE)
        lbl_title.pack(pady=20)
        
        lbl_desc = ctk.CTkLabel(self.help_window, text="Vui lòng mở file PDF để xem chi tiết.", font=FONT_MAIN, text_color=TEXT_MUTED)
        lbl_desc.pack(pady=20)
        
        def open_pdf():
            pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'huong_dan_su_dung.pdf')
            try:
                os.startfile(os.path.abspath(pdf_path))
            except Exception as e:
                self.show_error("Lỗi", f"Không thể mở file PDF: {str(e)}")
                
        btn_open_pdf = ctk.CTkButton(self.help_window, text="Mở file PDF Hướng dẫn", font=FONT_TEXT_LARGE, fg_color=ACCENT_BLUE, command=open_pdf)
        btn_open_pdf.pack(pady=20)

    def on_import(self):
        """Hiển thị hộp thoại chọn file và thực hiện nhập dữ liệu từ file CSV."""
        if not self.controller: return
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filepath:
            self.controller.import_csv(filepath)

    def on_export(self):
        """Hiển thị hộp thoại lưu file và thực hiện xuất dữ liệu ra file CSV."""
        if not self.controller: return
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if filepath:
            self.controller.export_csv(filepath)

    # ─── BUDGET WINDOW ────────────────────────────────────────────────────────

    def show_budget_window(self):
        """Mở cửa sổ quản lý Ngân sách & Tiết kiệm."""
        if self._focus_if_exists('budget_window'): return
        self.budget_window = self.create_toplevel_window("Ngân sách & Tiết kiệm", 820, 620, grab=False)
        self.budget_window.configure(fg_color=BG_COLOR)

        # Header
        hdr = ctk.CTkFrame(self.budget_window, fg_color=PANEL_BG, corner_radius=0, height=48)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=" Ngân sách & Tiết kiệm", image=self.icons.get('dialog_budget'), compound="left", font=FONT_TITLE, text_color=TEXT_MAIN).pack(side="left", padx=20, pady=12)

        # Month selector
        now = datetime.datetime.now()
        
        # Extract unique months from existing transactions
        months_set = {now.strftime("%Y-%m")} # Always include current month
        for t in self.transactions:
            try:
                # date format in self.transactions is usually "%d/%m/%Y %H:%M" or "%d/%m/%Y"
                dt = datetime.datetime.strptime(t['date'], "%d/%m/%Y %H:%M")
                months_set.add(dt.strftime("%Y-%m"))
            except ValueError:
                try:
                    dt = datetime.datetime.strptime(t['date'], "%d/%m/%Y")
                    months_set.add(dt.strftime("%Y-%m"))
                except ValueError:
                    pass
                    
        sorted_db_months = sorted(list(months_set), reverse=True)
        months = [f"{m[5:7]}/{m[0:4]}" for m in sorted_db_months]
        
        self._budget_month = tk.StringVar(value=months[0] if months else now.strftime("%m/%Y"))
        month_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        month_frame.pack(side="right", padx=20)
        ctk.CTkLabel(month_frame, text="Tháng:", font=FONT_MAIN, text_color=TEXT_MUTED).pack(side="left", padx=(0, 6))
        
        month_opt = ctk.CTkOptionMenu(month_frame, values=months, variable=self._budget_month,
                                      width=120, height=30, font=FONT_MAIN,
                                      command=lambda _: self._budget_refresh())
        month_opt.pack(side="left")

        # Tab bar
        self._budget_tab = tk.StringVar(value="budget")
        tab_bar = ctk.CTkFrame(self.budget_window, fg_color=PANEL_BG, height=40, corner_radius=0)
        tab_bar.pack(fill="x")
        tab_bar.pack_propagate(False)
        for lbl, key, icon_key in [(" Hạn mức", "budget", "budget"), (" Cảnh báo", "alerts", "alert"), (" Tiết kiệm", "savings", "savings")]:
            b = ctk.CTkButton(tab_bar, text=lbl, image=self.icons.get(icon_key), font=FONT_BUTTON,
                              fg_color="transparent", hover_color=PANEL_BG_HOVER,
                              height=40, corner_radius=0,
                              command=lambda k=key: self._budget_switch_tab(k))
            b.pack(side="left", padx=2)
            if key == "budget":
                self._budget_tab_btns = {key: b}
            else:
                self._budget_tab_btns[key] = b

        self._budget_content = ctk.CTkFrame(self.budget_window, fg_color=BG_COLOR)
        self._budget_content.pack(fill="both", expand=True, padx=0, pady=0)

        self._budget_switch_tab("budget")

    def _budget_switch_tab(self, key):
        for k, b in self._budget_tab_btns.items():
            b.configure(fg_color=ACCENT_BLUE if k == key else "transparent")
        for w in self._budget_content.winfo_children():
            w.destroy()
        self._budget_tab.set(key)
        if key == "budget":
            self._render_budget_tab(self._budget_content)
        elif key == "alerts":
            self._render_alerts_tab(self._budget_content)
        else:
            self._render_savings_tab(self._budget_content)

    def _budget_refresh(self):
        self._budget_switch_tab(self._budget_tab.get())

    def _get_db_month(self, ui_month):
        if '/' in ui_month:
            m, y = ui_month.split('/')
            return f"{y}-{m}"
        return ui_month

    # ── TAB 1: HẠN MỨC ──────────────────────────────────────────────────────

    def _render_budget_tab(self, parent):
        month = self._budget_month.get()
        db_month = self._get_db_month(month)

        # Form thêm hạn mức
        form = ctk.CTkFrame(parent, fg_color=PANEL_BG, corner_radius=10)
        form.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(form, text="ĐẶT HẠN MỨC THÁNG", font=FONT_LABEL, text_color=TEXT_MUTED).pack(anchor="w", padx=14, pady=(10, 4))

        row1 = ctk.CTkFrame(form, fg_color="transparent")
        row1.pack(fill="x", padx=14, pady=(0, 10))

        cats = self._get_categories()
        self._bud_cat_var = tk.StringVar(value=cats[0] if cats else "")
        cat_opt = ctk.CTkOptionMenu(row1, values=cats, variable=self._bud_cat_var, width=200, height=36, font=FONT_MAIN)
        cat_opt.pack(side="left", padx=(0, 8))

        self._bud_limit_entry = ctk.CTkEntry(row1, placeholder_text="Số tiền hạn mức", width=200, height=36, font=FONT_AMOUNT)
        self._bud_limit_entry.pack(side="left", padx=(0, 8))
        self._bud_limit_entry.bind("<KeyRelease>", self._format_budget_amount)

        ctk.CTkButton(row1, text="Lưu hạn mức", fg_color=ACCENT_BLUE, height=36, width=120,
                      font=FONT_BUTTON, command=lambda: self._save_budget(month)).pack(side="left", padx=(0, 8))

        ctk.CTkButton(row1, text="Copy tháng trước", fg_color=PANEL_BG_HOVER, height=36, width=140,
                      font=FONT_BUTTON, command=lambda: self._copy_last_month(month)).pack(side="left")

        # Bảng usage
        self._render_usage_table(parent, db_month)

    def _format_budget_amount(self, event):
        if event.keysym in ('Left', 'Right', 'Home', 'End'): return
        content = self._bud_limit_entry.get().replace(',', '')
        if not content: return
        try:
            formatted = "{:,}".format(int(content))
            idx = self._bud_limit_entry.index("insert")
            old_len = len(self._bud_limit_entry.get())
            self._bud_limit_entry.delete(0, 'end')
            self._bud_limit_entry.insert(0, formatted)
            new_len = len(self._bud_limit_entry.get())
            self._bud_limit_entry.icursor(idx + (new_len - old_len))
        except ValueError:
            pass

    def _save_budget(self, month):
        if not self.controller: return
        db_month = self._get_db_month(month)
        cat = self._bud_cat_var.get()
        amt_str = self._bud_limit_entry.get().replace(',', '')
        try:
            amt = float(amt_str)
            if amt <= 0: raise ValueError
        except ValueError:
            self.show_error("Lỗi", "Hạn mức phải là số > 0")
            return

        result = self.controller.set_budget(cat, db_month, amt, overwrite=False)
        if result['status'] == 'exists':
            old_fmt = f"{result['old_limit']:,.0f} đ"
            new_fmt = f"{amt:,.0f} đ"
            if mb.askyesno("Ghi đè?",
                           f"Danh mục '{cat}' đã có hạn mức {old_fmt}.\nGhi đè bằng {new_fmt}?",
                           icon="warning"):
                self.controller.set_budget(cat, db_month, amt, overwrite=True)
                self.show_message("OK", f"Đã cập nhật hạn mức {cat}: {new_fmt}")
        elif result['status'] in ('created', 'updated'):
            self.show_message("OK", f"Đã lưu hạn mức {cat}: {amt:,.0f} đ")

        self._bud_limit_entry.delete(0, 'end')
        self._budget_refresh()

    def _copy_last_month(self, month):
        if not self.controller: return
        db_month = self._get_db_month(month)
        count = self.controller.copy_budget_from_last_month(db_month)
        if count > 0:
            self.show_message("OK", f"Đã copy {count} hạn mức từ tháng trước")
        else:
            self.show_error("Thông báo", "Không có hạn mức tháng trước để copy")
        self._budget_refresh()

    def _render_usage_table(self, parent, month):
        usage = self.controller.get_usage(month) if self.controller else []

        # Table header
        thead = ctk.CTkFrame(parent, fg_color=PANEL_BG, corner_radius=8, height=34)
        thead.pack(fill="x", padx=16, pady=(0, 2))
        thead.pack_propagate(False)
        for txt, w, anchor in [("Danh mục", 180, "w"), ("Hạn mức", 130, "e"),
                                ("Đã dùng", 130, "e"), ("Còn lại", 130, "e"),
                                ("%", 60, "center"), ("Trạng thái", 130, "w")]:
            ctk.CTkLabel(thead, text=txt, width=w, anchor=anchor,
                         font=FONT_TABLE_HEADER, text_color=TEXT_MUTED).pack(side="left", padx=5)

        scroll = ctk.CTkScrollableFrame(parent, fg_color=BG_COLOR)
        scroll.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        if not usage:
            ctk.CTkLabel(scroll, text="Chưa có hạn mức nào trong tháng này",
                         font=FONT_MAIN, text_color=TEXT_MUTED).pack(pady=30)
            return

        total_limit = total_spent = total_remaining = 0
        for row in usage:
            pct = row['pct']
            color = ACCENT_RED if pct >= 100 else (ACCENT_AMBER if pct >= 80 else ACCENT_GREEN)
            remaining_color = ACCENT_RED if row['remaining'] < 0 else TEXT_MAIN

            r = ctk.CTkFrame(scroll, fg_color="transparent", height=38)
            r.pack(fill="x")
            r.pack_propagate(False)
            sep = tk.Frame(scroll, bg=BORDER_COLOR, height=1)
            sep.pack(fill="x", padx=4)

            ctk.CTkLabel(r, text=row['category'], width=180, anchor="w", font=FONT_MAIN).pack(side="left", padx=5)
            ctk.CTkLabel(r, text=f"{row['limit']:,.0f} đ", width=130, anchor="e", font=FONT_MAIN, text_color=TEXT_MUTED).pack(side="left", padx=5)
            ctk.CTkLabel(r, text=f"{row['spent']:,.0f} đ", width=130, anchor="e", font=FONT_MAIN, text_color=color).pack(side="left", padx=5)
            ctk.CTkLabel(r, text=f"{row['remaining']:,.0f} đ", width=130, anchor="e", font=FONT_MAIN, text_color=remaining_color).pack(side="left", padx=5)

            # Progress bar
            pf = ctk.CTkFrame(r, width=60, fg_color="transparent")
            pf.pack(side="left", padx=5)
            pf.pack_propagate(False)
            ctk.CTkLabel(pf, text=f"{min(pct,999):.0f}%", font=FONT_MAIN, text_color=color, anchor="center").pack(expand=True)

            ctk.CTkLabel(r, text=row['status'], width=130, anchor="w", font=FONT_MAIN, text_color=color).pack(side="left", padx=5)

            total_limit += row['limit']
            total_spent += row['spent']
            total_remaining += row['remaining']

        # Totals row
        tk.Frame(scroll, bg=BORDER_COLOR, height=2).pack(fill="x", padx=4, pady=4)
        tot = ctk.CTkFrame(scroll, fg_color="transparent", height=36)
        tot.pack(fill="x")
        tot.pack_propagate(False)
        tot_pct = (total_spent / total_limit * 100) if total_limit else 0
        tot_color = ACCENT_RED if total_remaining < 0 else ACCENT_GREEN
        ctk.CTkLabel(tot, text="TỔNG", width=180, anchor="w", font=FONT_BUTTON, text_color=TEXT_MAIN).pack(side="left", padx=5)
        ctk.CTkLabel(tot, text=f"{total_limit:,.0f} đ", width=130, anchor="e", font=FONT_BUTTON, text_color=TEXT_MUTED).pack(side="left", padx=5)
        ctk.CTkLabel(tot, text=f"{total_spent:,.0f} đ", width=130, anchor="e", font=FONT_BUTTON, text_color=ACCENT_RED).pack(side="left", padx=5)
        ctk.CTkLabel(tot, text=f"{total_remaining:,.0f} đ", width=130, anchor="e", font=FONT_BUTTON, text_color=tot_color).pack(side="left", padx=5)
        ctk.CTkLabel(tot, text=f"{tot_pct:.0f}%", width=60, anchor="center", font=FONT_BUTTON, text_color=tot_color).pack(side="left", padx=5)

    # ── TAB 2: CẢNH BÁO ─────────────────────────────────────────────────────

    def _render_alerts_tab(self, parent):
        month = self._budget_month.get()
        db_month = self._get_db_month(month)
        alerts = self.controller.check_alerts(db_month) if self.controller else []

        card = ctk.CTkFrame(parent, fg_color=PANEL_BG, corner_radius=12)
        card.pack(fill="x", padx=16, pady=12)

        hdr_txt = f" CẢNH BÁO – Tháng {month}"
        ctk.CTkLabel(card, text=hdr_txt, image=self.icons.get('alert'), compound="left", font=FONT_TITLE, text_color=TEXT_MAIN).pack(anchor="w", padx=16, pady=(12, 4))

        sep = tk.Frame(card, bg=BORDER_COLOR, height=1)
        sep.pack(fill="x", padx=16)

        scroll = ctk.CTkScrollableFrame(parent, fg_color=BG_COLOR)
        scroll.pack(fill="both", expand=True, padx=16, pady=8)

        if not alerts:
            ctk.CTkLabel(scroll, text=" Tất cả danh mục đều an toàn trong tháng này!", image=self.icons.get('safe'), compound="left",
                         font=FONT_TEXT_LARGE, text_color=ACCENT_GREEN).pack(pady=40)
            return

        for a in alerts:
            pct = a['pct']
            if pct >= 100:
                icon_txt = " VƯỢT HẠN"
                icon_img = self.icons.get('danger')
                color = ACCENT_RED
                detail = f"→ Vượt {abs(a['remaining']):,.0f} ₫ so với hạn mức"
            else:
                icon_txt = " SẮP VƯỢT"
                icon_img = self.icons.get('warning')
                color = ACCENT_AMBER
                detail = f"→ Còn lại {a['remaining']:,.0f} ₫"

            row = ctk.CTkFrame(scroll, fg_color=PANEL_BG, corner_radius=8)
            row.pack(fill="x", pady=4)

            top = ctk.CTkFrame(row, fg_color="transparent")
            top.pack(fill="x", padx=14, pady=(10, 2))
            ctk.CTkLabel(top, text=f"{icon_txt}  [{a['category']}]: {pct:.1f}%", image=icon_img, compound="left",
                         font=FONT_BUTTON, text_color=color).pack(side="left")

            ctk.CTkLabel(row, text=detail, font=FONT_MAIN, text_color=TEXT_MUTED).pack(anchor="w", padx=28, pady=(0, 10))

            # Mini progress bar
            bar_frame = ctk.CTkFrame(row, fg_color="transparent")
            bar_frame.pack(fill="x", padx=14, pady=(0, 10))
            prog = ctk.CTkProgressBar(bar_frame, height=8, corner_radius=4,
                                      fg_color=BORDER_COLOR, progress_color=color)
            prog.pack(fill="x")
            prog.set(min(pct / 100, 1.0))

        ctk.CTkButton(scroll, text="Kiểm tra lại", fg_color=ACCENT_BLUE, height=36,
                      font=FONT_BUTTON, command=self._budget_refresh).pack(pady=12)

    # ── TAB 3: TIẾT KIỆM ────────────────────────────────────────────────────

    def _render_savings_tab(self, parent):
        month = self._budget_month.get()
        db_month = self._get_db_month(month)
        progress = self.controller.get_savings_progress(db_month) if self.controller else {}

        # Goal form
        form = ctk.CTkFrame(parent, fg_color=PANEL_BG, corner_radius=10)
        form.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(form, text="MỤC TIÊU TIẾT KIỆM THÁNG", font=FONT_LABEL, text_color=TEXT_MUTED).pack(anchor="w", padx=14, pady=(10, 4))
        frow = ctk.CTkFrame(form, fg_color="transparent")
        frow.pack(fill="x", padx=14, pady=(0, 12))

        self._sav_entry = ctk.CTkEntry(frow, placeholder_text="Nhập mục tiêu tiết kiệm", width=240, height=36, font=FONT_AMOUNT)
        self._sav_entry.pack(side="left", padx=(0, 8))
        self._sav_entry.bind("<KeyRelease>", self._format_savings_amount)

        current_goal = progress.get('goal', 0)
        if current_goal > 0:
            self._sav_entry.insert(0, f"{current_goal:,.0f}")

        ctk.CTkButton(frow, text="Lưu mục tiêu", fg_color=ACCENT_BLUE, height=36, width=130,
                      font=FONT_BUTTON, command=lambda: self._save_savings_goal(month)).pack(side="left")

        # Progress display
        if progress:
            card = ctk.CTkFrame(parent, fg_color=PANEL_BG, corner_radius=12)
            card.pack(fill="x", padx=16, pady=4)

            status = progress.get('status', '')
            if '🎉' in status or 'Đạt' in status: status_color = ACCENT_GREEN
            elif '❌' in status or 'vượt' in status: status_color = ACCENT_RED
            elif '📈' in status or 'còn' in status: status_color = ACCENT_AMBER
            else: status_color = TEXT_MUTED

            ctk.CTkLabel(card, text=f" TIẾN ĐỘ TIẾT KIỆM – Tháng {month}", image=self.icons.get('savings'), compound="left",
                         font=FONT_TITLE, text_color=TEXT_MAIN).pack(anchor="w", padx=16, pady=(12, 4))
            tk.Frame(card, bg=BORDER_COLOR, height=1).pack(fill="x", padx=16)

            rows_data = [
                ("Tổng thu", f"{progress.get('total_income', 0):,.0f} ₫", ACCENT_GREEN),
                ("Tổng chi", f"{progress.get('total_expense', 0):,.0f} ₫", ACCENT_RED),
                ("Tiết kiệm thực", f"{progress.get('actual_saving', 0):,.0f} ₫", TEXT_MAIN),
                ("Mục tiêu", f"{progress.get('goal', 0):,.0f} ₫", TEXT_MUTED),
            ]
            for label, value, color in rows_data:
                r = ctk.CTkFrame(card, fg_color="transparent")
                r.pack(fill="x", padx=16, pady=3)
                ctk.CTkLabel(r, text=label, font=FONT_MAIN, text_color=TEXT_MUTED, width=180, anchor="w").pack(side="left")
                ctk.CTkLabel(r, text=value, font=FONT_AMOUNT, text_color=color).pack(side="left")

            tk.Frame(card, bg=BORDER_COLOR, height=1).pack(fill="x", padx=16, pady=6)

            # Status line
            goal = progress.get('goal', 0)
            actual = progress.get('actual_saving', 0)
            pct = progress.get('pct_achieved', 0)
            icon_img = None
            if goal > 0 and actual >= goal:
                status_txt = f" Đạt mục tiêu! ({pct:.1f}% — vượt {progress.get('gap', 0):,.0f} ₫)"
                icon_img = self.icons.get('success')
            elif goal > 0 and actual > 0:
                status_txt = f" {pct:.1f}% — còn thiếu {abs(progress.get('gap', 0)):,.0f} ₫"
                icon_img = self.icons.get('stats')
            elif actual <= 0:
                status_txt = " Chi vượt thu — không đạt mục tiêu"
                icon_img = self.icons.get('error')
            else:
                status_txt = " Chưa đặt mục tiêu tiết kiệm"
                icon_img = self.icons.get('warning')

            ctk.CTkLabel(card, text=status_txt, image=icon_img, compound="left", font=FONT_BUTTON, text_color=status_color).pack(anchor="w", padx=16, pady=(0, 8))

            # Progress bar (chỉ khi có goal)
            if goal > 0:
                bar_frame = ctk.CTkFrame(card, fg_color="transparent")
                bar_frame.pack(fill="x", padx=16, pady=(0, 14))
                prog = ctk.CTkProgressBar(bar_frame, height=12, corner_radius=6,
                                          fg_color=BORDER_COLOR, progress_color=status_color)
                prog.pack(fill="x")
                prog.set(min(max(actual / goal, 0), 1.0))

    def _format_savings_amount(self, event):
        if event.keysym in ('Left', 'Right', 'Home', 'End'): return
        content = self._sav_entry.get().replace(',', '')
        if not content: return
        try:
            formatted = "{:,}".format(int(content))
            idx = self._sav_entry.index("insert")
            old_len = len(self._sav_entry.get())
            self._sav_entry.delete(0, 'end')
            self._sav_entry.insert(0, formatted)
            new_len = len(self._sav_entry.get())
            self._sav_entry.icursor(idx + (new_len - old_len))
        except ValueError:
            pass

    def _save_savings_goal(self, month):
        if not self.controller: return
        db_month = self._get_db_month(month)
        amt_str = self._sav_entry.get().replace(',', '')
        try:
            amt = float(amt_str)
            if amt < 0: raise ValueError
        except ValueError:
            self.show_error("Lỗi", "Mục tiêu phải là số >= 0")
            return
        self.controller.set_savings_goal(db_month, amt)
        self.show_message("OK", f"Đã lưu mục tiêu tiết kiệm: {amt:,.0f} ₫")
        self._budget_refresh()

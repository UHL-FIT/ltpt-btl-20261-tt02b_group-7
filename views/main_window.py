import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog
import tkinter.messagebox as mb
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import os
import threading
from PIL import Image, ImageTk

# --- CONSTANTS ---
TX_TYPE_EXPENSE_VN = "Chi tiêu"
TX_TYPE_INCOME_VN = "Thu nhập"
ADD_NEW_CAT_TEXT = "Thêm mới..."

# --- COLORS & FONTS ---
BG_COLOR = "#0F172A"
PANEL_BG = "#1E293B"
PANEL_BG_HOVER = "#334155"
ACCENT_BLUE = "#3B82F6"
ACCENT_GREEN = "#10B981"
ACCENT_RED = "#EF4444"
ACCENT_AMBER = "#F59E0B"
TEXT_MAIN = "#F8FAFC"
TEXT_MUTED = "#94A3B8"
BORDER_COLOR = "#334155"

FONT_MAIN = ("Inter", 13)
FONT_TITLE = ("Inter", 16, "bold")
FONT_LABEL = ("Inter", 11, "bold")
FONT_AMOUNT = ("Consolas", 14, "bold")
FONT_SUMMARY = ("Inter", 20, "bold")

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
        self.geometry("1200x800")
        self.configure(fg_color=BG_COLOR)
        ctk.set_appearance_mode("dark")
        
        self.controller = None
        self.dashboard_window = None
        self.help_window = None
        self.loading_window = None
        
        self.transactions = []
        self.filtered_transactions = []
        self.current_page = 1
        self.rows_per_page = 15
        
        self.selected_row_ids = set()
        
        self.load_icons()
        
        self.setup_ui()
        self.bind_shortcuts()

    def load_icons(self):
        """Tải các biểu tượng icon từ thư mục assets."""
        icon_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icons")
        self.icons = {}
        self.tk_icons = {}
        icon_names = ['import', 'export', 'stats', 'help', 'edit', 'delete', 'add', 'search', 'tx', 'exp', 'inc', 'net', 'success', 'error', 'money', 'empty', 'copy']
        for name in icon_names:
            path = os.path.join(icon_dir, f"{name}.png")
            if os.path.exists(path):
                img = Image.open(path)
                self.icons[name] = ctk.CTkImage(light_image=img, dark_image=img, size=(20, 20))
                self.tk_icons[name] = ImageTk.PhotoImage(img.resize((16, 16)))
        
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
        
        self.transaction_window = None
        self.category_window = None

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
        ctk.CTkLabel(left_frame, text="", image=self.icons.get('money')).pack(side="left", padx=(0,10))
        ctk.CTkLabel(left_frame, text="Quản Lý Chi Tiêu Cá Nhân", font=FONT_TITLE, text_color=TEXT_MAIN).pack(side="left")
        
        center_frame = ctk.CTkFrame(self.topbar, fg_color="transparent")
        center_frame.grid(row=0, column=1, pady=8)
        self.entry_search = ctk.CTkEntry(center_frame, placeholder_text="Tìm kiếm giao dịch...", 
                                         width=400, height=32, corner_radius=16, border_width=1, fg_color=BG_COLOR, border_color=BORDER_COLOR)
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<KeyRelease>", self.on_search_typing)
        
        right_frame = ctk.CTkFrame(self.topbar, fg_color="transparent")
        right_frame.grid(row=0, column=2, padx=20, sticky="e")
        
        # Nút Import: Nhập dữ liệu giao dịch từ file CSV vào ứng dụng
        btn_import = ctk.CTkButton(right_frame, text=" Nhập CSV", image=self.icons.get('import'), height=36, fg_color="transparent", hover_color=PANEL_BG_HOVER, command=self.on_import)
        btn_import.pack(side="left", padx=2)
        # Nút Export: Xuất dữ liệu giao dịch hiện tại ra file CSV
        btn_export = ctk.CTkButton(right_frame, text=" Xuất CSV", image=self.icons.get('export'), height=36, fg_color="transparent", hover_color=PANEL_BG_HOVER, command=self.on_export)
        btn_export.pack(side="left", padx=2)
        # Nút Thống kê: Mở Dashboard xem các biểu đồ phân tích (Pie chart, Line chart)
        btn_stats = ctk.CTkButton(right_frame, text=" Thống kê", image=self.icons.get('stats'), height=36, fg_color="transparent", hover_color=PANEL_BG_HOVER, command=self.show_dashboard)
        btn_stats.pack(side="left", padx=2)
        # Nút Hướng dẫn: Mở bảng hướng dẫn để xem file PDF
        btn_help = ctk.CTkButton(right_frame, text=" Hướng dẫn", image=self.icons.get('help'), height=36, fg_color="transparent", hover_color=PANEL_BG_HOVER, command=self.show_help)
        btn_help.pack(side="left", padx=2)

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
        btn_add = ctk.CTkButton(self.action_bar, text=" Thêm giao dịch", image=self.icons.get('add'), fg_color=ACCENT_BLUE, font=("Inter", 13, "bold"), corner_radius=16, height=36, command=self.toggle_drawer)
        btn_add.pack(side="left")

    def setup_main_table(self):
        """Khởi tạo cấu trúc bảng hiển thị danh sách giao dịch."""
        self.table_container = ctk.CTkFrame(self, fg_color="transparent")
        self.table_container.grid(row=3, column=0, sticky="nsew", padx=20, pady=0)
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(1, weight=1)
        
        header_frame = ctk.CTkFrame(self.table_container, height=36, fg_color=PANEL_BG, corner_radius=8)
        header_frame.grid(row=0, column=0, sticky="ew")
        
        self.cols = [("☐", 40), ("#", 40), ("Thời gian", 120), ("Danh mục", 150), ("Loại", 100), ("Số tiền", 120), ("Ghi chú", 200), ("Thao tác", 80)]
        for text, width in self.cols:
            anchor = "e" if text == "Số tiền" else "w"
            if text in ["☐", "#", "Thao tác"]: anchor = "center"
            lbl = ctk.CTkLabel(header_frame, text=text, font=("Inter", 14, "bold"), text_color=TEXT_MUTED, width=width, anchor=anchor)
            lbl.pack(side="left", padx=5)
            
        self.table_scroll = ctk.CTkScrollableFrame(self.table_container, fg_color="transparent")
        self.table_scroll.grid(row=1, column=0, sticky="nsew", pady=(5,0))

    def setup_bottom_bar(self):
        """Khởi tạo thanh điều hướng phân trang và các nút thao tác hàng loạt (bulk actions) ở dưới cùng."""
        self.bottom_bar = ctk.CTkFrame(self, height=56, fg_color=PANEL_BG, corner_radius=12)
        self.bottom_bar.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        self.bottom_bar.grid_columnconfigure(0, weight=1)
        
        self.bulk_frame = ctk.CTkFrame(self.bottom_bar, fg_color="transparent")
        self.bulk_frame.grid(row=0, column=0, sticky="w", padx=10)
        # Nút Xóa nhiều: Xóa tất cả các hàng đang được chọn (tick ô vuông)
        self.btn_bulk_del = ctk.CTkButton(self.bulk_frame, text=" Xoá đã chọn", image=self.icons.get('delete'), fg_color=ACCENT_RED, width=150, height=32, command=self.on_delete_selected)
        self.btn_bulk_del.pack(side="left", padx=5)
        # Nút Xuất nhiều: Xuất riêng những hàng đang được chọn ra file CSV
        self.btn_bulk_exp = ctk.CTkButton(self.bulk_frame, text=" Xuất đã chọn", image=self.icons.get('export'), fg_color=PANEL_BG_HOVER, width=150, height=32, command=self.on_export_selected)
        self.btn_bulk_exp.pack(side="left", padx=5)
        self.bulk_frame.grid_remove()
        
        right_frame = ctk.CTkFrame(self.bottom_bar, fg_color="transparent")
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
        # Nhãn hiển thị tiến độ phân trang
        self.lbl_page = ctk.CTkLabel(right_frame, text="Trang 1/1", font=FONT_MAIN)
        self.lbl_page.pack(side="left", padx=10)
        
        # Nút Lùi trang: Trở về trang chứa các giao dịch mới hơn
        btn_prev = ctk.CTkButton(right_frame, text="<", width=30, height=30, fg_color=PANEL_BG_HOVER, command=self.prev_page)
        btn_prev.pack(side="left", padx=2)
        # Nút Tới trang: Sang trang chứa các giao dịch cũ hơn
        btn_next = ctk.CTkButton(right_frame, text=">", width=30, height=30, fg_color=PANEL_BG_HOVER, command=self.next_page)
        btn_next.pack(side="left", padx=2)

    def bind_shortcuts(self):
        """Đăng ký các phím tắt cho ứng dụng (Ctrl+N, Ctrl+F, Delete)."""
        self.bind("<Control-n>", lambda e: self.toggle_drawer())
        self.bind("<Control-f>", lambda e: self.entry_search.focus())
        self.bind("<Delete>", lambda e: self.on_delete_selected())

    # --- ACTIONS & LOGIC ---

    def on_search_typing(self, event):
        self.filtered_transactions = self.transactions
        self.current_page = 1
        self.render_table_page()


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
        self.on_search_typing(None) 
        
        total_tx = len(self.transactions)
        total_inc = sum(float(t['amount']) for t in self.transactions if t['type'] == TX_TYPE_INCOME_VN)
        total_exp = sum(float(t['amount']) for t in self.transactions if t['type'] == TX_TYPE_EXPENSE_VN)
        net = total_inc - total_exp
        
        self.card_tx.configure(text=str(total_tx))
        self.card_exp.configure(text=f"{total_exp:,.0f} đ")
        self.card_inc.configure(text=f"{total_inc:,.0f} đ")
        self.card_net.configure(text=f"{net:,.0f} đ", text_color=ACCENT_GREEN if net >= 0 else ACCENT_RED)

    def render_table_page(self):
        """Hiển thị dữ liệu các giao dịch lên bảng theo trang hiện tại."""
        for widget in self.table_scroll.winfo_children():
            widget.destroy()
            
        if not self.filtered_transactions:
            ctk.CTkLabel(self.table_scroll, text=" Không tìm thấy giao dịch nào", image=self.icons.get('empty'), compound="left", font=FONT_TITLE, text_color=TEXT_MUTED).pack(pady=50)
            self.lbl_page.configure(text="Trang 1/1")
            return
            
        start_idx = (self.current_page - 1) * self.rows_per_page
        end_idx = start_idx + self.rows_per_page
        page_data = self.filtered_transactions[start_idx:end_idx]
        
        total_pages = max(1, (len(self.filtered_transactions) + self.rows_per_page - 1) // self.rows_per_page)
        self.lbl_page.configure(text=f"Trang {self.current_page}/{total_pages}")
        
        for idx, t in enumerate(page_data):
            self.create_table_row(t, start_idx + idx)
            
        self.update_bulk_actions_visibility()

    def create_table_row(self, t, index):
        """Tạo một hàng dữ liệu cho một giao dịch cụ thể trong bảng."""
        bg_color = PANEL_BG if index % 2 == 0 else "transparent"
        row = ctk.CTkFrame(self.table_scroll, height=40, fg_color=bg_color, corner_radius=6)
        row.pack(fill="x", pady=1)
        row.pack_propagate(False)
        
        action_frame = ctk.CTkFrame(row, fg_color="transparent", width=80)
        
        def on_enter(e, r=row, af=action_frame):
            r.configure(fg_color=PANEL_BG_HOVER)
            
        def on_leave(e, r=row, orig=bg_color, af=action_frame):
            if t['id'] not in self.selected_row_ids:
                r.configure(fg_color=orig)
            else:
                r.configure(fg_color="#1E3A8A")
            
        chk_var = tk.BooleanVar(value=t['id'] in self.selected_row_ids)
        chk = ctk.CTkCheckBox(row, text="", variable=chk_var, width=40, command=lambda id=t['id'], v=chk_var: self.toggle_row_selection(id, v.get()))
        chk.pack(side="left", padx=(10,0))
        
        ctk.CTkLabel(row, text=str(t['id']), width=40, anchor="center", font=FONT_MAIN, text_color=TEXT_MUTED).pack(side="left", padx=5)
        
        date_str = str(t['date'])
        if " " not in date_str: date_str += " 00:00"
        ctk.CTkLabel(row, text=date_str, width=120, anchor="w", font=FONT_MAIN).pack(side="left", padx=5)
        
        ctk.CTkLabel(row, text=t['category'], width=150, anchor="w", font=FONT_MAIN).pack(side="left", padx=5)
        
        type_color = ACCENT_RED if t['type'] == TX_TYPE_EXPENSE_VN else ACCENT_GREEN
        display_type = t['type']
        badge = ctk.CTkFrame(row, fg_color=type_color, corner_radius=10, width=80, height=24)
        badge.pack_propagate(False)
        badge.pack(side="left", padx=10, pady=8)
        ctk.CTkLabel(badge, text=display_type, font=("Inter", 10, "bold"), text_color="white").pack(expand=True)
        
        amt_str = f"{float(t['amount']):,.0f} đ"
        ctk.CTkLabel(row, text=amt_str, width=120, anchor="e", font=FONT_AMOUNT, text_color=type_color).pack(side="left", padx=5)
        
        ctk.CTkLabel(row, text=str(t['note'])[:30], width=200, anchor="w", font=FONT_MAIN, text_color=TEXT_MUTED).pack(side="left", padx=5)
        
        action_frame.pack(side="left", padx=5)
        # Nút Sửa (Icon Edit): Sẽ trượt mở Side Drawer với các thông tin đã điền sẵn để người dùng chỉnh sửa
        btn_edit = ctk.CTkButton(action_frame, text="", image=self.icons.get('edit'), width=30, height=30, fg_color="transparent", hover_color=ACCENT_BLUE, command=lambda t=t: self.open_edit_drawer(t))
        btn_edit.pack(side="left", padx=2)
        # Nút Xóa (Icon Xóa): Mở cảnh báo, sau khi xác nhận thì xóa ngay giao dịch này
        btn_del = ctk.CTkButton(action_frame, text="", image=self.icons.get('delete'), width=30, height=30, fg_color="transparent", hover_color=ACCENT_RED, command=lambda t=t: self.delete_single_transaction(t))
        btn_del.pack(side="left", padx=2)

        row.bind("<Enter>", on_enter)
        row.bind("<Leave>", on_leave)
        for child in row.winfo_children():
            child.bind("<Button-3>", lambda e, t=t: self.show_context_menu(e, t))
            if not isinstance(child, ctk.CTkButton) and not isinstance(child, ctk.CTkCheckBox):
                child.bind("<Button-1>", lambda e, id=t['id'], v=chk_var: self.toggle_row_selection(id, not v.get()))

    def toggle_row_selection(self, t_id, state):
        """Xử lý thao tác chọn/bỏ chọn một giao dịch bằng ô checkbox."""
        if state:
            self.selected_row_ids.add(t_id)
        else:
            self.selected_row_ids.discard(t_id)
        self.update_bulk_actions_visibility()
        self.render_table_page() 

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

    def show_context_menu(self, event, t):
        """Hiển thị menu ngữ cảnh (chuột phải) cho một dòng giao dịch."""
        menu = tk.Menu(self, tearoff=0, bg=PANEL_BG, fg=TEXT_MAIN, activebackground=ACCENT_BLUE)
        menu.add_command(label=" Sửa", image=self.tk_icons.get('edit'), compound="left", command=lambda: self.open_edit_drawer(t))
        menu.add_command(label=" Xóa", image=self.tk_icons.get('delete'), compound="left", command=lambda: self.delete_single_transaction(t))
        menu.add_command(label=" Nhân bản", image=self.tk_icons.get('copy'), compound="left", command=lambda: self.duplicate_transaction(t))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def duplicate_transaction(self, t):
        pass

    def delete_single_transaction(self, t):
        if mb.askyesno("Xác nhận", f"Xóa giao dịch này?"):
            self.controller.delete_transactions([t['id']])

    def on_delete_selected(self):
        if not self.selected_row_ids: return
        if mb.askyesno("Xác nhận", f"Xóa {len(self.selected_row_ids)} giao dịch đã chọn?"):
            self.controller.delete_transactions(list(self.selected_row_ids))
            self.selected_row_ids.clear()

    def on_export_selected(self):
        pass

    def toggle_drawer(self):
        """Mở cửa sổ thêm giao dịch mới."""
        self.open_transaction_window()

    def open_transaction_window(self, edit_t=None):
        """Khởi tạo và hiển thị cửa sổ con để Thêm hoặc Sửa thông tin giao dịch."""
        if self._focus_if_exists('transaction_window'): return
            
        title = "Giao dịch mới" if not edit_t else "Sửa giao dịch"
        self.transaction_window = self.create_toplevel_window(title, 400, 550)
        
        self.current_edit_id = edit_t['id'] if edit_t else None
        
        form = ctk.CTkScrollableFrame(self.transaction_window, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=20)
        
        self._create_form_label(form, "THỜI GIAN", top_pady=10)
        self.inp_date = ctk.CTkEntry(form, placeholder_text="DD/MM/YYYY HH:MM", height=36)
        self.inp_date.pack(fill="x")
        self.inp_date.insert(0, edit_t['date'] if edit_t else datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
        
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
        
        btn_confirm = ctk.CTkButton(self.transaction_window, text="Xác nhận", fg_color=ACCENT_BLUE, height=48, font=("Inter", 14, "bold"), command=self.save_transaction)
        btn_confirm.pack(fill="x", padx=20, pady=20, side="bottom")
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
        pass
            
    def delete_category(self, name):
        pass

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

    def open_edit_drawer(self, t):
        """Mở cửa sổ và điền sẵn thông tin để chỉnh sửa giao dịch hiện tại."""
        self.open_transaction_window(edit_t=t)

    def save_transaction(self):
        """Kiểm tra dữ liệu nhập vào và lưu/cập nhật thông tin giao dịch vào cơ sở dữ liệu."""
        if not self.controller: return
        date = self.inp_date.get()
        amount_str = self.inp_amount.get().replace(',', '')
        category = self.inp_cat.get()
        t_type = self.inp_type.get()
        note = self.inp_note.get()
        
        try:
            amount = float(amount_str)
        except ValueError:
            self.show_error("Lỗi", "Số tiền phải là một con số hợp lệ.")
            return
            
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
            ctk.CTkFrame(row, width=40, height=20, fg_color=BORDER_COLOR).pack(side="left", padx=10)
            ctk.CTkFrame(row, width=100, height=20, fg_color=BORDER_COLOR).pack(side="left", padx=10)
            ctk.CTkFrame(row, width=150, height=20, fg_color=BORDER_COLOR).pack(side="left", padx=10)
            ctk.CTkFrame(row, width=80, height=20, fg_color=BORDER_COLOR).pack(side="left", padx=10)
            
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
        pass

    def update_charts(self, category_data, trend_data):
        pass

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
                
        btn_open_pdf = ctk.CTkButton(self.help_window, text="Mở file PDF Hướng dẫn", font=("Inter", 14), fg_color=ACCENT_BLUE, command=open_pdf)
        btn_open_pdf.pack(pady=20)

    def on_import(self):
        pass

    def on_export(self):
        pass

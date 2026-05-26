# Nhập các thư viện giao diện người dùng
import tkinter as tk
import customtkinter as ctk
from views.core.theme_styles import *
from views.core.ui_decorators import safe_execution

# Khai báo lớp FilterWindow hiển thị giao diện lọc dữ liệu nâng cao
class FilterWindow(ctk.CTkToplevel):
    # Khởi tạo cửa sổ lọc dữ liệu
    def __init__(self, master, icons, **kwargs):
        """
        Cửa sổ cấu hình lọc dữ liệu cao cấp giúp tinh chỉnh chi tiết kết quả truy vấn giao dịch.
        """
        super().__init__(master, **kwargs)
        self.main_app = master
        self.icons = icons
        
        self.title("Lọc giao dịch")
        self.geometry("550x400")
        self.transient(master)
        self.grab_set()
        self.configure(fg_color=PANEL_BG)
        
        # Căn giữa hộp thoại so với cửa sổ cha
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (550 // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (400 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.temp_filter_categories = list(master.filter_categories)
        self.cat_dropdown_window = None
        
        self.setup_ui()

    # Bố trí các phần tử giao diện người dùng
    def setup_ui(self):
        # Tiêu đề
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(hdr, text="Bộ lọc", font=FONT_TITLE, text_color=TEXT_MAIN).pack(side="left")
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20)
        
        def create_row(label_text):
            row = ctk.CTkFrame(content, fg_color="transparent")
            row.pack(fill="x", pady=8)
            lbl = ctk.CTkLabel(row, text=label_text, width=120, anchor="w", font=FONT_MAIN, text_color=TEXT_MUTED)
            lbl.pack(side="left")
            return row
            
        # Dòng chọn Danh mục
        row_cat = create_row("Danh mục")
        btn_text = "Tất cả" if not self.temp_filter_categories else ", ".join(self.temp_filter_categories)
        if len(btn_text) > 30: btn_text = btn_text[:27] + "..."
        
        self.cat_button = ctk.CTkButton(
            row_cat, text=btn_text, height=36, font=FONT_MAIN, 
            fg_color=BG_COLOR, hover_color=PANEL_BG_HOVER, anchor="w", 
            text_color=TEXT_MAIN, command=self.show_cat_dropdown
        )
        self.cat_button.pack(side="left", fill="x", expand=True)
        
        # Dòng chọn Loại giao dịch
        row_type = create_row("Loại")
        self.cb_filter_type = ctk.CTkOptionMenu(
            row_type, values=["Tất cả", TX_TYPE_EXPENSE_VN, TX_TYPE_INCOME_VN], 
            height=36, font=FONT_MAIN, fg_color=BG_COLOR, 
            button_color=BG_COLOR, button_hover_color=PANEL_BG_HOVER
        )
        self.cb_filter_type.pack(side="left", fill="x", expand=True)
        self.cb_filter_type.set(self.main_app.filter_type)
        
        # Dòng lọc Số tiền
        row_amt = create_row("Số tiền")
        self.entry_min_amt = ctk.CTkEntry(row_amt, placeholder_text="Từ (đ)", height=36, font=FONT_MAIN, fg_color=BG_COLOR, border_color=BORDER_COLOR)
        self.entry_min_amt.pack(side="left", fill="x", expand=True)
        self.entry_min_amt.insert(0, self.main_app.filter_min_amt)
        ctk.CTkLabel(row_amt, text=" - ", font=FONT_MAIN).pack(side="left", padx=5)
        self.entry_max_amt = ctk.CTkEntry(row_amt, placeholder_text="Đến (đ)", height=36, font=FONT_MAIN, fg_color=BG_COLOR, border_color=BORDER_COLOR)
        self.entry_max_amt.pack(side="left", fill="x", expand=True)
        self.entry_max_amt.insert(0, self.main_app.filter_max_amt)
        
        # Dòng lọc Thời gian
        row_date = create_row("Thời gian")
        self.entry_min_date = ctk.CTkEntry(row_date, placeholder_text="Từ (DD/MM/YYYY)", height=36, font=FONT_MAIN, fg_color=BG_COLOR, border_color=BORDER_COLOR)
        self.entry_min_date.pack(side="left", fill="x", expand=True)
        self.entry_min_date.insert(0, self.main_app.filter_min_date)
        ctk.CTkLabel(row_date, text=" - ", font=FONT_MAIN).pack(side="left", padx=5)
        self.entry_max_date = ctk.CTkEntry(row_date, placeholder_text="Đến (DD/MM/YYYY)", height=36, font=FONT_MAIN, fg_color=BG_COLOR, border_color=BORDER_COLOR)
        self.entry_max_date.pack(side="left", fill="x", expand=True)
        self.entry_max_date.insert(0, self.main_app.filter_max_date)
        
        # Các nút chức năng chân trang
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=20, side="bottom")
        
        btn_reset = ctk.CTkButton(footer, text="Đặt lại", width=100, height=40, fg_color="transparent", hover_color=PANEL_BG_HOVER, font=FONT_BUTTON, command=self.reset_filters)
        btn_reset.pack(side="left")
        
        btn_apply = ctk.CTkButton(footer, text="Áp dụng", width=100, height=40, fg_color="#3B82F6", hover_color="#2563EB", font=FONT_BUTTON, command=self.save_filters)
        btn_apply.pack(side="right")

    # Đặt lại toàn bộ các bộ lọc về mặc định ban đầu
    @safe_execution("Lỗi đặt lại bộ lọc")
    def reset_filters(self):
        self.temp_filter_categories.clear()
        self.cat_button.configure(text="Tất cả")
        self.cb_filter_type.set("Tất cả")
        self.entry_min_amt.delete(0, "end")
        self.entry_max_amt.delete(0, "end")
        self.entry_min_date.delete(0, "end")
        self.entry_max_date.delete(0, "end")
        if self.cat_dropdown_window and self.cat_dropdown_window.winfo_exists():
            self.cat_dropdown_window.destroy()

    # Áp dụng các điều kiện lọc và đóng cửa sổ
    @safe_execution("Lỗi áp dụng bộ lọc")
    def save_filters(self):
        self.main_app.filter_categories = list(self.temp_filter_categories)
        self.main_app.filter_type = self.cb_filter_type.get()
        self.main_app.filter_min_amt = self.entry_min_amt.get().strip()
        self.main_app.filter_max_amt = self.entry_max_amt.get().strip()
        self.main_app.filter_min_date = self.entry_min_date.get().strip()
        self.main_app.filter_max_date = self.entry_max_date.get().strip()
        self.destroy()
        self.main_app.apply_filters()

    # Hiển thị trình thả xuống đa chọn danh mục
    @safe_execution("Lỗi mở danh mục lọc")
    def show_cat_dropdown(self):
        if self.cat_dropdown_window and self.cat_dropdown_window.winfo_exists():
            self.cat_dropdown_window.destroy()
            return
            
        scaling = self._get_window_scaling()
        x = (self.cat_button.winfo_rootx() - self.winfo_rootx()) / scaling
        y = (self.cat_button.winfo_rooty() - self.winfo_rooty() + self.cat_button.winfo_height()) / scaling
        width = self.cat_button.winfo_width() / scaling
        
        self.cat_dropdown_window = ctk.CTkFrame(self, fg_color=BORDER_COLOR, corner_radius=4, border_width=1, width=width, height=220)
        self.cat_dropdown_window.place(x=x, y=y)
        self.cat_dropdown_window.lift()
        
        frame = ctk.CTkFrame(self.cat_dropdown_window, fg_color=BG_COLOR, corner_radius=0)
        frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        scroll = ctk.CTkScrollableFrame(frame, fg_color=BG_COLOR, corner_radius=0)
        scroll.pack(fill="both", expand=True)
        
        cats = self.main_app._get_categories()
        self.cat_vars = {}
        
        all_var = tk.BooleanVar(value=not bool(self.temp_filter_categories))
        
        def update_button_text():
            if not self.temp_filter_categories:
                self.cat_button.configure(text="Tất cả")
            else:
                text = ", ".join(self.temp_filter_categories)
                if len(text) > 30:
                    text = text[:27] + "..."
                self.cat_button.configure(text=text)
        
        def on_all():
            if all_var.get():
                self.temp_filter_categories.clear()
                for v in self.cat_vars.values():
                    v.set(False)
            else:
                all_var.set(True)
            update_button_text()
            
        def on_cat(cat, var):
            if var.get():
                if cat not in self.temp_filter_categories:
                    self.temp_filter_categories.append(cat)
                all_var.set(False)
            else:
                if cat in self.temp_filter_categories:
                    self.temp_filter_categories.remove(cat)
                if not self.temp_filter_categories:
                    all_var.set(True)
            update_button_text()
            
        chk_all = ctk.CTkCheckBox(scroll, text="Tất cả", variable=all_var, font=FONT_MAIN, border_width=1, checkbox_width=20, checkbox_height=20, command=on_all)
        chk_all.pack(anchor="w", padx=10, pady=(10, 5))
        
        for cat in cats:
            var = tk.BooleanVar(value=cat in self.temp_filter_categories)
            chk = ctk.CTkCheckBox(scroll, text=cat, variable=var, font=FONT_MAIN, border_width=1, checkbox_width=20, checkbox_height=20, command=lambda c=cat, v=var: on_cat(c, v))
            chk.pack(anchor="w", padx=10, pady=5)
            self.cat_vars[cat] = var
            
        close_btn = ctk.CTkButton(frame, text="Xong", height=28, fg_color=PANEL_BG_HOVER, command=self.cat_dropdown_window.destroy)
        close_btn.pack(fill="x", padx=5, pady=5)

# ==========================================
# Tên file: filter_dialog.py (nằm trong thư mục views/transactions)
# Danh sách lớp và chức năng OOP:
# Lớp: FilterWindow
# - Chức năng: Hộp thoại tùy chọn bộ lọc nâng cao (CTkToplevel) hỗ trợ lọc giao dịch chi tiết theo nhiều tiêu chí đồng thời như: đa danh mục chi tiêu, loại giao dịch, khoảng số tiền và khoảng thời gian.
# Khái niệm OOP sử dụng:
# - Tính kế thừa (Inheritance): FilterWindow kế thừa ctk.CTkToplevel để chạy như một cửa sổ độc quyền nổi lên phía trên MainWindow.
# - Tính đóng gói (Encapsulation): Đóng gói chi tiết xây dựng giao diện các trường nhập liệu bộ lọc, thuật toán tạo trình thả xuống đa chọn danh mục (Custom Multi-select Dropdown) và quản lý trạng thái tạm thời (self.temp_filter_categories) của các tùy chọn trước khi áp dụng.
# - Giao tiếp đối tượng (Object Collaboration): Đồng bộ dữ liệu hai chiều với master (MainWindow), lấy cấu hình lọc hiện có của master để hiển thị và ghi đè ngược cấu hình lọc mới về master, đồng thời gọi trực tiếp main_app.apply_filters() để tải lại bảng giao dịch sau khi lưu.
# ==========================================

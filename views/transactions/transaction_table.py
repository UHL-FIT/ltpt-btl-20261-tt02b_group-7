# Nhập các thư viện cần thiết cho bảng dữ liệu
import tkinter as tk
import customtkinter as ctk
from views.core.theme_styles import *
from views.core.ui_decorators import safe_execution

# ==========================================
# Tên file: transaction_table.py (nằm trong thư mục views/transactions)
# Danh sách lớp và chức năng OOP:
# Lớp: TransactionTable
# - Chức năng: Thành phần bảng tùy chỉnh phức tạp (Custom Table Component) hiển thị chi tiết các giao dịch tài chính, hỗ trợ cuộn dữ liệu, phản hồi trạng thái hover/click dòng, checkbox đa lựa chọn, sắp xếp động và menu tác vụ nhanh.
# Khái niệm OOP sử dụng:
# - Tính kế thừa (Inheritance): Kế thừa ctk.CTkFrame để thừa hưởng các thuộc tính thiết lập container UI của CustomTkinter.
# - Tính đóng gói (Encapsulation): Che giấu toàn bộ cấu trúc lắp ghép phức tạp của tiêu đề cột, khung cuộn, định dạng trạng thái dòng (màu xanh cho lựa chọn, đỏ/xanh lá badge loại giao dịch, v.v.). Cung cấp các API công khai rõ ràng như clear_table(), show_empty_state(), add_row() phục vụ MainWindow.
# - Ủy nhiệm sự kiện qua Callbacks (Loose Coupling): Nhận danh sách các callback nghiệp vụ rộng lớn (chọn dòng, sắp xếp, sửa, xóa, menu chuột phải) để chuyển tiếp hành vi người dùng về MainWindow/Controller xử lý, đảm bảo thiết kế lỏng lẻo dễ tái sử dụng.
# ==========================================


# Khai báo lớp TransactionTable hiển thị danh sách các giao dịch dưới dạng bảng
class TransactionTable(ctk.CTkFrame):
    # Khởi tạo bảng danh sách giao dịch
    def __init__(self, master, icons, select_all_var,
                 toggle_select_all_cb, toggle_row_selection_cb,
                 sort_cb, edit_cb, delete_cb, context_menu_cb,
                 **kwargs):
        """
        Thành phần Bảng dữ liệu tùy chỉnh cao cấp hiển thị lịch sử giao dịch.
        """
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.icons = icons
        self.select_all_var = select_all_var
        self.toggle_select_all_cb = toggle_select_all_cb
        self.toggle_row_selection_cb = toggle_row_selection_cb
        self.sort_cb = sort_cb
        self.edit_cb = edit_cb
        self.delete_cb = delete_cb
        self.context_menu_cb = context_menu_cb
        
        self.header_labels = {}
        self.cols = [("☐", 40), ("Thời gian", 160), ("Danh mục", 150), ("Loại", 100), ("Số tiền", 140), ("Ghi chú", 200), ("Thao tác", 80)]
        
        self.setup_header()
        self.setup_scroll_area()
        
    # Tạo ô checkbox tùy chỉnh sử dụng cho việc chọn dòng
    def _create_checkbox(self, parent, variable, command):
        return ctk.CTkCheckBox(
            parent, text="", variable=variable, width=40,
            checkbox_width=20, checkbox_height=20, border_width=1, corner_radius=5,
            border_color="#64748B", fg_color="#3B82F6", hover_color="#2563EB",
            command=command
        )
        
    # Khởi tạo thanh tiêu đề cột của bảng
    def setup_header(self):
        header_frame = ctk.CTkFrame(self, height=36, fg_color=PANEL_BG, corner_radius=8)
        header_frame.pack_propagate(False)
        header_frame.grid(row=0, column=0, sticky="ew")
        
        # Pack Thao tác first with side="right" to anchor it to the far right
        for text, width in self.cols:
            if text == "Thao tác":
                cursor = ""
                col_frame = ctk.CTkFrame(header_frame, fg_color="transparent", width=width, height=36)
                col_frame.pack_propagate(False)
                col_frame.pack(side="right", padx=(5, 41), fill="y")
                
                inner = ctk.CTkFrame(col_frame, fg_color="transparent", height=36)
                inner.pack(expand=True, fill="y")
                
                lbl = ctk.CTkLabel(inner, text=text, font=FONT_TABLE_HEADER, text_color=TEXT_MUTED, cursor=cursor)
                lbl.pack(side="left")
                break

        # Then pack the rest from left to right, allowing Ghi chú to expand and fill the remaining middle space
        for text, width in self.cols:
            if text == "Thao tác":
                continue
                
            anchor = "e" if text == "Số tiền" else "w"
            if text in ["☐", "Loại"]: anchor = "center"
            
            if text == "☐":
                self.header_checkbox = self._create_checkbox(header_frame, self.select_all_var, self.toggle_select_all_cb)
                self.header_checkbox.pack(side="left", padx=(16, 0))
            else:
                cursor = "hand2" if text in ["Thời gian", "Số tiền"] else ""
                col_frame = ctk.CTkFrame(header_frame, fg_color="transparent", width=width, height=36)
                col_frame.pack_propagate(False)
                
                custom_padx = (50, 5) if text == "Ghi chú" else 5
                if text == "Ghi chú":
                    col_frame.pack(side="left", padx=custom_padx, fill="both", expand=True)
                else:
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
                    
                    lbl.bind("<Button-1>", lambda e, c=text: self.sort_cb(c))
                    lbl_arr.bind("<Button-1>", lambda e, c=text: self.sort_cb(c))
                    col_frame.bind("<Button-1>", lambda e, c=text: self.sort_cb(c))
                    
        self.update_header_arrows(None, None)
        
    # Thiết lập khung cuộn chứa dữ liệu bảng
    def setup_scroll_area(self):
        self.table_scroll = ctk.CTkScrollableFrame(self, fg_color=BG_COLOR)
        self.table_scroll.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        
    # Cập nhật mũi tên chỉ hướng sắp xếp trên tiêu đề cột
    def update_header_arrows(self, sort_by, sort_order):
        for col, lbl_arr in self.header_labels.items():
            if sort_by == col:
                if sort_order == "desc":
                    lbl_arr.configure(image=self.icons.get('sort_down'))
                else:
                    lbl_arr.configure(image=self.icons.get('sort_up'))
            else:
                lbl_arr.configure(image=self.icons.get('sort'))
                
    # Xóa sạch tất cả các hàng hiện tại trong bảng
    def clear_table(self):
        for widget in self.table_scroll.winfo_children():
            widget.destroy()
            
    # Hiển thị thông báo khi không có giao dịch nào thỏa mãn điều kiện
    def show_empty_state(self):
        self.clear_table()
        ctk.CTkLabel(
            self.table_scroll, text=" Không tìm thấy giao dịch nào", 
            image=self.icons.get('empty'), compound="left", 
            font=FONT_TITLE, text_color=TEXT_MUTED
        ).pack(pady=50)
        
    # Hiển thị các ô khung giả lập (skeleton) khi đang nạp dữ liệu
    def show_loading_placeholder(self):
        self.clear_table()
        for _ in range(5):
            row = ctk.CTkFrame(self.table_scroll, height=40, fg_color=PANEL_BG, corner_radius=6)
            row.pack(fill="x", pady=2)
            for w in [40, 100, 150, 80]:
                ctk.CTkFrame(row, width=w, height=20, fg_color=BORDER_COLOR).pack(side="left", padx=10)
                
    # Thêm một hàng dữ liệu giao dịch mới vào bảng
    @safe_execution("Lỗi kết xuất hàng giao dịch")
    def add_row(self, t, index, is_selected, toggle_callback):
        bg_color = "transparent"
        
        outer_row = ctk.CTkFrame(self.table_scroll, fg_color="transparent")
        outer_row.pack(fill="x")
        
        row = ctk.CTkFrame(outer_row, height=44, fg_color=bg_color, corner_radius=0)
        row.pack(fill="x")
        row.pack_propagate(False)
        
        separator = tk.Frame(outer_row, bg=BORDER_COLOR, height=1)
        separator.pack(fill="x", padx=10)
        
        action_frame = ctk.CTkFrame(row, fg_color="transparent", width=80, height=36, corner_radius=0, border_width=0)
        action_frame.pack_propagate(False)
        action_frame.pack(side="right", padx=(5, 25))
        
        def on_enter(e, r=row):
            r.configure(fg_color=PANEL_BG_HOVER)
            
        def on_leave(e, r=row, orig=bg_color):
            # Kiểm tra trạng thái lựa chọn
            if not chk_var.get():
                r.configure(fg_color=orig)
            else:
                r.configure(fg_color="#1E3A8A")
                
        chk_var = tk.BooleanVar(value=is_selected)
        
        # Thao tác chọn checkbox để cập nhật trạng thái
        def on_checkbox_toggle():
            state = chk_var.get()
            toggle_callback(t['id'], state, row, chk_var)
            
        chk = self._create_checkbox(row, chk_var, on_checkbox_toggle)
        chk.pack(side="left", padx=(10, 0))
        
        # Đổi màu dòng nếu dòng đó đã được chọn từ trước
        if is_selected:
            row.configure(fg_color="#1E3A8A")
            
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
        
        # Ghi chú label với fill="x" và expand=True để kéo dài tự động đến cột Thao tác
        note_lbl = ctk.CTkLabel(row, text=str(t['note']), anchor="w", font=FONT_MAIN, text_color=TEXT_MUTED)
        note_lbl.pack(side="left", padx=(50, 5), fill="x", expand=True)
        
        btn_edit = ctk.CTkButton(
            action_frame, text="", image=self.icons.get('edit'), 
            width=30, height=30, fg_color="transparent", hover_color=ACCENT_BLUE, 
            command=lambda: self.edit_cb(t)
        )
        btn_edit.pack(side="left", padx=2)
        
        btn_del = ctk.CTkButton(
            action_frame, text="", image=self.icons.get('delete'), 
            width=30, height=30, fg_color="transparent", hover_color=ACCENT_RED, 
            command=lambda: self.delete_cb(t)
        )
        btn_del.pack(side="left", padx=2)
        
        row.bind("<Enter>", on_enter)
        row.bind("<Leave>", on_leave)
        
        for child in row.winfo_children():
            child.bind("<Button-3>", lambda e, item=t: self.context_menu_cb(e, item))
            if not isinstance(child, ctk.CTkButton) and not isinstance(child, ctk.CTkCheckBox):
                child.bind("<Button-1>", lambda e, item_id=t['id'], v=chk_var, r=row: toggle_callback(item_id, not v.get(), r, v))


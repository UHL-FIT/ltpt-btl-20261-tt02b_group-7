# Nhập các thư viện cần thiết
import customtkinter as ctk
from views.core.theme_styles import (
    PANEL_BG, BG_COLOR, BORDER_COLOR, TEXT_MAIN, FONT_TITLE, FONT_MAIN, 
    PANEL_BG_HOVER, FONT_BUTTON
)

# ==========================================
# Tên file: header_view.py (nằm trong thư mục views/core)
# Danh sách lớp và chức năng OOP:
# Lớp: HeaderView
# - Chức năng: Thành phần giao diện tùy chỉnh (Custom Widget) quản lý thanh tiêu đề trên cùng của ứng dụng, chứa logo, ô tìm kiếm và các nút hành động (Nhập CSV, Xuất CSV, Thống kê, Hạn mức, Trợ giúp).
# Khái niệm OOP sử dụng:
# - Tính kế thừa (Inheritance): HeaderView kế thừa ctk.CTkFrame để làm bộ khung nền chứa các thành phần giao diện khác.
# - Ủy nhiệm sự kiện qua Callback (Loose Coupling / Callbacks): Tiếp nhận các hàm callback thông qua hàm dựng (__init__) từ MainWindow để kích hoạt sự kiện bên ngoài mà không cần gắn chặt logic xử lý trực tiếp vào lớp này.
# - Tính đóng gói (Encapsulation): Che giấu chi tiết cài đặt của các ô nhập liệu và các nút bên trong, chỉ cung cấp các API công khai rõ ràng như get_search_text(), clear_search(), focus_search() để tương tác với dữ liệu.
# ==========================================


# Khai báo lớp HeaderView quản lý thanh tiêu đề trên cùng
class HeaderView(ctk.CTkFrame):
    # Khởi tạo thanh tiêu đề chứa logo, ô tìm kiếm và các nút chức năng
    def __init__(self, master, icons, search_cb, import_cb, export_cb, stats_cb, help_cb, **kwargs):
        """
        Khung chứa thanh tiêu đề cao cấp hiển thị logo, ô nhập tìm kiếm và các nút tác vụ.
        """
        super().__init__(master, height=48, fg_color=PANEL_BG, corner_radius=0, **kwargs)
        self.grid_columnconfigure(1, weight=1)
        self.pack_propagate(False)
        
        self.icons = icons
        
        # Phần bên trái: Logo & Tiêu đề ứng dụng
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=20, sticky="w")
        ctk.CTkLabel(left_frame, text="", image=self.icons.get('app_logo')).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(left_frame, text="Quản Lý Chi Tiêu Cá Nhân", font=FONT_TITLE, text_color=TEXT_MAIN).pack(side="left")
        
        # Phần ở giữa: Khung chứa thanh tìm kiếm dạng Capsule
        search_container = ctk.CTkFrame(
            self, fg_color=BG_COLOR, border_color=BORDER_COLOR, border_width=1,
            corner_radius=18, height=36, width=320
        )
        search_container.grid(row=0, column=1, pady=6)
        search_container.grid_propagate(False)
        search_container.grid_columnconfigure(0, weight=1)
        search_container.grid_rowconfigure(0, weight=1)
        
        self.entry_search = ctk.CTkEntry(
            search_container, placeholder_text="Tìm kiếm giao dịch...", 
            width=230, height=30, border_width=0, 
            fg_color="transparent", font=FONT_MAIN,
            text_color=TEXT_MAIN
        )
        self.entry_search.grid(row=0, column=0, padx=(15, 5), sticky="we")
        self.entry_search.bind("<Return>", lambda event: search_cb())
        
        self.btn_search = ctk.CTkButton(
            search_container, text="", image=self.icons.get('search'), 
            width=28, height=28, corner_radius=14, fg_color="transparent", 
            hover_color=PANEL_BG_HOVER, font=FONT_BUTTON, command=search_cb
        )
        self.btn_search.grid(row=0, column=1, padx=(2, 8))
        
        # Phần bên phải: Các nút chức năng
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.grid(row=0, column=2, padx=20, sticky="e")
        
        for text, icon, cmd in [
            (" Nhập CSV", 'import', import_cb), 
            (" Xuất CSV", 'export', export_cb),
            (" Thống kê", 'stats', stats_cb), 
            (" Hướng dẫn", 'help', help_cb)
        ]:
            ctk.CTkButton(
                right_frame, text=text, image=self.icons.get(icon), height=36,
                fg_color="transparent", hover_color=PANEL_BG_HOVER, font=FONT_BUTTON, 
                command=cmd
            ).pack(side="left", padx=2)
            
    # Lấy văn bản đang nhập trong ô tìm kiếm
    def get_search_text(self):
        """
        Lấy chuỗi ký tự tìm kiếm hiện tại từ ô nhập liệu.
        """
        return self.entry_search.get()
        
    # Xóa trắng ô tìm kiếm
    def clear_search(self):
        """
        Xóa nội dung ô tìm kiếm và đặt về rỗng.
        """
        self.entry_search.delete(0, 'end')
        
    # Tập trung con trỏ vào ô tìm kiếm
    def focus_search(self):
        """
        Di chuyển tiêu điểm con trỏ nhập liệu trực tiếp vào ô tìm kiếm.
        """
        self.entry_search.focus()


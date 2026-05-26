# Nhập các thư viện cần thiết
import customtkinter as ctk
from views.core.theme_styles import (
    PANEL_BG, TEXT_MAIN, FONT_MAIN, ACCENT_RED, ACCENT_GREEN
)

# ==========================================
# Tên file: toast_notification.py (nằm trong thư mục views/common)
# Danh sách lớp và chức năng OOP:
# Lớp: ToastNotification
# - Chức năng: Thành phần giao diện tùy chỉnh hiển thị thông báo đẩy (Toast Notification) thời gian ngắn ở góc dưới màn hình và tự động biến mất.
# Khái niệm OOP sử dụng:
# - Tính kế thừa (Inheritance): ToastNotification kế thừa ctk.CTkFrame để làm khung chứa thông báo với các cài đặt kiểu dáng riêng.
# - Tính đóng gói hành vi tự quản lý (Self-contained Behavior Encapsulation): Lớp tự đóng gói các chi tiết hiển thị dựa trên phân loại (error viền đỏ, info viền xanh) và logic tự dọn dẹp bằng cách lên lịch hủy chính nó (self.after(ms, self.destroy)). Người dùng lớp chỉ cần gọi phương thức công khai show() để kích hoạt thông báo mà không cần lo lắng về việc quản lý vòng đời của đối tượng.
# ==========================================


# Khai báo lớp ToastNotification hiển thị thông báo góc dưới phải màn hình
class ToastNotification(ctk.CTkFrame):
    # Khởi tạo thông báo Toast với nội dung, loại thông báo và biểu tượng tương ứng
    def __init__(self, master, message, type="info", image=None, **kwargs):
        """
        Thông báo đẩy (toast) cao cấp hiển thị ở góc dưới bên phải giao diện ứng dụng.
        """
        bcolor = ACCENT_RED if type == "error" else ACCENT_GREEN
        super().__init__(master, fg_color=PANEL_BG, corner_radius=8, border_width=1, border_color=bcolor, **kwargs)
        
        self.lbl = ctk.CTkLabel(
            self, text=f"  {message}", image=image, compound="left", 
            text_color=TEXT_MAIN, font=FONT_MAIN
        )
        self.lbl.pack(padx=20, pady=12)
        
    # Định vị và hiển thị Toast trên màn hình, tự động biến mất sau khoảng thời gian ms
    def show(self, ms=3000):
        """
        Hiển thị toast lên giao diện và tự động hủy sau số mili giây chỉ định.
        """
        self.place(relx=0.98, rely=0.95, anchor="se")
        self.after(ms, self.destroy)


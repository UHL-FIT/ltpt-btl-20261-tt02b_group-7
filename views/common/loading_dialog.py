# Nhập các thư viện cần thiết
import customtkinter as ctk
from views.core.theme_styles import PANEL_BG, FONT_TITLE, ACCENT_BLUE

# Khai báo lớp LoadingDialog hiển thị thông báo đang tải (loading)
class LoadingDialog(ctk.CTkToplevel):
    # Khởi tạo hộp thoại chờ với một thanh tiến trình chạy vô tận
    def __init__(self, master, message="Đang xử lý...", **kwargs):
        """
        Popup hiển thị trạng thái chờ ở giữa cửa sổ chính với thanh tiến trình hoạt động liên tục.
        """
        super().__init__(master, **kwargs)
        self.title("Đang xử lý")
        self.geometry("300x150")
        self.transient(master)
        self.grab_set()
        self.configure(fg_color=PANEL_BG)
        
        # Căn giữa hộp thoại so với cửa sổ cha
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (300 // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (150 // 2)
        self.geometry(f"+{x}+{y}")
        
        lbl = ctk.CTkLabel(self, text=message, font=FONT_TITLE)
        lbl.pack(expand=True, pady=(20, 10))
        
        self.progressbar = ctk.CTkProgressBar(self, mode="indeterminate", progress_color=ACCENT_BLUE)
        self.progressbar.pack(pady=10, padx=20, fill="x")
        self.progressbar.start()
        
    # Dừng chạy thanh tiến trình và đóng cửa sổ một cách an toàn
    def stop(self):
        """
        Dừng hoạt ảnh của thanh tiến trình và hủy cửa sổ dialog.
        """
        try:
            self.progressbar.stop()
            self.destroy()
        except Exception:
            pass

# ==========================================
# Tên file: loading_dialog.py (nằm trong thư mục views/common)
# Danh sách lớp và chức năng OOP:
# Lớp: LoadingDialog
# - Chức năng: Hộp thoại chờ độc quyền (CTkToplevel + grab_set) hiển thị thanh tiến trình không xác định thời gian (indeterminate) khi ứng dụng đang chạy các tác vụ chạy nền (như import/export CSV, nạp biểu đồ).
# Khái niệm OOP sử dụng:
# - Tính kế thừa (Inheritance): LoadingDialog kế thừa ctk.CTkToplevel để hoạt động như một cửa sổ hội thoại trồi lên phía trên, chặn tương tác với cửa sổ cha trong khi xử lý tác vụ.
# - Tính đóng gói (Encapsulation): Tự khởi tạo và điều khiển trạng thái chuyển động của thanh tiến trình (progressbar.start()) bên trong hàm dựng, đóng gói hành vi tự ngắt hoạt ảnh và tự hủy an toàn thông qua phương thức công khai duy nhất stop().
# ==========================================

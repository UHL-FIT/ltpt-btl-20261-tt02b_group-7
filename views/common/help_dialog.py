# Nhập các thư viện cần thiết cho hộp thoại hướng dẫn
import os
import customtkinter as ctk
from views.core.theme_styles import *
from views.core.ui_decorators import safe_execution

# Khai báo lớp HelpWindow hiển thị hộp thoại hướng dẫn sử dụng tài liệu
class HelpWindow(ctk.CTkToplevel):
    # Khởi tạo hộp thoại hướng dẫn sử dụng
    def __init__(self, master, icons, **kwargs):
        """
        Cửa sổ popup kích hoạt mở tài liệu huong_dan_su_dung.pdf trên Hệ điều hành.
        """
        super().__init__(master, **kwargs)
        self.title("Hướng dẫn")
        self.geometry("400x300")
        self.transient(master)
        self.configure(fg_color=PANEL_BG)
        self.icons = icons
        self.main_app = master
        
        # Căn giữa hộp thoại so với cửa sổ cha
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (400 // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (300 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.setup_ui()

    # Thiết lập giao diện người dùng cho hộp thoại hướng dẫn
    def setup_ui(self):
        lbl_title = ctk.CTkLabel(self, text="Hướng dẫn sử dụng", font=FONT_TITLE)
        lbl_title.pack(pady=20)
        
        lbl_desc = ctk.CTkLabel(self, text="Vui lòng mở file PDF để xem chi tiết.", font=FONT_MAIN, text_color=TEXT_MUTED)
        lbl_desc.pack(pady=20)
        
        btn_open_pdf = ctk.CTkButton(self, text="Mở file PDF Hướng dẫn", font=FONT_TEXT_LARGE, fg_color=ACCENT_BLUE, command=self.open_pdf)
        btn_open_pdf.pack(pady=20)

    # Mở tệp tin PDF hướng dẫn sử dụng trên máy tính của người dùng
    @safe_execution("Lỗi mở tài liệu hướng dẫn")
    def open_pdf(self):
        # Đường dẫn tới tệp pdf ở thư mục gốc của dự án. 
        # views/dialogs/help_dialog.py là cấp 3 (views -> dialogs -> help_dialog.py), nên cần lùi 3 cấp thư mục.
        pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'huong_dan_su_dung.pdf')
        try:
            os.startfile(os.path.abspath(pdf_path))
        except Exception as e:
            self.main_app.show_error("Lỗi", f"Không thể mở file PDF: {str(e)}")

# ==========================================
# Tên file: help_dialog.py (nằm trong thư mục views/dialogs)
# Danh sách lớp và chức năng OOP:
# Lớp: HelpWindow
# - Chức năng: Hộp thoại con (CTkToplevel) hiển thị thông tin giới thiệu và cung cấp nút mở trực tiếp tài liệu hướng dẫn sử dụng định dạng PDF trên Hệ điều hành.
# Khái niệm OOP sử dụng:
# - Tính kế thừa (Inheritance): Lớp kế thừa ctk.CTkToplevel để nhanh chóng thừa hưởng các thuộc tính quản lý cửa sổ dạng hộp thoại trồi lên (Popup Dialog).
# - Tính đóng gói (Encapsulation): Lớp đóng gói kín kẽ các widgets giao diện của riêng mình và hành vi tương ứng (HelpWindow quản lý đường dẫn và tương tác mở tệp PDF bên ngoài hệ điều hành).
# ==========================================

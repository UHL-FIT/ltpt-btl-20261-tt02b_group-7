# Nhập các thư viện cần thiết
import customtkinter as ctk
from views.core.theme_styles import (
    PANEL_BG, BORDER_COLOR, TEXT_MAIN, TEXT_MUTED, FONT_LABEL, FONT_SUMMARY
)

# ==========================================
# Tên file: summary_card.py (nằm trong thư mục views/common)
# Danh sách lớp và chức năng OOP:
# Lớp: SummaryCard
# - Chức năng: Lớp thành phần giao diện tùy chỉnh (Custom Widget) dùng để hiển thị các thông tin tóm tắt tài chính (Thu nhập, Chi tiêu, Số dư, v.v.) trực quan.
# Khái niệm OOP sử dụng:
# - Tính kế thừa (Inheritance): SummaryCard kế thừa ctk.CTkFrame để có đầy đủ thuộc tính và hành vi của một container trong CustomTkinter.
# - Tính đóng gói (Encapsulation): Đóng gói chi tiết giao diện con (icon, tiêu đề, nhãn giá trị) bên trong lớp. Đồng thời cung cấp phương thức công khai configure_value để cập nhật dữ liệu từ bên ngoài một cách an toàn mà không làm lộ cấu trúc widget bên trong.
# - Tái sử dụng đối tượng (Object Reusability): Cho phép khởi tạo nhanh nhiều thẻ tóm tắt tài chính khác nhau (Income, Expense, Balance) từ một khuôn mẫu duy nhất giúp giảm thiểu trùng lặp mã nguồn.
# ==========================================


# Khai báo lớp SummaryCard hiển thị thông tin tóm tắt các chỉ số tài chính
class SummaryCard(ctk.CTkFrame):
    # Khởi tạo thẻ tóm tắt với nhãn, giá trị hiển thị, biểu tượng và màu sắc văn bản
    def __init__(self, master, label, value, icon, value_color=TEXT_MAIN, **kwargs):
        """
        Thẻ tóm tắt cao cấp hiển thị các chỉ số tài chính trên giao diện chính.
        """
        super().__init__(master, fg_color=PANEL_BG, corner_radius=12, border_width=1, border_color=BORDER_COLOR, **kwargs)
        
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=15, pady=(10, 0))
        if icon:
            ctk.CTkLabel(top_frame, text="", image=icon).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(top_frame, text=label, font=FONT_LABEL, text_color=TEXT_MUTED).pack(side="left")
        
        self.val_lbl = ctk.CTkLabel(self, text=value, font=FONT_SUMMARY, text_color=value_color)
        self.val_lbl.pack(anchor="w", padx=15, pady=(0, 10))
        
    # Cập nhật giá trị hiển thị trên thẻ một cách an toàn
    def configure_value(self, value, text_color=None):
        """
        Cập nhật lại nhãn giá trị hiển thị của thẻ tóm tắt.
        """
        self.val_lbl.configure(text=value)
        if text_color:
            self.val_lbl.configure(text_color=text_color)


import customtkinter as ctk
from views.core.theme_styles import (
    PANEL_BG, ACCENT_AMBER, TEXT_MUTED, BORDER_COLOR
)

class BaseTab(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.master = master
        self.controller = controller
        self.icons = getattr(master, 'icons', {})
        self.main_app = getattr(master, 'main_app', master)
        self.show_message = getattr(master, 'show_message', lambda t, m: None)
        self.show_error = getattr(master, 'show_error', lambda t, m: None)
        self.selected_month = None

    def format_currency_short(self, val):
        """Định dạng rút gọn các chỉ số tiền mặt (Ví dụ: 1.5M đ, 30.5k đ)"""
        abs_val = abs(val)
        suffix = "đ"
        if abs_val >= 1_000_000:
            formatted = f"{val / 1_000_000:.1f}M"
        elif abs_val >= 1_000:
            formatted = f"{val / 1_000:.1f}k"
        else:
            formatted = f"{val:.0f}"
        return f"{formatted} {suffix}"
        
    def format_currency_vn(self, val):
        """Định dạng tiền Việt chuẩn (ví dụ: 4,585,000 đ)"""
        return f"{val:,.0f} đ"

    def _check_month_selected(self):
        """
        Kiểm tra xem người dùng có đang chọn một tháng cụ thể không.
        Nếu là 'Tất cả' (None), hiển thị thẻ cảnh báo hướng dẫn và trả về False.
        """
        # Xóa sạch widget cũ trong self trước khi vẽ
        for widget in self.winfo_children():
            widget.destroy()
            
        if self.selected_month is not None:
            return True
            
        # Vẽ thẻ cảnh báo "Tất cả" cực kỳ cao cấp
        warning_card = ctk.CTkFrame(
            self,
            fg_color=PANEL_BG,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_COLOR
        )
        warning_card.pack(expand=True, padx=40, pady=40)
        
        # Icon cảnh báo màu hổ phách/vàng
        warning_icon = self.icons.get('warning')
        icon_lbl = ctk.CTkLabel(
            warning_card,
            text="",
            image=warning_icon
        )
        icon_lbl.pack(pady=(30, 15))
        
        title_lbl = ctk.CTkLabel(
            warning_card,
            text="Chọn tháng để quản lý",
            font=("Consolas", 18, "bold"),
            text_color=ACCENT_AMBER
        )
        title_lbl.pack(pady=(0, 10), padx=30)
        
        desc_lbl = ctk.CTkLabel(
            warning_card,
            text="Hạn mức ngân sách, cảnh báo và mục tiêu tiết kiệm hoạt động theo từng tháng.\nVui lòng chọn một tháng cụ thể ở góc trên bên phải để tiếp tục.",
            font=("Consolas", 12),
            text_color=TEXT_MUTED,
            justify="center"
        )
        desc_lbl.pack(pady=(0, 30), padx=30)
        
        return False

    def refresh(self, selected_month):
        """Làm mới dữ liệu và vẽ lại các biểu đồ trong tab con."""
        self.selected_month = selected_month

    def cleanup(self):
        """Dọn dẹp bộ nhớ biểu đồ khi đóng cửa sổ."""
        pass

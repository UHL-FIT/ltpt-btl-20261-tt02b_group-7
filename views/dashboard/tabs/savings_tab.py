import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils.logger import logger

from views.core.theme_styles import (
    BG_COLOR, PANEL_BG, PANEL_BG_HOVER, ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED, ACCENT_AMBER,
    TEXT_MAIN, TEXT_MUTED, BORDER_COLOR, FONT_MAIN, FONT_LABEL
)
from views.dashboard.tabs.base_tab import BaseTab
from views.core.ui_decorators import format_entry_amount

class SavingsTab(BaseTab):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, controller, **kwargs)
        
        self.savings_fig = None
        self.savings_ax = None
        self.savings_canvas = None
        
    def refresh(self, selected_month):
        super().refresh(selected_month)
        self._render_savings_tab()
        
    def _render_savings_tab(self):
        """Dựng giao diện cho tab Tiết kiệm tích lũy."""
        for widget in self.winfo_children():
            widget.destroy()
            
        if not self._check_month_selected():
            return
            
        db_month = self.selected_month
        
        # 3. Tạo bố cục 2 cột (Trái: Nhập mục tiêu, Phải: Báo cáo trực quan kèm Metrics)
        self.grid_columnconfigure(0, weight=4, uniform="savings_col")
        self.grid_columnconfigure(1, weight=6, uniform="savings_col")
        self.grid_rowconfigure(0, weight=1)
        
        # CỘT TRÁI: NHẬP MỤC TIÊU FORM
        left_panel = ctk.CTkFrame(
            self,
            fg_color=PANEL_BG,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_COLOR
        )
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        
        ctk.CTkLabel(
            left_panel,
            text="Mục tiêu tích lũy",
            font=("Consolas", 16, "bold"),
            text_color=TEXT_MAIN,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 15))
        
        ctk.CTkLabel(
            left_panel,
            text="Mục tiêu tiết kiệm trong tháng (đ):",
            font=FONT_LABEL,
            text_color=TEXT_MUTED,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(5, 5))
        
        self.savings_entry = ctk.CTkEntry(
            left_panel,
            height=38,
            placeholder_text="Ví dụ: 3,000,000",
            font=FONT_MAIN,
            fg_color=BG_COLOR,
            border_color=BORDER_COLOR
        )
        self.savings_entry.pack(fill="x", padx=20, pady=(0, 20))
        self.savings_entry.bind("<KeyRelease>", lambda event: format_entry_amount(self.savings_entry, event))
        
        current_goal = self.controller.get_savings_goal(db_month) if self.controller else 0.0
        if current_goal > 0:
            formatted_goal = f"{int(current_goal):,}"
            self.savings_entry.insert(0, formatted_goal)
            
        save_btn = ctk.CTkButton(
            left_panel,
            text="Lưu mục tiêu",
            font=("Consolas", 13, "bold"),
            fg_color=ACCENT_BLUE,
            hover_color=PANEL_BG_HOVER,
            text_color=TEXT_MAIN,
            height=38,
            command=lambda: self._save_savings_goal(db_month)
        )
        save_btn.pack(fill="x", padx=20, pady=(0, 20))
        
        divider = ctk.CTkFrame(left_panel, height=1, fg_color=BORDER_COLOR)
        divider.pack(fill="x", padx=20, pady=(10, 20))
        
        advice_lbl = ctk.CTkLabel(
            left_panel,
            text="💡 Mẹo tích lũy:\nĐặt mục tiêu tiết kiệm bằng 10% - 20% tổng thu nhập hàng tháng để xây dựng quỹ khẩn cấp vững vàng.",
            font=("Consolas", 11),
            text_color=TEXT_MUTED,
            justify="left",
            wraplength=230,
            anchor="w"
        )
        advice_lbl.pack(fill="x", padx=20, pady=(0, 20))
        
        # CỘT PHẢI: BÁO CÁO TIẾN TRÌNH TRỰC QUAN
        right_panel = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        
        # Chia cột phải thành 2 phân vùng: Trái (Donut Ring), Phải (Metrics & Lời khuyên)
        right_panel.grid_columnconfigure(0, weight=4, uniform="savings_right_inner")
        right_panel.grid_columnconfigure(1, weight=6, uniform="savings_right_inner")
        right_panel.grid_rowconfigure(0, weight=1)
        
        prog = self.controller.get_savings_progress(db_month) if self.controller else {}
        
        goal_amt = prog.get('goal', 0.0)
        income_amt = prog.get('total_income', 0.0)
        expense_amt = prog.get('total_expense', 0.0)
        saving_amt = prog.get('actual_saving', 0.0)
        gap_amt = prog.get('gap', 0.0)
        pct_achieved = prog.get('pct_achieved', 0.0)
        status_str = prog.get('status', "⚠ Chưa đặt mục tiêu")
        
        progress_color = ACCENT_BLUE
        if "Đạt mục tiêu" in status_str:
            progress_color = ACCENT_GREEN
        elif "Đang tiến tới" in status_str:
            progress_color = ACCENT_AMBER
        elif "Chi vượt thu" in status_str or saving_amt < 0:
            progress_color = ACCENT_RED
            
        # 1. PHÂN VÙNG TRÁI: DONUT PROGRESS RING
        donut_card = ctk.CTkFrame(
            right_panel,
            fg_color=PANEL_BG,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_COLOR
        )
        donut_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        
        ctk.CTkLabel(
            donut_card,
            text="Vòng tiến độ",
            font=("Consolas", 14, "bold"),
            text_color=TEXT_MAIN
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        # Khởi tạo hoặc vẽ lại Figure Donut
        if self.savings_fig is None:
            self.savings_fig = plt.figure(figsize=(3, 3), facecolor=PANEL_BG)
            self.savings_ax = self.savings_fig.add_subplot(111)
        else:
            self.savings_ax.clear()
            
        self.savings_ax.set_facecolor(PANEL_BG)
        
        # Xác định kích thước và màu sắc donut
        if goal_amt <= 0:
            donut_sizes = [100]
            donut_colors = [BORDER_COLOR]
            center_text = "0%"
        elif saving_amt <= 0:
            donut_sizes = [100]
            donut_colors = [ACCENT_RED]
            center_text = "Chi > Thu" if saving_amt < 0 else "0%"
        elif saving_amt >= goal_amt:
            donut_sizes = [100]
            donut_colors = [ACCENT_GREEN]
            center_text = f"{pct_achieved:.0f}%"
        else:
            donut_sizes = [saving_amt, goal_amt - saving_amt]
            donut_colors = [progress_color, BORDER_COLOR]
            center_text = f"{pct_achieved:.1f}%"
            
        # Vẽ biểu đồ donut
        self.savings_ax.pie(
            donut_sizes,
            colors=donut_colors,
            startangle=90,
            counterclock=False,
            wedgeprops=dict(width=0.28, edgecolor=PANEL_BG, linewidth=2.5)
        )
        
        # Văn bản phần trăm lớn ở tâm Donut
        self.savings_ax.text(
            0, 0, center_text,
            ha='center', va='center',
            fontsize=16, fontweight='bold',
            color=TEXT_MAIN, family='Consolas'
        )
        
        self.savings_ax.axis('equal')
        self.savings_fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        
        self.savings_canvas = FigureCanvasTkAgg(self.savings_fig, master=donut_card)
        self.savings_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.savings_canvas.draw()
        
        # 2. PHÂN VÙNG PHẢI: METRICS & ADVICE CARD
        metrics_panel = ctk.CTkFrame(
            right_panel,
            fg_color="transparent"
        )
        metrics_panel.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        
        # Trạng thái tích lũy
        status_card = ctk.CTkFrame(
            metrics_panel,
            fg_color=PANEL_BG,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR
        )
        status_card.pack(fill="x", pady=(0, 10))
        
        status_row = ctk.CTkFrame(status_card, fg_color="transparent")
        status_row.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            status_row,
            text="Trạng thái:",
            font=("Consolas", 12),
            text_color=TEXT_MUTED
        ).pack(side="left")
        
        status_badge = ctk.CTkLabel(
            status_row,
            text=status_str,
            font=("Consolas", 11, "bold"),
            text_color=progress_color,
            fg_color=BG_COLOR,
            corner_radius=6,
            padx=10,
            pady=3
        )
        status_badge.pack(side="left", padx=8)
        
        # Grid 4 thẻ thông tin nhỏ
        metric_grid = ctk.CTkFrame(metrics_panel, fg_color="transparent")
        metric_grid.pack(fill="x", pady=(0, 10))
        
        metric_grid.grid_columnconfigure(0, weight=1, uniform="grid_item")
        metric_grid.grid_columnconfigure(1, weight=1, uniform="grid_item")
        metric_grid.grid_rowconfigure(0, weight=1, uniform="grid_row")
        metric_grid.grid_rowconfigure(1, weight=1, uniform="grid_row")
        
        metrics_def = [
            ("Mục tiêu đề ra", goal_amt, TEXT_MAIN, 0, 0),
            ("Đã tích lũy", saving_amt, ACCENT_GREEN if saving_amt >= 0 else ACCENT_RED, 0, 1),
            ("Tổng thu nhập", income_amt, ACCENT_GREEN, 1, 0),
            ("Tổng chi tiêu", expense_amt, ACCENT_RED, 1, 1)
        ]
        
        for name, amt, color, r, c in metrics_def:
            card_item = ctk.CTkFrame(
                metric_grid,
                fg_color=PANEL_BG,
                corner_radius=12,
                border_width=1,
                border_color=BORDER_COLOR
            )
            card_item.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
            
            ctk.CTkLabel(
                card_item,
                text=name,
                font=("Consolas", 11),
                text_color=TEXT_MUTED
            ).pack(anchor="w", padx=10, pady=(8, 2))
            
            formatted_amt = self.format_currency_vn(amt)
            ctk.CTkLabel(
                card_item,
                text=formatted_amt,
                font=("Consolas", 13, "bold"),
                text_color=color
            ).pack(anchor="w", padx=10, pady=(2, 8))
            
        # Lời khuyên động
        if goal_amt == 0:
            advice_text = "Hãy thiết lập mục tiêu ở bên trái để bắt đầu lập kế hoạch tích lũy."
            advice_color = TEXT_MUTED
        elif saving_amt <= 0:
            advice_text = "🔴 Nguy hiểm: Chi tiêu của bạn đang lớn hơn hoặc bằng tổng thu nhập. Hãy thắt chặt ngân sách chi tiêu ngay!"
            advice_color = ACCENT_RED
        elif saving_amt >= goal_amt:
            advice_text = "🎉 Tuyệt vời! Bạn đã vượt mục tiêu tiết kiệm đề ra. Hãy tiếp tục duy trì thói quen tích lũy thông minh này."
            advice_color = ACCENT_GREEN
        else:
            advice_text = f"📈 Cố lên! Bạn cần tiết kiệm thêm {self.format_currency_vn(abs(gap_amt))} nữa để đạt mục tiêu tháng."
            advice_color = ACCENT_AMBER
            
        advice_card = ctk.CTkFrame(metrics_panel, fg_color=PANEL_BG, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        advice_card.pack(fill="x")
        
        ctk.CTkLabel(
            advice_card,
            text=advice_text,
            font=("Consolas", 11, "bold"),
            text_color=advice_color,
            justify="left",
            wraplength=260
        ).pack(padx=12, pady=10)
        
    def _save_savings_goal(self, db_month):
        """Lưu mục tiêu tiết kiệm."""
        amt_str = self.savings_entry.get().replace(",", "").replace(".", "").strip()
        if not amt_str:
            self.show_error("Lỗi", "Vui lòng nhập số tiền mục tiêu!")
            return
            
        try:
            amt = float(amt_str)
            if amt < 0:
                raise ValueError()
        except ValueError:
            self.show_error("Lỗi", "Số tiền mục tiêu tiết kiệm phải là số dương hợp lệ!")
            return
            
        try:
            self.controller.set_savings_goal(db_month, amt)
            self.show_message("Thành công", "Đã cập nhật mục tiêu tích lũy thành công!")
            self._render_savings_tab()
        except Exception as e:
            self.show_error("Lỗi", f"Không thể đặt mục tiêu tiết kiệm: {str(e)}")
            

            
    def cleanup(self):
        """Giải phóng tài nguyên biểu đồ của SavingsTab"""
        logger.info("Giải phóng tài nguyên biểu đồ của SavingsTab")
        if self.savings_fig is not None:
            try:
                plt.close(self.savings_fig)
            except Exception:
                pass

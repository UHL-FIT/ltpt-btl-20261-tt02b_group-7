import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from utils.logger import logger

from views.core.theme_styles import (
    BG_COLOR, PANEL_BG, ACCENT_GREEN, ACCENT_RED, ACCENT_AMBER,
    TEXT_MAIN, TEXT_MUTED, BORDER_COLOR
)
from views.dashboard.tabs.base_tab import BaseTab

class AlertsTab(BaseTab):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, controller, **kwargs)
        
        self.alerts_fig = None
        self.alerts_ax = None
        self.alerts_canvas = None
        
    def refresh(self, selected_month):
        super().refresh(selected_month)
        self._render_alerts_tab()
        
    def _render_alerts_tab(self):
        """Dựng giao diện cho tab Cảnh báo vượt hạn."""
        for widget in self.winfo_children():
            widget.destroy()
            
        if not self._check_month_selected():
            return
            
        db_month = self.selected_month
        
        alerts_data = self.controller.check_alerts(db_month) if self.controller else []
        
        over_limit_count = 0
        warning_count = 0
        for item in alerts_data:
            if item['pct'] >= 100:
                over_limit_count += 1
            elif item['pct'] >= 80:
                warning_count += 1
                
        # Card tổng kết phía trên
        top_card = ctk.CTkFrame(
            self,
            fg_color=PANEL_BG,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_COLOR
        )
        top_card.pack(fill="x", pady=(10, 15))
        
        ctk.CTkLabel(
            top_card,
            text="Tình trạng chi tiêu trong tháng",
            font=("Consolas", 15, "bold"),
            text_color=TEXT_MAIN
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        stats_layout = ctk.CTkFrame(top_card, fg_color="transparent")
        stats_layout.pack(fill="x", padx=20, pady=(0, 15))
        
        stats_layout.grid_columnconfigure(0, weight=1, uniform="alert_stat")
        stats_layout.grid_columnconfigure(1, weight=1, uniform="alert_stat")
        stats_layout.grid_rowconfigure(0, weight=1)
        
        # Vượt hạn
        left_stat = ctk.CTkFrame(stats_layout, fg_color=BG_COLOR, corner_radius=12)
        left_stat.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)
        
        ctk.CTkLabel(
            left_stat,
            text=str(over_limit_count),
            font=("Consolas", 28, "bold"),
            text_color=ACCENT_RED
        ).pack(pady=(12, 2))
        
        ctk.CTkLabel(
            left_stat,
            text="Danh mục vượt hạn mức",
            font=("Consolas", 12),
            text_color=TEXT_MUTED
        ).pack(pady=(0, 12))
        
        # Chạm ngưỡng
        right_stat = ctk.CTkFrame(stats_layout, fg_color=BG_COLOR, corner_radius=12)
        right_stat.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)
        
        ctk.CTkLabel(
            right_stat,
            text=str(warning_count),
            font=("Consolas", 28, "bold"),
            text_color=ACCENT_AMBER
        ).pack(pady=(12, 2))
        
        ctk.CTkLabel(
            right_stat,
            text="Danh mục chạm ngưỡng (>= 80%)",
            font=("Consolas", 12),
            text_color=TEXT_MUTED
        ).pack(pady=(0, 12))
        
        chart_card = ctk.CTkFrame(
            self,
            fg_color=PANEL_BG,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_COLOR
        )
        chart_card.pack(fill="both", expand=True, pady=(5, 10))
        
        ctk.CTkLabel(
            chart_card,
            text="Trực quan hóa cảnh báo hạn mức",
            font=("Consolas", 16, "bold"),
            text_color=TEXT_MAIN,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 15))
        
        usage_data = self.controller.get_usage(db_month) if self.controller else []
        
        if not usage_data:
            empty_lbl = ctk.CTkLabel(
                chart_card,
                text="Chưa thiết lập hạn mức để kiểm tra cảnh báo.",
                font=("Consolas", 13),
                text_color=TEXT_MUTED,
                justify="center"
            )
            empty_lbl.pack(expand=True, pady=40)
            return
            
        # Khởi tạo hoặc vẽ lại Figure
        if self.alerts_fig is None:
            self.alerts_fig = plt.figure(figsize=(6, 3.5), facecolor=PANEL_BG)
            self.alerts_ax = self.alerts_fig.add_subplot(111)
        else:
            self.alerts_ax.clear()
            
        self.alerts_ax.set_facecolor(PANEL_BG)
        
        # Dữ liệu
        categories = [item['category'] for item in usage_data]
        percentages = [item['pct'] for item in usage_data]
        
        x_indices = np.arange(len(categories))
        width = 0.4
        
        # Thiết lập màu sắc cột dựa trên tỷ lệ %
        bar_colors = []
        for pct in percentages:
            if pct >= 100:
                bar_colors.append(ACCENT_RED)
            elif pct >= 80:
                bar_colors.append(ACCENT_AMBER)
            else:
                bar_colors.append(ACCENT_GREEN)
                
        # Vẽ các cột biểu đồ dọc biểu diễn % chi tiêu
        rects = self.alerts_ax.bar(x_indices, percentages, width, color=bar_colors, edgecolor='none', zorder=3)
        
        # Vẽ 2 đường giới hạn ngang
        self.alerts_ax.axhline(80, color=ACCENT_AMBER, linestyle='--', linewidth=1.2, alpha=0.85, zorder=2)
        self.alerts_ax.axhline(100, color=ACCENT_RED, linestyle='--', linewidth=1.2, alpha=0.85, zorder=2)
        
        # Thêm nhãn chữ cho các đường giới hạn
        self.alerts_ax.text(
            len(categories) - 0.4, 82, "Cảnh báo (80%)",
            color=ACCENT_AMBER, fontsize=8, family='Consolas', fontweight='bold', ha='right'
        )
        self.alerts_ax.text(
            len(categories) - 0.4, 102, "Ngưỡng đỏ (100%)",
            color=ACCENT_RED, fontsize=8, family='Consolas', fontweight='bold', ha='right'
        )
        
        # Cấu hình biểu đồ
        short_labels = []
        for lbl in categories:
            if len(lbl) > 10:
                short_labels.append(lbl[:9] + "..")
            else:
                short_labels.append(lbl)
                
        self.alerts_ax.set_xticks(x_indices)
        self.alerts_ax.set_xticklabels(short_labels, color=TEXT_MAIN, fontsize=10, family='Consolas')
        self.alerts_ax.tick_params(axis='both', which='both', length=0)
        self.alerts_ax.tick_params(axis='y', colors=TEXT_MUTED, labelsize=9)
        self.alerts_ax.yaxis.set_major_formatter(ticker.PercentFormatter())
        self.alerts_ax.grid(axis='y', color=BORDER_COLOR, linestyle='-', linewidth=0.8, alpha=0.15, zorder=1)
        
        # Nâng cao giới hạn trục Y một chút để biểu diễn thông thoáng
        max_pct = max(percentages) if percentages else 0
        self.alerts_ax.set_ylim(0, max(120, max_pct * 1.15))
        
        # Ẩn viền
        for spine in ['top', 'right', 'left', 'bottom']:
            self.alerts_ax.spines[spine].set_visible(False)
            
        # Thêm nhãn % chính xác trên đầu mỗi cột
        for rect in rects:
            height_val = rect.get_height()
            self.alerts_ax.annotate(
                f"{height_val:.1f}%",
                xy=(rect.get_x() + rect.get_width() / 2, height_val),
                xytext=(0, 4),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=9, fontweight='bold',
                color=TEXT_MAIN, family='Consolas'
            )
            
        # Đồng bộ phông chữ
        for label in self.alerts_ax.get_xticklabels():
            label.set_fontproperties({'family': 'Consolas', 'size': 10})
        for label in self.alerts_ax.get_yticklabels():
            label.set_fontproperties({'family': 'Consolas', 'size': 9})
            
        self.alerts_fig.subplots_adjust(left=0.08, right=0.96, top=0.90, bottom=0.15)
        
        # Dựng canvas
        self.alerts_canvas = FigureCanvasTkAgg(self.alerts_fig, master=chart_card)
        self.alerts_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        self.alerts_canvas.draw()

    def cleanup(self):
        """Giải phóng tài nguyên biểu đồ của AlertsTab"""
        logger.info("Giải phóng tài nguyên biểu đồ của AlertsTab")
        if self.alerts_fig is not None:
            try:
                plt.close(self.alerts_fig)
            except Exception:
                pass

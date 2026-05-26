import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime
from views.core.ui_decorators import safe_execution
from utils.logger import logger

from views.core.theme_styles import (
    PANEL_BG, PANEL_BG_HOVER, ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED, ACCENT_AMBER,
    TEXT_MAIN, TEXT_MUTED, BORDER_COLOR
)
from views.dashboard.tabs.base_tab import BaseTab

class StatsTab(BaseTab):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, controller, **kwargs)
        
        # --- CÁC WIDGETS CỦA TAB THỐNG KÊ (Original Dashboard) ---
        # Revenue Flow Card (Thẻ biểu đồ lớn phía trên — giờ là theo danh mục)
        self.revenue_card = ctk.CTkFrame(
            self,
            fg_color=PANEL_BG,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.revenue_card.pack(fill="x", pady=(0, 20))
        
        self.rev_header_frame = ctk.CTkFrame(self.revenue_card, fg_color="transparent")
        self.rev_header_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        self.rev_title = ctk.CTkLabel(
            self.rev_header_frame,
            text="Chi tiêu theo danh mục",
            font=("Consolas", 16, "bold"),
            text_color=TEXT_MAIN
        )
        self.rev_title.pack(side="left")
        
        # Matplotlib Area cho Revenue Flow
        self.rev_chart_frame = ctk.CTkFrame(self.revenue_card, fg_color="transparent")
        self.rev_chart_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.rev_figure = plt.figure(figsize=(9, 3.2), facecolor=PANEL_BG)
        self.rev_ax = self.rev_figure.add_subplot(111)
        self.rev_ax.set_facecolor(PANEL_BG)
        self.rev_canvas = FigureCanvasTkAgg(self.rev_figure, master=self.rev_chart_frame)
        self.rev_canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Khu vực bên dưới (Chia đôi 2 cột)
        self.bottom_layout = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_layout.pack(fill="both", expand=True)
        
        self.bottom_layout.grid_columnconfigure(0, weight=1, uniform="bottom_grid")
        self.bottom_layout.grid_columnconfigure(1, weight=1, uniform="bottom_grid")
        self.bottom_layout.grid_rowconfigure(0, weight=1)
        
        # --- CỘT TRÁI: Thẻ Available (Đồ thị hình tròn/donut) ---
        self.available_card = ctk.CTkFrame(
            self.bottom_layout,
            fg_color=PANEL_BG,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.available_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.avail_header_frame = ctk.CTkFrame(self.available_card, fg_color="transparent")
        self.avail_header_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        self.avail_title = ctk.CTkLabel(
            self.avail_header_frame,
            text="Cơ cấu chi tiêu",
            font=("Consolas", 16, "bold"),
            text_color=TEXT_MAIN
        )
        self.avail_title.pack(side="left")
        
        self.avail_body = ctk.CTkFrame(self.available_card, fg_color="transparent")
        self.avail_body.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.donut_container = ctk.CTkFrame(self.avail_body, fg_color="transparent")
        self.donut_container.pack(side="left", fill="both", expand=True)
        
        self.legend_container = ctk.CTkFrame(self.avail_body, fg_color="transparent", width=160)
        self.legend_container.pack(side="right", fill="y", padx=(10, 0))
        self.legend_container.pack_propagate(False)
        
        self.donut_figure = plt.figure(figsize=(3, 3), facecolor=PANEL_BG)
        self.donut_ax = self.donut_figure.add_subplot(111)
        self.donut_ax.set_facecolor(PANEL_BG)
        self.donut_canvas = FigureCanvasTkAgg(self.donut_figure, master=self.donut_container)
        self.donut_canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # --- CỘT PHẢI: Các thẻ chỉ số xếp dọc ---
        self.right_stack = ctk.CTkFrame(self.bottom_layout, fg_color="transparent")
        self.right_stack.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.right_stack.grid_rowconfigure(0, weight=1)
        self.right_stack.grid_columnconfigure(0, weight=1)
        
        # 3. Bảng Phân tích & Dự báo Chi tiêu thông minh
        self.analysis_card = ctk.CTkFrame(
            self.right_stack,
            fg_color=PANEL_BG,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_COLOR
        )
        self.analysis_card.grid(row=0, column=0, sticky="nsew")
        
        # Tiêu đề card phân tích
        self.analysis_header = ctk.CTkFrame(self.analysis_card, fg_color="transparent")
        self.analysis_header.pack(fill="x", padx=20, pady=(15, 10))
        
        self.analysis_title = ctk.CTkLabel(
            self.analysis_header,
            text="Phân tích & Dự báo Chi tiêu 🤖",
            font=("Consolas", 15, "bold"),
            text_color=TEXT_MAIN,
            anchor="w"
        )
        self.analysis_title.pack(side="left")
        
        # Thân chứa các nhận xét động (Scrollable)
        self.insights_scroll = ctk.CTkScrollableFrame(
            self.analysis_card,
            fg_color="transparent",
            scrollbar_button_color=BORDER_COLOR,
            scrollbar_button_hover_color=PANEL_BG_HOVER,
            corner_radius=8
        )
        self.insights_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))


    def refresh(self, selected_month):
        super().refresh(selected_month)
        if self.controller:
            self.controller.refresh_dashboard()
        else:
            self.update_charts(pd.Series(dtype=float), pd.DataFrame())

    def _get_month_display_text(self):
        """Chuyển đổi tháng YYYY-MM sang dạng hiển thị tiếng Việt."""
        if not self.selected_month:
            return "Tất cả"
        try:
            d = datetime.strptime(self.selected_month, "%Y-%m")
            return f"Tháng {d.month}/{d.year}"
        except Exception:
            return self.selected_month

    @safe_execution("Lỗi vẽ biểu đồ thống kê")
    def update_charts(self, category_data, trend_data):
        """
        Vẽ lại biểu đồ thống kê chi tiêu theo danh mục trong tháng được chọn.
        """
        logger.info(f"Vẽ lại biểu đồ thống kê theo tháng: {self.selected_month}")
        self.rev_ax.clear()
        self.donut_ax.clear()
        
        # 1. Truy xuất dữ liệu gốc
        try:
            df = self.controller.service.get_all_transactions()
        except Exception:
            df = pd.DataFrame()
            
        # ==========================================
        # PHẦN 1: LỌC DỮ LIỆU THEO THÁNG ĐƯỢC CHỌN
        # ==========================================
        cat_summary = pd.Series(dtype=float)
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            
            # Lọc theo tháng được chọn
            if self.selected_month:
                try:
                    sel_dt = datetime.strptime(self.selected_month, "%Y-%m")
                    month_mask = (df['date'].dt.year == sel_dt.year) & (df['date'].dt.month == sel_dt.month)
                    df_month = df[month_mask].copy()
                except Exception:
                    df_month = df.copy()
            else:
                df_month = df.copy()
        else:
            df_month = pd.DataFrame()
        
        # Tính tổng thu nhập, chi tiêu trong tháng
        total_income = df_month[df_month['type'] == 'Thu nhập']['amount'].sum() if not df_month.empty else 0.0
        total_expense = df_month[df_month['type'] == 'Chi tiêu']['amount'].sum() if not df_month.empty else 0.0
        
        # Lấy chi tiêu theo danh mục trong tháng
        exp_df = df_month[df_month['type'] == 'Chi tiêu'].copy() if not df_month.empty else pd.DataFrame()
        if not exp_df.empty:
            cat_summary = exp_df.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        # Cập nhật tiêu đề
        month_display = self._get_month_display_text()
        self.rev_title.configure(text=f"Chi tiêu theo danh mục — {month_display}")
        self.avail_title.configure(text=f"Cơ cấu chi tiêu — {month_display}")
        
        # Cập nhật Metrics
        savings = total_income - total_expense
        savings_rate = (savings / total_income * 100) if total_income > 0 else 0.0

        # Xóa sạch các nhận xét cũ
        for widget in self.insights_scroll.winfo_children():
            widget.destroy()

        # Định nghĩa hàm phụ thêm nhận xét
        def add_insight(icon, title, desc, text_color=TEXT_MAIN):
            row_frame = ctk.CTkFrame(self.insights_scroll, fg_color="transparent")
            row_frame.pack(fill="x", pady=4, padx=2)
            
            icon_lbl = ctk.CTkLabel(row_frame, text=icon, font=("Segoe UI Emoji", 13), width=24, anchor="n")
            icon_lbl.pack(side="left", anchor="n", padx=(0, 6))
            
            content_lbl = ctk.CTkLabel(
                row_frame,
                text=f"{title} {desc}",
                font=("Consolas", 11),
                text_color=text_color,
                justify="left",
                anchor="w",
                wraplength=340
            )
            content_lbl.pack(side="left", fill="x", expand=True)

        # 1. Nhận xét Tích lũy (Savings status)
        if total_income == 0 and total_expense > 0:
            add_insight(
                "🚨", "Chưa có thu nhập:",
                f"Tháng này bạn chưa ghi nhận thu nhập nào nhưng đã chi tiêu hết {self.format_currency_vn(total_expense)}. Hãy bổ sung nguồn thu sớm!",
                text_color=ACCENT_RED
            )
        elif savings < 0:
            add_insight(
                "🚨", "Chi tiêu quá tay:",
                f"Bạn đang chi tiêu vượt mức thu nhập tháng này là {self.format_currency_vn(abs(savings))} (thâm hụt {abs(savings_rate):.1f}%). Bạn cần thắt chặt ngân sách các mục không thiết yếu ngay lập tức!",
                text_color=ACCENT_RED
            )
        elif savings_rate >= 20:
            add_insight(
                "💎", "Tích lũy xuất sắc:",
                f"Bạn đã tiết kiệm được {savings_rate:.1f}% tổng thu nhập ({self.format_currency_vn(savings)}), đạt tỷ lệ tích lũy vàng lý tưởng (>20%). Hãy tiếp tục duy trì!",
                text_color=ACCENT_GREEN
            )
        elif total_income > 0:
            add_insight(
                "👍", "Tích lũy ổn định:",
                f"Bạn đã tiết kiệm được {savings_rate:.1f}% thu nhập ({self.format_currency_vn(savings)}). Hãy cố gắng hướng tới mốc 20% tích lũy theo nguyên tắc tài chính 50/30/20.",
                text_color=ACCENT_BLUE
            )

        # 2. Cảnh báo vượt hạn mức ngân sách
        if self.selected_month and self.controller:
            try:
                usage_list = self.controller.get_usage(self.selected_month)
                over_count = 0
                warning_count = 0
                over_categories = []
                warning_categories = []
                
                for item in usage_list:
                    if item['status'] == "🔴 VƯỢT HẠN":
                        over_count += 1
                        over_categories.append(item['category'])
                    elif item['status'] == "🟡 SẮP VƯỢT":
                        warning_count += 1
                        warning_categories.append(item['category'])
                        
                if over_count > 0:
                    cats_str = ", ".join(over_categories)
                    add_insight(
                        "⚠️", "Vượt hạn mức:",
                        f"Hệ thống phát hiện {over_count} nhóm đã chi tiêu VƯỢT ngân sách tối đa: {cats_str}. Vui lòng kiểm tra lại tiến độ sử dụng ngân sách.",
                        text_color=ACCENT_RED
                    )
                if warning_count > 0:
                    cats_str = ", ".join(warning_categories)
                    add_insight(
                        "⚠️", "Sắp chạm trần:",
                        f"Có {warning_count} nhóm đã dùng hơn 80% ngân sách: {cats_str}. Hãy cân đối lại chi tiêu cho các ngày còn lại.",
                        text_color=ACCENT_AMBER
                    )
            except Exception:
                pass

        # 3. Phân tích nhóm chi nhiều nhất (Max spending category)
        if not cat_summary.empty and cat_summary.sum() > 0:
            highest_cat = cat_summary.index[0]
            highest_amt = cat_summary.values[0]
            highest_pct = (highest_amt / total_expense * 100) if total_expense > 0 else 0.0
            
            if highest_pct >= 25:
                add_insight(
                    "🔥", "Chi tiêu trọng điểm:",
                    f"Tháng này bạn đã chi tiêu quá nhiều cho nhóm '{highest_cat}', chiếm đến {highest_pct:.0f}% tổng chi tiêu ({self.format_currency_vn(highest_amt)}). Hãy cân nhắc xem các khoản này có thực sự cần thiết không.",
                    text_color=ACCENT_AMBER
                )
            else:
                add_insight(
                    "📊", "Phân bổ chi tiêu:",
                    f"Nhóm chi tiêu lớn nhất là '{highest_cat}' chiếm {highest_pct:.0f}% tổng chi ({self.format_currency_vn(highest_amt)}). Cơ cấu phân bổ chi tiêu của bạn nhìn chung khá đồng đều.",
                    text_color=TEXT_MUTED
                )

        # 4. Dự báo chi tiêu (Spending Forecast)
        try:
            from datetime import datetime
            now = datetime.now()
            selected_dt = datetime.strptime(self.selected_month, "%Y-%m") if self.selected_month else None
            
            if selected_dt and selected_dt.year == now.year and selected_dt.month == now.month:
                import calendar
                current_day = now.day
                _, days_in_month = calendar.monthrange(now.year, now.month)
                
                # Tránh chia cho 0
                if current_day > 0 and total_expense > 0:
                    forecasted_expense = (total_expense / current_day) * days_in_month
                    forecasted_saving = total_income - forecasted_expense
                    
                    forecast_desc = f"Dựa trên tốc độ hiện tại ({current_day}/{days_in_month} ngày), dự báo tổng chi tiêu cả tháng sẽ chạm mốc {self.format_currency_vn(forecasted_expense)}."
                    if forecasted_saving < 0:
                        add_insight(
                            "🔮", "Dự báo cuối tháng:",
                            f"{forecast_desc} Bạn có nguy cơ thâm hụt tài chính khoảng {self.format_currency_vn(abs(forecasted_saving))}! Cần cắt giảm các chi phí không thiết yếu ngay.",
                            text_color=ACCENT_RED
                        )
                    else:
                        add_insight(
                            "🔮", "Dự báo cuối tháng:",
                            f"{forecast_desc} Dự kiến bạn vẫn tích lũy được {self.format_currency_vn(forecasted_saving)}.",
                            text_color=ACCENT_GREEN
                        )
        except Exception:
            pass

        # 5. Mẹo tài chính ngẫu nhiên dựa trên tình hình chi tiêu
        if total_income > 0:
            if savings_rate < 15:
                add_insight(
                    "💡", "Lời khuyên tài chính:",
                    "Thử áp dụng quy tắc 50/30/20 (50% thiết yếu, 30% linh hoạt, 20% tích lũy) bằng cách lên kế hoạch ngân sách cụ thể ngay đầu tháng.",
                    text_color=TEXT_MUTED
                )
            else:
                add_insight(
                    "💡", "Lời khuyên tích lũy:",
                    "Bạn đang tích lũy rất tốt! Hãy xem xét chuyển phần thặng dư này sang các tài sản sinh lời (gửi tiết kiệm, đầu tư) để tận dụng lãi kép.",
                    text_color=TEXT_MUTED
                )

        # ==========================================
        # CHUẨN BỊ DỮ LIỆU & MÀU SẮC ĐA DẠNG CHO BIỂU ĐỒ
        # ==========================================
        assigned_colors = []
        labels = []
        values = []
        if not cat_summary.empty and cat_summary.sum() > 0:
            # Hiển thị tối đa 7 danh mục lớn nhất, gom phần còn lại thành "Khác"
            if len(cat_summary) > 7:
                top_cats = cat_summary.head(6)
                other_sum = cat_summary.iloc[6:].sum()
                cat_summary = pd.concat([top_cats, pd.Series({"Khác": other_sum})])
            
            labels = cat_summary.index.tolist()
            values = cat_summary.values
            
            # Bảng màu sắc rực rỡ, hiện đại và đa dạng thiết kế riêng tối ưu cho giao diện Dark Mode
            chart_colors = [
                "#10B981",  # Xanh ngọc lục bảo (Emerald Green)
                "#3B82F6",  # Xanh dương sáng (Vibrant Blue)
                "#8B5CF6",  # Tím ánh oải hương (Vibrant Purple)
                "#EC4899",  # Hồng cánh sen rực rỡ (Vibrant Pink)
                "#F59E0B",  # Vàng hổ phách (Vibrant Amber)
                "#06B6D4",  # Xanh ngọc thanh khiết (Vibrant Cyan)
                "#F97316",  # Cam rực lửa (Vibrant Orange)
                "#F43F5E",  # Đỏ hoa hồng kiêu kỳ (Rose Red)
                "#84CC16",  # Xanh lá mạ tươi mới (Lime Green)
                "#14B8A6"   # Xanh mòng két mộc mạc (Deep Teal)
            ]
            
            for i, label in enumerate(labels):
                if label == "Khác":
                    assigned_colors.append("#64748B")  # Màu xám Slate trung tính, tinh tế cho danh mục "Khác"
                else:
                    assigned_colors.append(chart_colors[i % len(chart_colors)])

        # ==========================================
        # PHẦN 2: DỰNG HÌNH BIỂU ĐỒ CỘT THEO DANH MỤC (BAR CHART)
        # ==========================================
        if not cat_summary.empty and cat_summary.sum() > 0:
            n_bars = len(values)
            
            # Thiết lập trục biểu đồ
            self.rev_ax.grid(axis='y', color=BORDER_COLOR, linestyle='-', linewidth=0.8, alpha=0.15, zorder=1)
            
            # Vẽ các cột
            for i in range(n_bars):
                val = values[i]
                color = assigned_colors[i]
                
                # Vẽ cột: Khối màu đặc rực rỡ
                self.rev_ax.bar(
                    i, val, width=0.45, color=color, edgecolor=color,
                    linewidth=1, align='center', zorder=3
                )
                
                # Vẽ điểm tròn tinh tế ở đỉnh cột
                self.rev_ax.scatter(
                    i, val, s=120, facecolors=color, edgecolors=TEXT_MAIN,
                    linewidths=3.5, zorder=5
                )
                
                # Bong bóng hiển thị giá trị tiền tệ rút gọn
                val_str = self.format_currency_short(val)
                
                xytext_val = (0, 20) if val >= 0 else (0, -20)
                va_val = 'bottom' if val >= 0 else 'top'
                
                self.rev_ax.annotate(
                    val_str,
                    xy=(i, val),
                    xytext=xytext_val,
                    textcoords="offset points",
                    ha='center',
                    va=va_val,
                    fontsize=9.5,
                    fontweight='bold',
                    color=TEXT_MAIN,
                    family='Consolas',
                    bbox=dict(
                        boxstyle="round,pad=0.4",
                        facecolor=PANEL_BG_HOVER,
                        edgecolor=BORDER_COLOR,
                        linewidth=1.2,
                        alpha=0.95
                    ),
                    arrowprops=dict(
                        arrowstyle="-",
                        color=BORDER_COLOR,
                        linewidth=1
                    ),
                    zorder=6
                )
            
            # Định dạng các trục tọa độ
            for spine in ['top', 'right', 'left', 'bottom']:
                self.rev_ax.spines[spine].set_visible(False)
            
            # Rút gọn tên danh mục nếu quá dài để hiển thị sắc nét trên trục hoành
            short_labels = []
            for lbl in labels:
                if len(lbl) > 10:
                    short_labels.append(lbl[:9] + "..")
                else:
                    short_labels.append(lbl)
                
            self.rev_ax.set_xticks(range(n_bars))
            self.rev_ax.set_xticklabels(short_labels, color=TEXT_MUTED, fontsize=10, family='Consolas')
            self.rev_ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: self.format_currency_short(y)))
            
            self.rev_ax.tick_params(axis='both', which='both', length=0)
            self.rev_ax.tick_params(axis='y', colors=TEXT_MUTED, labelsize=9)
            
            # Đảm bảo font chữ đồng bộ
            for label in self.rev_ax.get_yticklabels():
                label.set_fontproperties({'family': 'Consolas', 'size': 9})
            for label in self.rev_ax.get_xticklabels():
                label.set_fontproperties({'family': 'Consolas', 'size': 10})
        else:
            self.rev_ax.text(0.5, 0.5, "Chưa có dữ liệu chi tiêu trong tháng này", color=TEXT_MUTED, ha='center', va='center', fontsize=12, family='Consolas')
            self.rev_ax.axis('off')

        # ==========================================
        # PHẦN 3: DỰNG HÌNH BIỂU ĐỒ TRÒN (DONUT CHART)
        # ==========================================
        if not cat_summary.empty and cat_summary.sum() > 0:
            donut_values = values.tolist() if hasattr(values, "tolist") else list(values)
            
            # Vẽ biểu đồ donut sử dụng bảng màu đồng bộ đã thiết lập
            wedges, texts = self.donut_ax.pie(
                donut_values,
                colors=assigned_colors,
                startangle=90,
                counterclock=False,
                wedgeprops=dict(width=0.32, edgecolor=PANEL_BG, linewidth=3)
            )
            
            # Tính % danh mục lớn nhất hiển thị ở trung tâm donut
            highest_pct = donut_values[0] / sum(donut_values) * 100 if sum(donut_values) > 0 else 0.0
            center_text = f"{highest_pct:.0f}%"
                
            self.donut_ax.text(
                0, 0, center_text,
                ha='center', va='center',
                fontsize=20, fontweight='bold',
                color=TEXT_MAIN, family='Consolas'
            )
            
            self.donut_ax.axis('equal')
            
            # Cập nhật bảng chú thích legend cực kỳ sắc nét bằng màu sắc đồng bộ
            self.update_native_legend(labels, donut_values, assigned_colors)
        else:
            self.donut_ax.text(
                0, 0, "0%",
                ha='center', va='center',
                fontsize=18, fontweight='bold',
                color=TEXT_MUTED, family='Consolas'
            )
            self.donut_ax.axis('equal')
            # Xóa sạch Legend cũ
            for widget in self.legend_container.winfo_children():
                widget.destroy()
                
        # Cập nhật các Canvas Matplotlib lên màn hình
        self.rev_figure.subplots_adjust(left=0.08, right=0.96, top=0.82, bottom=0.18)
        self.donut_figure.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        
        self.rev_canvas.draw()
        self.donut_canvas.draw()

    def update_native_legend(self, labels, values, colors):
        """Vẽ lại bảng chú giải bằng widget CustomTkinter cực kỳ sắc nét ở bên phải đồ thị."""
        for widget in self.legend_container.winfo_children():
            widget.destroy()
            
        total = sum(values)
        
        # Nhãn tiêu đề cho danh sách
        title_lbl = ctk.CTkLabel(
            self.legend_container,
            text="Phân bổ",
            font=("Consolas", 12, "bold"),
            text_color=TEXT_MUTED,
            anchor="w"
        )
        title_lbl.pack(fill="x", pady=(5, 8))
        
        for i, (label, val) in enumerate(zip(labels, values)):
            pct = val / total * 100 if total > 0 else 0.0
            color = colors[i % len(colors)]
            
            # Container từng dòng
            row = ctk.CTkFrame(self.legend_container, fg_color="transparent")
            row.pack(fill="x", pady=4)
            
            # Badge màu sắc vuông nhỏ bo tròn nhẹ
            badge = ctk.CTkFrame(row, width=12, height=12, fg_color=color, corner_radius=3)
            badge.pack(side="left", padx=(2, 6))
            badge.pack_propagate(False)
            
            # Tên nhãn và phần trăm tương ứng
            short_lbl = label[:11] + ".." if len(label) > 11 else label
            text_lbl = f"{short_lbl} ({pct:.0f}%)"
            
            lbl = ctk.CTkLabel(
                row,
                text=text_lbl,
                font=("Consolas", 11),
                text_color=TEXT_MAIN,
                anchor="w"
            )
            lbl.pack(side="left", fill="x", expand=True)

    def cleanup(self):
        """Dọn dẹp bộ nhớ biểu đồ khi đóng cửa sổ."""
        logger.info("Giải phóng tài nguyên biểu đồ của StatsTab")
        for fig in [self.rev_figure, self.donut_figure]:
            if fig is not None:
                try:
                    plt.close(fig)
                except Exception:
                    pass

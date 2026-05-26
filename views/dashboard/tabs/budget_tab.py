import customtkinter as ctk
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import tkinter.messagebox as mb
from utils.logger import logger

from views.core.theme_styles import (
    BG_COLOR, PANEL_BG, PANEL_BG_HOVER, ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED, ACCENT_AMBER,
    TEXT_MAIN, TEXT_MUTED, BORDER_COLOR, FONT_MAIN, FONT_LABEL
)
from views.dashboard.tabs.base_tab import BaseTab
from views.core.ui_decorators import format_entry_amount

class BudgetTab(BaseTab):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, controller, **kwargs)
        
        self.budget_fig = None
        self.budget_ax = None
        self.budget_canvas = None
        self._budget_cat_var = tk.StringVar()
        
    def refresh(self, selected_month):
        super().refresh(selected_month)
        self._render_budget_tab()
        
    def _render_budget_tab(self):
        """Dựng giao diện cho tab Hạn mức ngân sách."""
        # 1. Xóa sạch widget cũ
        for widget in self.winfo_children():
            widget.destroy()
            
        # 2. Kiểm tra xem có đang chọn tháng cụ thể không
        if not self._check_month_selected():
            return
            
        db_month = self.selected_month
        usage_data = self.controller.get_usage(db_month) if self.controller else []
        
        # 3. Tạo bố cục 2 cột (Trái: Form thiết lập, Phải: Biểu đồ so sánh hạn mức)
        self.grid_columnconfigure(0, weight=4, uniform="budget_col")
        self.grid_columnconfigure(1, weight=6, uniform="budget_col")
        self.grid_rowconfigure(0, weight=1)
        
        # CỘT TRÁI: FORM PANEL
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
            text="Thiết lập hạn mức",
            font=("Consolas", 16, "bold"),
            text_color=TEXT_MAIN,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 15))
        
        # Chọn danh mục
        ctk.CTkLabel(
            left_panel,
            text="Danh mục chi tiêu:",
            font=FONT_LABEL,
            text_color=TEXT_MUTED,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(5, 5))
        
        cats = self.controller.get_categories() if self.controller else []
        # Loại bỏ "Thêm mới..." từ danh sách nếu có
        cats = [c for c in cats if c != "Thêm mới..."]
        if cats and not self._budget_cat_var.get():
            self._budget_cat_var.set(cats[0])
            
        self.budget_cat_menu = ctk.CTkOptionMenu(
            left_panel,
            variable=self._budget_cat_var,
            values=cats,
            height=38,
            font=FONT_MAIN,
            fg_color=BG_COLOR,
            button_color=BORDER_COLOR,
            button_hover_color=PANEL_BG_HOVER,
            command=lambda _: self._update_budget_entry_from_selection()
        )
        self.budget_cat_menu.pack(fill="x", padx=20, pady=(0, 15))
        
        # Nhập hạn mức tiền
        ctk.CTkLabel(
            left_panel,
            text="Hạn mức tối đa (đ):",
            font=FONT_LABEL,
            text_color=TEXT_MUTED,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(5, 5))
        
        self.budget_amt_entry = ctk.CTkEntry(
            left_panel,
            height=38,
            placeholder_text="Ví dụ: 5,000,000",
            font=FONT_MAIN,
            fg_color=BG_COLOR,
            border_color=BORDER_COLOR
        )
        self.budget_amt_entry.pack(fill="x", padx=20, pady=(0, 20))
        self.budget_amt_entry.bind("<KeyRelease>", lambda event: format_entry_amount(self.budget_amt_entry, event))
        
        # Tự động điền trước hạn mức hiện có khi vừa render tab
        self._update_budget_entry_from_selection()
        
        # Nút Lưu
        save_btn = ctk.CTkButton(
            left_panel,
            text="Lưu hạn mức",
            font=("Consolas", 13, "bold"),
            fg_color=ACCENT_BLUE,
            hover_color=PANEL_BG_HOVER,
            text_color=TEXT_MAIN,
            height=38,
            command=lambda: self._save_budget(db_month)
        )
        save_btn.pack(fill="x", padx=20, pady=(0, 6))
        
        # Nút Xóa
        delete_btn = ctk.CTkButton(
            left_panel,
            text="Xóa hạn mức",
            font=("Consolas", 13, "bold"),
            fg_color="transparent",
            hover_color="#7F1D1D",
            text_color="#F43F5E",
            border_width=1,
            border_color="#F43F5E",
            height=38,
            command=lambda: self._delete_budget(db_month)
        )
        delete_btn.pack(fill="x", padx=20, pady=(0, 4))
        
        # Đường kẻ phân cách
        divider = ctk.CTkFrame(left_panel, height=1, fg_color=BORDER_COLOR)
        divider.pack(fill="x", padx=20, pady=(4, 4))
        
        # Nút sao chép tháng trước
        copy_btn = ctk.CTkButton(
            left_panel,
            text="Sao chép tháng trước",
            font=("Consolas", 13, "bold"),
            fg_color="transparent",
            hover_color=PANEL_BG_HOVER,
            text_color=TEXT_MUTED,
            border_width=1,
            border_color=BORDER_COLOR,
            height=38,
            command=lambda: self._copy_last_month(db_month)
        )
        copy_btn.pack(fill="x", padx=20, pady=(0, 6))
        
        # ─── DANH SÁCH CHỌN NHANH HẠN MỨC HIỆN TẠI (Quick-Edit List) ───
        ctk.CTkLabel(
            left_panel,
            text="Hạn mức đang hoạt động:",
            font=FONT_LABEL,
            text_color=TEXT_MUTED,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(4, 4))
        
        scroll_frame = ctk.CTkScrollableFrame(
            left_panel,
            fg_color=BG_COLOR,
            scrollbar_button_color=BORDER_COLOR,
            scrollbar_button_hover_color=PANEL_BG_HOVER,
            corner_radius=8,
            height=280
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        if not usage_data:
            ctk.CTkLabel(
                scroll_frame,
                text="Chưa thiết lập hạn mức",
                font=("Consolas", 11),
                text_color=TEXT_MUTED
            ).pack(pady=15)
        else:
            # Tiêu đề bảng trong scroll_frame
            header_row = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            header_row.pack(fill="x", pady=(2, 5))
            
            header_row.grid_columnconfigure(0, weight=4, uniform="budget_tbl")
            header_row.grid_columnconfigure(1, weight=3, uniform="budget_tbl")
            header_row.grid_columnconfigure(2, weight=3, uniform="budget_tbl")
            
            ctk.CTkLabel(header_row, text="Danh mục", font=("Consolas", 10, "bold"), text_color=TEXT_MUTED, anchor="w").grid(row=0, column=0, sticky="ew", padx=(5, 2))
            ctk.CTkLabel(header_row, text="Hạn mức", font=("Consolas", 10, "bold"), text_color=TEXT_MUTED, anchor="e").grid(row=0, column=1, sticky="ew", padx=2)
            ctk.CTkLabel(header_row, text="Thực chi", font=("Consolas", 10, "bold"), text_color=TEXT_MUTED, anchor="e").grid(row=0, column=2, sticky="ew", padx=(2, 5))
            
            for b_item in usage_data:
                cat_name = b_item['category']
                lim_val = b_item['limit']
                spent_val = b_item['spent']
                
                # Rút gọn tên danh mục nếu quá dài
                cat_disp = cat_name[:14] + ".." if len(cat_name) > 14 else cat_name
                
                # Container từng dòng
                row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent", corner_radius=6)
                row_frame.pack(fill="x", pady=1)
                
                row_frame.grid_columnconfigure(0, weight=4, uniform="budget_tbl")
                row_frame.grid_columnconfigure(1, weight=3, uniform="budget_tbl")
                row_frame.grid_columnconfigure(2, weight=3, uniform="budget_tbl")
                
                # Tạo các Label cột (rút gọn suffix ' đ' để tránh tràn chữ)
                lbl_cat = ctk.CTkLabel(row_frame, text=cat_disp, font=("Consolas", 11), text_color=TEXT_MAIN, anchor="w", cursor="hand2")
                lbl_cat.grid(row=0, column=0, sticky="ew", padx=(5, 2))
                
                lbl_lim = ctk.CTkLabel(
                    row_frame, 
                    text=self.format_currency_vn(lim_val).replace(" đ", ""), 
                    font=("Consolas", 11), 
                    text_color=TEXT_MAIN, 
                    anchor="e", 
                    cursor="hand2"
                )
                lbl_lim.grid(row=0, column=1, sticky="ew", padx=2)
                
                is_over = spent_val > lim_val
                spent_color = ACCENT_RED if is_over else TEXT_MAIN
                lbl_spent = ctk.CTkLabel(
                    row_frame, 
                    text=self.format_currency_vn(spent_val).replace(" đ", ""), 
                    font=("Consolas", 11, "bold" if is_over else "normal"), 
                    text_color=spent_color, 
                    anchor="e", 
                    cursor="hand2"
                )
                lbl_spent.grid(row=0, column=2, sticky="ew", padx=(2, 5))
                
                # Thiết lập hover hiệu ứng động
                def make_hover(rf=row_frame):
                    rf.bind("<Enter>", lambda e, r=rf: r.configure(fg_color=PANEL_BG_HOVER))
                    rf.bind("<Leave>", lambda e, r=rf: r.configure(fg_color="transparent"))
                make_hover()
                
                # Nhấp chọn dòng để sửa
                def bind_click(widget, c=cat_name, l=lim_val):
                    widget.bind("<Button-1>", lambda e: self._select_budget_for_edit(c, l))
                
                for w in [row_frame, lbl_cat, lbl_lim, lbl_spent]:
                    bind_click(w)
        
        # CỘT PHẢI: BIỂU ĐỒ SO SÁNH HẠN MỨC
        right_panel = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        
        chart_card = ctk.CTkFrame(
            right_panel,
            fg_color=PANEL_BG,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_COLOR
        )
        chart_card.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            chart_card,
            text="Tiến độ sử dụng hạn mức",
            font=("Consolas", 16, "bold"),
            text_color=TEXT_MAIN,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(20, 15))
        
        if not usage_data:
            empty_lbl = ctk.CTkLabel(
                chart_card,
                text="Chưa thiết lập hạn mức nào cho tháng này.",
                font=("Consolas", 13),
                text_color=TEXT_MUTED,
                justify="center"
            )
            empty_lbl.pack(expand=True, pady=40)
            return
            
        # Khởi tạo hoặc vẽ lại Figure
        if self.budget_fig is None:
            self.budget_fig = plt.figure(figsize=(5, 4), facecolor=PANEL_BG)
            self.budget_ax = self.budget_fig.add_subplot(111)
        else:
            self.budget_ax.clear()
            
        self.budget_ax.set_facecolor(PANEL_BG)
        
        # Lọc và đảo ngược danh sách để vẽ từ trên xuống dưới
        categories = [item['category'] for item in usage_data]
        limits = [item['limit'] for item in usage_data]
        spent = [item['spent'] for item in usage_data]
        
        categories.reverse()
        limits.reverse()
        spent.reverse()
        
        y_indices = np.arange(len(categories))
        height = 0.3
        
        # Vẽ cột Hạn mức (màu Slate tối)
        self.budget_ax.barh(y_indices - 0.17, limits, height, label='Hạn mức', color='#475569', edgecolor='none')
        
        # Xác định màu sắc động cho cột Thực chi
        spent_colors = []
        for s, lim in zip(spent, limits):
            pct = (s / lim * 100) if lim > 0 else 0.0
            if pct >= 100:
                spent_colors.append(ACCENT_RED)
            elif pct >= 80:
                spent_colors.append(ACCENT_AMBER)
            else:
                spent_colors.append(ACCENT_GREEN)
                
        # Vẽ cột Thực chi
        self.budget_ax.barh(y_indices + 0.17, spent, height, label='Thực chi', color=spent_colors, edgecolor='none')
        
        # Cấu hình trục và hiển thị
        self.budget_ax.set_yticks(y_indices)
        
        short_labels = []
        for lbl in categories:
            if len(lbl) > 14:
                short_labels.append(lbl[:12] + "..")
            else:
                short_labels.append(lbl)
                
        self.budget_ax.set_yticklabels(short_labels, color=TEXT_MAIN, fontsize=10, family='Consolas')
        self.budget_ax.tick_params(axis='both', which='both', length=0)
        self.budget_ax.tick_params(axis='y', colors=TEXT_MAIN, labelsize=10)
        self.budget_ax.tick_params(axis='x', bottom=False, labelbottom=False)
        
        # Mở rộng giới hạn trục hoành trục X một chút để không bị đè văn bản nhãn số liệu
        max_val_all = max(max(limits), max(spent)) if (limits or spent) else 1000
        if limits:
            self.budget_ax.set_xlim(0, max_val_all * 1.55)
            
        # Ẩn khung viền
        for spine in ['top', 'right', 'left', 'bottom']:
            self.budget_ax.spines[spine].set_visible(False)
            
        # Thêm nhãn tiền tệ rút gọn bên cạnh cột
        padding = max_val_all * 0.02
        for i, (s, lim) in enumerate(zip(spent, limits)):
            pct = (s / lim * 100) if lim > 0 else 0.0
            pct_str = f"{pct:.0f}%"
            
            is_over = s >= lim and lim > 0
            if is_over:
                label_text = f"{self.format_currency_short(s)} / {self.format_currency_short(lim)} ({pct_str})"
                text_color = ACCENT_RED
                font_weight = 'bold'
                font_size = 10
            elif pct >= 80:
                label_text = f"{self.format_currency_short(s)} / {self.format_currency_short(lim)} ({pct_str})"
                text_color = ACCENT_AMBER
                font_weight = 'bold'
                font_size = 10
            else:
                label_text = f"{self.format_currency_short(s)} / {self.format_currency_short(lim)} ({pct_str})"
                text_color = TEXT_MAIN
                font_weight = 'normal'
                font_size = 10
                
            max_val = max(s, lim)
            self.budget_ax.text(
                max_val + padding, i, label_text,
                va='center', ha='left', fontsize=font_size, color=text_color, family='Consolas', fontweight=font_weight
            )
            
        # Thêm Legend chú giải
        self.budget_ax.legend(
            loc='upper right', bbox_to_anchor=(1.0, 1.15),
            ncol=2, frameon=False, facecolor=PANEL_BG, labelcolor=TEXT_MAIN,
            prop={'family': 'Consolas', 'size': 9}
        )
        
        # Áp dụng font và màu sắc sắc nét
        for label in self.budget_ax.get_yticklabels():
            label.set_fontproperties({'family': 'Consolas', 'size': 10, 'weight': 'bold'})
            label.set_color(TEXT_MAIN)
            
        self.budget_fig.subplots_adjust(left=0.22, right=0.70, top=0.88, bottom=0.08)
        
        # Nhúng vào Canvas
        self.budget_canvas = FigureCanvasTkAgg(self.budget_fig, master=chart_card)
        self.budget_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        self.budget_canvas.draw()

    def _save_budget(self, db_month):
        """Lưu hạn mức ngân sách từ form nhập."""
        cat = self._budget_cat_var.get()
        if not cat:
            self.show_error("Lỗi", "Vui lòng chọn danh mục chi tiêu!")
            return
            
        amt_str = self.budget_amt_entry.get().replace(",", "").replace(".", "").strip()
        if not amt_str:
            self.show_error("Lỗi", "Vui lòng nhập số tiền hạn mức!")
            return
            
        try:
            amt = float(amt_str)
            if amt < 0:
                raise ValueError()
        except ValueError:
            self.show_error("Lỗi", "Số tiền hạn mức phải là số dương hợp lệ!")
            return
            
        try:
            self.controller.set_budget(cat, db_month, amt, overwrite=True)
            self.show_message("Thành công", f"Đã cập nhật hạn mức nhóm '{cat}' thành công!")
            self.budget_amt_entry.delete(0, tk.END)
            self._render_budget_tab()
        except Exception as e:
            self.show_error("Lỗi", f"Không thể lưu hạn mức ngân sách: {str(e)}")

    def _delete_budget(self, db_month):
        """Xóa hạn mức ngân sách của danh mục đang chọn."""
        cat = self._budget_cat_var.get()
        if not cat:
            self.show_error("Lỗi", "Vui lòng chọn danh mục chi tiêu cần xóa hạn mức!")
            return
            
        confirm = mb.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa hạn mức của nhóm '{cat}' trong tháng {db_month} không?",
            parent=self,
            icon="warning"
        )
        if not confirm:
            return
            
        try:
            self.controller.delete_budget(cat, db_month)
            self.show_message("Thành công", f"Đã xóa hạn mức nhóm '{cat}' thành công!")
            self.budget_amt_entry.delete(0, tk.END)
            self._render_budget_tab()
        except Exception as e:
            self.show_error("Lỗi", f"Không thể xóa hạn mức ngân sách: {str(e)}")

    def _copy_last_month(self, db_month):
        """Sao chép hạn mức từ tháng trước sang tháng hiện tại."""
        try:
            copied_count = self.controller.copy_budget_from_last_month(db_month)
            if copied_count > 0:
                self.show_message("Thành công", f"Đã sao chép thành công {copied_count} nhóm hạn mức từ tháng trước!")
                self._render_budget_tab()
            else:
                self.show_message("Thông báo", "Không tìm thấy dữ liệu hạn mức tháng trước hoặc tất cả hạn mức đã tồn tại.")
        except Exception as e:
            self.show_error("Lỗi", f"Lỗi sao chép hạn mức: {str(e)}")



    def _update_budget_entry_from_selection(self):
        """Tự động cập nhật ô nhập hạn mức khi thay đổi lựa chọn danh mục trong OptionMenu."""
        cat = self._budget_cat_var.get()
        if not cat:
            self.budget_amt_entry.delete(0, tk.END)
            return
            
        db_month = self.selected_month
        current_limit = None
        if self.controller:
            try:
                current_limit = self.controller.service.get_budget(cat, db_month)
            except Exception:
                current_limit = None
                
        self.budget_amt_entry.delete(0, tk.END)
        if current_limit is not None and current_limit > 0:
            formatted = f"{int(current_limit):,}"
            self.budget_amt_entry.insert(0, formatted)

    def _select_budget_for_edit(self, category, limit_value):
        """Chọn nhanh một danh mục hạn mức để chỉnh sửa từ danh sách."""
        self._budget_cat_var.set(category)
        formatted_val = f"{int(limit_value):,}"
        self.budget_amt_entry.delete(0, tk.END)
        self.budget_amt_entry.insert(0, formatted_val)
        self.budget_amt_entry.focus()

    def cleanup(self):
        """Dọn dẹp bộ nhớ biểu đồ khi đóng cửa sổ."""
        logger.info("Giải phóng tài nguyên biểu đồ của BudgetTab")
        if self.budget_fig is not None:
            try:
                plt.close(self.budget_fig)
            except Exception:
                pass

# Nhập các thư viện cần thiết
import customtkinter as ctk
import tkinter as tk
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from views.core.theme_styles import (
    BG_COLOR, PANEL_BG, PANEL_BG_HOVER,
    TEXT_MAIN, TEXT_MUTED, BORDER_COLOR, FONT_MAIN
)
from utils.logger import logger
from views.dashboard.tabs import StatsTab, BudgetTab, AlertsTab, SavingsTab

# Khai báo lớp DashboardWindow hiển thị giao diện phân tích biểu đồ thống kê
class DashboardWindow(ctk.CTkToplevel):
    # Khởi tạo cửa sổ thống kê
    def __init__(self, master, controller, initial_tab="stats", **kwargs):
        """
        Cửa sổ thống kê phân tích trực quan hóa dữ liệu chi tiêu tích hợp Ngân sách & Tiết kiệm.
        """
        super().__init__(master, **kwargs)
        self.title("Bảng thống kê")
        self.geometry("1080x700")
        self.transient(master)
        self.configure(fg_color=BG_COLOR)
        
        # Căn giữa cửa sổ so với cửa sổ cha
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (980 // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (700 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.controller = controller
        self.selected_month = None  # Tháng đang được chọn (format: "YYYY-MM")
        self.available_months = []  # Danh sách tháng có dữ liệu
        
        # Thiết lập style tối cho Matplotlib
        plt.style.use('dark_background')
        
        # Bind sự kiện đóng cửa sổ để giải phóng bộ nhớ
        self.bind("<Destroy>", self._on_window_destroy)
        
        # Lấy danh sách tháng có dữ liệu
        self._load_available_months()
        
        # --- THIẾT KẾ BỐ CỤC ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=25, pady=20)
        
        # 1. Header Title
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 10))
        
        self.header_label = ctk.CTkLabel(
            self.header_frame,
            text="Bảng thống kê",
            font=("Consolas", 26, "bold"),
            text_color=TEXT_MAIN,
            anchor="w"
        )
        self.header_label.pack(side="left")
        
        # 1.5 Thanh công cụ điều khiển (Chứa các Tab bên trái và Chọn tháng bên phải ngang hàng)
        self.toolbar_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.toolbar_frame.pack(fill="x", pady=(0, 20))
        
        # Vùng chứa các nút Tab bấm riêng biệt
        self.tabs_container = ctk.CTkFrame(self.toolbar_frame, fg_color="transparent")
        self.tabs_container.pack(side="left")
        
        # Trình chọn tháng ở góc phải hàng ngang với các Tab
        month_frame = ctk.CTkFrame(self.toolbar_frame, fg_color="transparent")
        month_frame.pack(side="right")
        ctk.CTkLabel(month_frame, text="Tháng:", font=FONT_MAIN, text_color=TEXT_MUTED).pack(side="left", padx=(0, 6))
        
        # Chuyển đổi danh sách tháng sang format hiển thị MM/YYYY
        self._month_display_values = ["Tất cả"]
        for m in self.available_months:
            try:
                d = datetime.strptime(m, "%Y-%m")
                self._month_display_values.append(f"{d.month:02d}/{d.year}")
            except Exception:
                self._month_display_values.append(m)
        
        # Tìm giá trị mặc định hiển thị
        default_display = "Tất cả"
        if self.selected_month:
            try:
                d = datetime.strptime(self.selected_month, "%Y-%m")
                default_display = f"{d.month:02d}/{d.year}"
            except Exception:
                pass
        
        self._month_var = tk.StringVar(value=default_display)
        self.month_option_menu = ctk.CTkOptionMenu(
            month_frame,
            values=self._month_display_values,
            variable=self._month_var,
            width=120,
            height=30,
            font=FONT_MAIN,
            command=lambda _: self._on_month_changed()
        )
        self.month_option_menu.pack(side="left")
        
        self.icons = getattr(master, 'icons', {})
        self.main_app = master
        self.show_message = getattr(master, 'show_message', lambda t, m: None)
        self.show_error = getattr(master, 'show_error', lambda t, m: None)
        
        self.tab_buttons = {}
        self.active_tab = initial_tab
        
        tabs_config = [
            (" Thống kê", "stats", "stats"),
            (" Hạn mức", "budget", "budget"),
            (" Cảnh báo", "alerts", "alert"),
            (" Tiết kiệm", "savings", "savings")
        ]
        
        for lbl, key, icon_key in tabs_config:
            is_active = (key == self.active_tab)
            b = ctk.CTkButton(
                self.tabs_container, 
                text=lbl, 
                image=self.icons.get(icon_key), 
                font=("Consolas", 13, "bold"),
                fg_color=PANEL_BG if is_active else "transparent", 
                hover_color=PANEL_BG_HOVER,
                text_color=TEXT_MAIN if is_active else TEXT_MUTED,
                border_width=1,
                border_color=BORDER_COLOR,
                height=36, 
                corner_radius=8,
                command=lambda k=key: self._switch_tab(k)
            )
            b.pack(side="left", padx=6, pady=2)
            self.tab_buttons[key] = b
            
        # 2. Vùng chứa nội dung các Tabs
        self.content_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)
        
        # Khởi tạo các Tab components
        self.tabs = {}
        self.tabs["stats"] = StatsTab(self.content_container, self.controller)
        self.tabs["budget"] = BudgetTab(self.content_container, self.controller)
        self.tabs["alerts"] = AlertsTab(self.content_container, self.controller)
        self.tabs["savings"] = SavingsTab(self.content_container, self.controller)
        
        for key, tab_instance in self.tabs.items():
            tab_instance.grid(row=0, column=0, sticky="nsew")
            
        # Mở tab mặc định được chỉ định
        self._switch_tab(initial_tab)

    def _on_window_destroy(self, event):
        """Giải phóng các tài nguyên biểu đồ khi đóng cửa sổ."""
        if event.widget == self:
            logger.info("Giải phóng tài nguyên biểu đồ của DashboardWindow và các Tabs con")
            for key, tab in self.tabs.items():
                try:
                    tab.cleanup()
                except Exception as e:
                    logger.error(f"Lỗi dọn dẹp tab {key}: {e}")

    def _load_available_months(self):
        """Lấy danh sách các tháng có dữ liệu giao dịch từ database."""
        try:
            df = self.controller.service.get_all_transactions()
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                # Lấy danh sách tháng duy nhất (format YYYY-MM), sắp xếp giảm dần
                months = df['date'].dt.to_period('M').unique()
                self.available_months = sorted([str(m) for m in months], reverse=True)
                
                # Mặc định chọn Tất cả
                self.selected_month = None
            else:
                self.available_months = []
                self.selected_month = None
        except Exception:
            self.available_months = []
            self.selected_month = None
            
    def _on_month_changed(self):
        """Callback khi người dùng chọn tháng từ OptionMenu."""
        ui_month = self._month_var.get()  # Format: MM/YYYY hoặc "Tất cả"
        if ui_month == "Tất cả":
            self.selected_month = None
        elif '/' in ui_month:
            m, y = ui_month.split('/')
            self.selected_month = f"{y}-{m}"
        else:
            self.selected_month = ui_month
        
        # Làm mới dữ liệu cho tab hiện tại
        self._refresh_active_tab()
        
    def _switch_tab(self, key):
        """Chuyển đổi qua lại giữa các Tab."""
        self.active_tab = key
        # Cập nhật style nút tab:
        for tab_key, button in self.tab_buttons.items():
            if tab_key == key:
                button.configure(
                    fg_color=PANEL_BG,
                    border_color=BORDER_COLOR,
                    text_color=TEXT_MAIN
                )
            else:
                button.configure(
                    fg_color="transparent",
                    border_color=BORDER_COLOR,
                    text_color=TEXT_MUTED
                )
        
        # Hiển thị frame tương ứng bằng cách lift (tránh pack_forget gây giật lag giao diện)
        if key in self.tabs:
            self.tabs[key].lift()
            
        # Làm mới nội dung tab
        self._refresh_active_tab()

    def _refresh_active_tab(self):
        """Làm mới dữ liệu của tab đang active."""
        if self.active_tab in self.tabs:
            self.tabs[self.active_tab].refresh(self.selected_month)
            
    def update_charts(self, category_data, trend_data):
        """Cập nhật dữ liệu và vẽ lại các biểu đồ trong bảng thống kê (uỷ quyền cho StatsTab)."""
        if "stats" in self.tabs:
            self.tabs["stats"].update_charts(category_data, trend_data)

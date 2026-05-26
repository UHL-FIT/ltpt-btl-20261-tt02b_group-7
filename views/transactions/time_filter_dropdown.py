# Nhập các thư viện hệ thống và giao diện người dùng
import datetime
import tkinter as tk
import customtkinter as ctk
from views.core.theme_styles import *
from views.core.ui_decorators import safe_execution
from utils.logger import logger

# Khai báo lớp ViewByDropdown hiển thị trình đơn lọc thời gian cao cấp dạng Floating Frame
class ViewByDropdown(ctk.CTkFrame):
    # Khởi tạo dropdown lọc thời gian
    def __init__(self, master, button_trigger, on_apply_cb, initial_preset="Tất cả", **kwargs):
        """
        Component lọc khoảng thời gian tùy chỉnh cao cấp dạng Floating Popover.
        - master: MainWindow của ứng dụng.
        - button_trigger: Nút kích hoạt dropdown để tính tọa độ hiển thị.
        - on_apply_cb: Callback nhận tham số (start_date_str, end_date_str, preset_name) khi bấm Áp dụng.
        """
        # Đặt cấu hình viền bo tròn và nền tối theo tông màu chung của ứng dụng
        super().__init__(
            master, fg_color=PANEL_BG, corner_radius=12, 
            border_width=1, border_color=BORDER_COLOR, 
            width=460, height=350, **kwargs
        )
        self.main_app = master
        self.btn_trigger = button_trigger
        self.on_apply_cb = on_apply_cb
        self.icons = master.icons
        
        self.active_preset = initial_preset
        self.cal_window = None
        
        # Ngăn chặn co giãn chiều rộng/chiều cao tự động để giữ nguyên kích thước premium
        self.pack_propagate(False)
        
        self.setup_ui()
        
        # Thiết lập khoảng ngày ban đầu dựa vào Preset được truyền vào
        if self.active_preset:
            self.select_preset(self.active_preset)
        else:
            # Lấy khoảng ngày có sẵn của main_app
            self.entry_from.insert(0, master.filter_min_date)
            self.entry_to.insert(0, master.filter_max_date)
            self.update_preview()
            
    # Xây dựng toàn bộ layout UI 3 phần cho dropdown
    def setup_ui(self):
        # Thiết lập khoảng cách đệm
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # ================= PART 1: PRESET GRID =================
        grid_frame = ctk.CTkFrame(container, fg_color="transparent")
        grid_frame.pack(fill="x", pady=(0, 5))
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        grid_frame.columnconfigure(2, weight=1)
        
        presets = [
            ("Hôm nay", 0, 0), ("Hôm qua", 0, 1), ("Tuần này", 0, 2),
            ("Tuần trước", 1, 0), ("Tháng này", 1, 1), ("Tháng trước", 1, 2),
            ("Tất cả", 2, 0)
        ]
        
        self.preset_buttons = {}
        for name, row, col in presets:
            btn_text = "Xem tất cả" if name == "Tất cả" else name
            btn = ctk.CTkButton(
                grid_frame, text=btn_text, height=34, font=FONT_MAIN,
                corner_radius=8, border_width=1, border_color=BORDER_COLOR,
                command=lambda n=name: self.select_preset(n)
            )
            if name == "Tất cả":
                btn.grid(row=row, column=col, columnspan=3, padx=4, pady=4, sticky="ew")
            else:
                btn.grid(row=row, column=col, padx=4, pady=4, sticky="ew")
            self.preset_buttons[name] = btn
            
        # Đường kẻ phân cách siêu mỏng
        divider = tk.Frame(container, bg=BORDER_COLOR, height=1)
        divider.pack(fill="x", pady=8)
        
        # ================= PART 2: CUSTOM RANGE (Inputs & Chips) =================
        # Nhãn nhỏ tiêu đề
        lbl_title = ctk.CTkLabel(container, text="KHOẢNG TÙY CHỈNH", font=FONT_LABEL, text_color=TEXT_MUTED, anchor="w")
        lbl_title.pack(fill="x", pady=(0, 6))
        
        # Hàng chứa 2 ô date inputs nằm ngang có mũi tên ở giữa
        inputs_frame = ctk.CTkFrame(container, fg_color="transparent")
        inputs_frame.pack(fill="x", pady=(0, 8))
        
        # Ô nhập Từ ngày
        container_from, self.entry_from = self.create_date_input(inputs_frame, "Từ ngày")
        container_from.pack(side="left", fill="x", expand=True)
        
        # Mũi tên liên kết
        arrow_lbl = ctk.CTkLabel(inputs_frame, text=" → ", font=FONT_MAIN, text_color=TEXT_MUTED)
        arrow_lbl.pack(side="left", padx=5)
        
        # Ô nhập Đến ngày
        container_to, self.entry_to = self.create_date_input(inputs_frame, "Đến ngày")
        container_to.pack(side="left", fill="x", expand=True)
        
        # Hàng chứa các Chip lùi ngày nhanh
        chips_frame = ctk.CTkFrame(container, fg_color="transparent")
        chips_frame.pack(fill="x", pady=(0, 5))
        
        chips_data = [
            ("7 ngày", 7), ("14 ngày", 14), ("30 ngày", 30),
            ("2 tháng", 60), ("3 tháng", 90)
        ]
        
        self.chip_buttons = {}
        for text, days in chips_data:
            btn_chip = ctk.CTkButton(
                chips_frame, text=text, width=74, height=24, font=FONT_BADGE,
                fg_color="transparent", hover_color=PANEL_BG_HOVER,
                border_width=1, border_color=BORDER_COLOR, text_color=TEXT_MUTED,
                corner_radius=12, command=lambda d=days, t=text: self.on_chip_click(d, t)
            )
            btn_chip.pack(side="left", padx=4)
            self.chip_buttons[text] = btn_chip
            
        # ================= PART 3: FOOTER (Reset, Preview, Apply) =================
        footer_frame = ctk.CTkFrame(container, fg_color="transparent")
        footer_frame.pack(fill="x", side="bottom")
        
        # Trái: Nút Đặt lại
        self.btn_reset = ctk.CTkButton(
            footer_frame, text="Đặt lại", width=80, height=36, font=FONT_BUTTON,
            fg_color="transparent", hover_color=PANEL_BG_HOVER, text_color=TEXT_MUTED,
            corner_radius=8, command=self.reset_to_default
        )
        self.btn_reset.pack(side="left")
        
        # Phải: Nút Áp dụng
        self.btn_apply = ctk.CTkButton(
            footer_frame, text="Áp dụng", width=90, height=36, font=FONT_BUTTON,
            fg_color="#1E293B", hover_color=PANEL_BG_HOVER, text_color=TEXT_MAIN,
            border_width=1, border_color=BORDER_COLOR, corner_radius=8,
            command=self.apply_filter
        )
        self.btn_apply.pack(side="right")
        
        # Giữa: Text Preview Real-time
        self.lbl_preview = ctk.CTkLabel(footer_frame, text="--/-- – --/--", font=FONT_MAIN, text_color=TEXT_MUTED, anchor="center")
        self.lbl_preview.pack(side="left", fill="x", expand=True, padx=10)
        
        # Lắng nghe sự kiện người dùng chỉnh sửa ô nhập trực tiếp
        self.entry_from.bind("<KeyRelease>", lambda e: self.on_key_release())
        self.entry_to.bind("<KeyRelease>", lambda e: self.on_key_release())

    # Tạo ô nhập ngày bo tròn tùy chỉnh kết hợp nút chọn lịch nằm bên trong
    def create_date_input(self, parent, placeholder):
        box_frame = ctk.CTkFrame(parent, fg_color=BG_COLOR, border_width=1, border_color=BORDER_COLOR, corner_radius=8, height=38)
        box_frame.pack_propagate(False)
        
        entry = ctk.CTkEntry(
            box_frame, placeholder_text=placeholder, fg_color="transparent",
            border_width=0, font=FONT_MAIN, text_color=TEXT_MAIN, height=30
        )
        entry.pack(side="left", fill="x", expand=True, padx=(10, 2))
        
        btn_cal = ctk.CTkButton(
            box_frame, text="", image=self.icons.get('calendar'), width=24, height=24,
            fg_color="transparent", hover_color=PANEL_BG_HOVER, corner_radius=4,
            command=lambda: self.open_calendar_popup(entry)
        )
        btn_cal.pack(side="right", padx=(2, 6))
        
        return box_frame, entry

    # Tính toán khoảng ngày bắt đầu và kết thúc của Preset chỉ định
    def get_preset_range(self, preset_name):
        today = datetime.date.today()
        if preset_name == "Hôm nay":
            return today, today
        elif preset_name == "Hôm qua":
            yesterday = today - datetime.timedelta(days=1)
            return yesterday, yesterday
        elif preset_name == "Tuần này":
            weekday = today.weekday() # Monday=0, Sunday=6
            start = today - datetime.timedelta(days=weekday)
            end = start + datetime.timedelta(days=6)
            return start, end
        elif preset_name == "Tuần trước":
            weekday = today.weekday()
            start = today - datetime.timedelta(days=weekday + 7)
            end = start + datetime.timedelta(days=6)
            return start, end
        elif preset_name == "Tháng này":
            start = today.replace(day=1)
            # Tìm ngày đầu tiên của tháng sau rồi trừ đi 1 ngày
            next_month = start.replace(day=28) + datetime.timedelta(days=4)
            end = next_month - datetime.timedelta(days=next_month.day)
            return start, end
        elif preset_name == "Tháng trước":
            first_of_this_month = today.replace(day=1)
            end = first_of_this_month - datetime.timedelta(days=1)
            start = end.replace(day=1)
            return start, end
        elif preset_name == "7 ngày":
            return today - datetime.timedelta(days=6), today
        elif preset_name == "14 ngày":
            return today - datetime.timedelta(days=13), today
        elif preset_name == "30 ngày":
            return today - datetime.timedelta(days=29), today
        elif preset_name == "2 tháng":
            return today - datetime.timedelta(days=59), today
        elif preset_name == "3 tháng":
            return today - datetime.timedelta(days=89), today
        elif preset_name == "Tất cả":
            return "", ""
        return today, today

    # Cập nhật viền & nền nút Preset được chọn để tạo trải nghiệm trực quan
    def update_preset_highlights(self):
        for name, btn in self.preset_buttons.items():
            if name == self.active_preset:
                btn.configure(
                    fg_color="#1E3A8A", # Màu Navy cao cấp
                    border_color="#3B82F6", # Màu xanh sáng tinh tế
                    text_color="#93C5FD"
                )
            else:
                btn.configure(
                    fg_color=PANEL_BG,
                    border_color=BORDER_COLOR,
                    text_color=TEXT_MAIN
                )
                
        # Cập nhật trạng thái highlight cho các chip lùi ngày nhanh
        for text, btn in self.chip_buttons.items():
            if text == self.active_preset:
                btn.configure(
                    fg_color="#1E3A8A", # Màu Navy cao cấp
                    border_color="#3B82F6", # Màu xanh sáng tinh tế
                    text_color="#93C5FD"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    border_color=BORDER_COLOR,
                    text_color=TEXT_MUTED
                )

    # Chọn preset nhanh từ grid
    def select_preset(self, name):
        self.active_preset = name
        start_dt, end_dt = self.get_preset_range(name)
        
        self.entry_from.delete(0, 'end')
        self.entry_to.delete(0, 'end')
        
        if name != "Tất cả":
            self.entry_from.insert(0, start_dt.strftime("%d/%m/%Y"))
            self.entry_to.insert(0, end_dt.strftime("%d/%m/%Y"))
        
        self.update_preset_highlights()
        self.update_preview()

    # Mở lịch chọn ngày dạng popup sử dụng thư viện tkcalendar
    @safe_execution("Lỗi mở lịch")
    def open_calendar_popup(self, entry_widget):
        if self.cal_window and self.cal_window.winfo_exists():
            self.cal_window.focus()
            return
            
        self.cal_window = ctk.CTkToplevel(self)
        self.cal_window.title("Chọn ngày")
        self.cal_window.geometry("300x300")
        self.cal_window.transient(self)
        self.cal_window.grab_set()
        self.cal_window.configure(fg_color=PANEL_BG)
        
        # Căn giữa popup lịch so với dropdown
        self.cal_window.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (300 // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (300 // 2)
        self.cal_window.geometry(f"+{int(x)}+{int(y)}")
        
        import tkcalendar
        
        try:
            curr_val = entry_widget.get().strip()
            dt = datetime.datetime.strptime(curr_val, "%d/%m/%Y")
            year, month, day = dt.year, dt.month, dt.day
        except:
            now = datetime.date.today()
            year, month, day = now.year, now.month, now.day
            
        cal = tkcalendar.Calendar(self.cal_window, selectmode='day', date_pattern='dd/mm/yyyy', year=year, month=month, day=day)
        cal.pack(pady=10, padx=10, fill="both", expand=True)
        
        def confirm_date():
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, cal.get_date())
            self.cal_window.destroy()
            self.cal_window = None
            
            # Reset preset do người dùng vừa đổi ngày thủ công
            self.active_preset = None
            self.update_preset_highlights()
            self.update_preview()
            
        btn_ok = ctk.CTkButton(self.cal_window, text="Chọn", command=confirm_date, height=36, fg_color=ACCENT_BLUE, font=FONT_BUTTON)
        btn_ok.pack(pady=10)
        
        # Dọn dẹp con trỏ khi đóng cửa sổ ngang
        self.cal_window.protocol("WM_DELETE_WINDOW", lambda: self._close_cal_window())

    def _close_cal_window(self):
        if self.cal_window:
            self.cal_window.destroy()
            self.cal_window = None

    # Xử lý sự kiện click chip nhanh (lùi ngày ngược lại N ngày tính từ hôm nay)
    def on_chip_click(self, days, preset_name):
        self.active_preset = preset_name
        start_dt, end_dt = self.get_preset_range(preset_name)
        
        self.entry_from.delete(0, 'end')
        self.entry_from.insert(0, start_dt.strftime("%d/%m/%Y"))
        
        self.entry_to.delete(0, 'end')
        self.entry_to.insert(0, end_dt.strftime("%d/%m/%Y"))
        
        self.update_preset_highlights()
        self.update_preview()

    # Xử lý sự kiện bàn phím khi người dùng nhập thủ công vào các ô nhập
    def on_key_release(self):
        self.active_preset = None
        self.update_preset_highlights()
        self.update_preview()

    # Cập nhật dòng preview real-time ở giữa Footer và kiểm định tính hợp lệ của ngày nhập
    def update_preview(self):
        date_from = self.entry_from.get().strip()
        date_to = self.entry_to.get().strip()
        
        if not date_from and not date_to:
            self.lbl_preview.configure(text="Xem tất cả", text_color=TEXT_MAIN)
            self.btn_apply.configure(state="normal")
            return
            
        try:
            # Kiểm chứng định dạng ngày có khớp chuẩn DD/MM/YYYY không
            d1 = datetime.datetime.strptime(date_from, "%d/%m/%Y")
            d2 = datetime.datetime.strptime(date_to, "%d/%m/%Y")
            
            # Hiển thị preview chuẩn
            self.lbl_preview.configure(text=f"{date_from} – {date_to}", text_color=TEXT_MAIN)
            self.btn_apply.configure(state="normal")
        except ValueError:
            # Hiển thị hướng dẫn định dạng nếu người dùng đang gõ dở
            self.lbl_preview.configure(text="Chờ nhập ngày...", text_color=TEXT_MUTED)
            self.btn_apply.configure(state="disabled")

    # Đặt lại bộ lọc về preset mặc định (Tất cả)
    def reset_to_default(self):
        self.select_preset("Tất cả")

    # Áp dụng bộ lọc thời gian và đóng dropdown
    @safe_execution("Lỗi áp dụng lọc thời gian")
    def apply_filter(self):
        date_from = self.entry_from.get().strip()
        date_to = self.entry_to.get().strip()
        
        if not date_from and not date_to:
            logger.info("Áp dụng lọc Xem theo thời gian: Tất cả")
            self.on_apply_cb("", "", "Tất cả")
            return
            
        # Đảm bảo dữ liệu hợp lệ trước khi trigger filter
        try:
            datetime.datetime.strptime(date_from, "%d/%m/%Y")
            datetime.datetime.strptime(date_to, "%d/%m/%Y")
        except ValueError:
            return
            
        logger.info(f"Áp dụng lọc Xem theo thời gian: Từ {date_from} đến {date_to} (Preset: {self.active_preset})")
        self.on_apply_cb(date_from, date_to, self.active_preset)

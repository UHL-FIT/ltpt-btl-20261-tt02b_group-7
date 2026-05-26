# Nhập các thư viện cần thiết cho việc nhập dữ liệu giao dịch
import datetime
import customtkinter as ctk
from views.core.theme_styles import *
from views.core.ui_decorators import safe_execution, format_entry_amount
from utils.logger import logger

# Khai báo lớp TransactionWindow tạo biểu mẫu thêm/sửa giao dịch tài chính
class TransactionWindow(ctk.CTkToplevel):
    # Khởi tạo hộp thoại giao dịch
    def __init__(self, master, controller, icons, edit_t=None, **kwargs):
        """
        Biểu mẫu popup tương tác dùng để thêm mới hoặc cập nhật thông tin giao dịch tài chính.
        """
        super().__init__(master, **kwargs)
        self.main_app = master
        self.controller = controller
        self.icons = icons
        self.edit_t = edit_t
        self.current_edit_id = edit_t['id'] if edit_t else None
        self.calendar_window = None
        
        title = "Giao dịch mới" if not edit_t else "Sửa giao dịch"
        self.title(title)
        self.geometry("400x580")
        self.transient(master)
        self.grab_set()
        self.configure(fg_color=PANEL_BG)
        
        # Căn giữa hộp thoại so với cửa sổ cha
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (400 // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (580 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.setup_ui()

    # Tạo nhãn tiêu đề cho các trường nhập liệu trên biểu mẫu
    def _create_form_label(self, parent, text, top_pady=15):
        ctk.CTkLabel(parent, text=text, font=FONT_LABEL, text_color=TEXT_MUTED).pack(anchor="w", pady=(top_pady, 5))

    # Thiết lập giao diện người dùng cho biểu mẫu nhập liệu
    def setup_ui(self):
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=20)
        
        self._create_form_label(form, "THỜI GIAN", top_pady=10)
        
        datetime_frame = ctk.CTkFrame(form, fg_color="transparent")
        datetime_frame.pack(fill="x")
        
        self.inp_date = ctk.CTkEntry(datetime_frame, placeholder_text="DD/MM/YYYY", height=36)
        self.inp_date.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        btn_calendar = ctk.CTkButton(
            datetime_frame, text="", image=self.icons.get('calendar'), 
            width=36, height=36, fg_color=PANEL_BG_HOVER, hover_color=ACCENT_BLUE, 
            command=self.open_calendar_popup
        )
        btn_calendar.pack(side="left", padx=(0, 10))
        
        self.inp_time = ctk.CTkEntry(datetime_frame, placeholder_text="HH:MM", height=36, width=80)
        self.inp_time.pack(side="left")
        
        if self.edit_t:
            dt_parts = str(self.edit_t['date']).split()
            date_val = dt_parts[0]
            if '-' in date_val:
                p = date_val.split('-')
                if len(p) == 3 and len(p[0]) == 4:
                    date_val = f"{p[2]}/{p[1]}/{p[0]}"
            time_val = dt_parts[1] if len(dt_parts) > 1 else "00:00"
            if len(time_val.split(':')) == 3: time_val = time_val.rsplit(':', 1)[0]
        else:
            now = datetime.datetime.now()
            date_val = now.strftime("%d/%m/%Y")
            time_val = now.strftime("%H:%M")
            
        self.inp_date.insert(0, date_val)
        self.inp_time.insert(0, time_val)
        
        self._create_form_label(form, "SỐ TIỀN")
        self.inp_amount = ctk.CTkEntry(form, placeholder_text="0", height=40, font=FONT_AMOUNT)
        self.inp_amount.pack(fill="x")
        self.inp_amount.bind("<KeyRelease>", lambda event: format_entry_amount(self.inp_amount, event))
        if self.edit_t:
            amt_val = str(self.edit_t['amount'])
            try:
                amt_val = "{:,}".format(int(float(amt_val)))
            except: pass
            self.inp_amount.insert(0, amt_val)
        
        self._create_form_label(form, "LOẠI")
        self.inp_type = ctk.CTkSegmentedButton(form, values=[TX_TYPE_EXPENSE_VN, TX_TYPE_INCOME_VN], height=36, selected_color=ACCENT_BLUE)
        self.inp_type.pack(fill="x")
        if self.edit_t:
            self.inp_type.set(self.edit_t.get('type', TX_TYPE_EXPENSE_VN))
        else:
            self.inp_type.set(TX_TYPE_EXPENSE_VN)
        
        self._create_form_label(form, "DANH MỤC")
        cats = self.main_app._get_categories()
        cats.append(ADD_NEW_CAT_TEXT)
        self.inp_cat = ctk.CTkOptionMenu(form, values=cats, height=36, command=self.on_category_select)
        self.inp_cat.pack(fill="x")
        if self.edit_t:
            val = self.edit_t['category']
            if val not in cats:
                val = cats[0] if cats else ""
            self.inp_cat.set(val)
        else:
            self.inp_cat.set(cats[0] if cats else "")
            
        self._create_form_label(form, "GHI CHÚ")
        self.inp_note = ctk.CTkEntry(form, placeholder_text="Giao dịch này dùng để làm gì?", height=36)
        self.inp_note.pack(fill="x")
        if self.edit_t: self.inp_note.insert(0, self.edit_t['note'])
        
        btn_confirm = ctk.CTkButton(self, text="Xác nhận", fg_color=ACCENT_BLUE, height=48, font=FONT_BUTTON_LARGE, command=self.save_transaction)
        btn_confirm.pack(fill="x", padx=20, pady=20, side="bottom")

    # Mở lịch chọn ngày tháng dạng popup
    @safe_execution("Lỗi mở lịch chọn ngày")
    def open_calendar_popup(self):
        if self.calendar_window and self.calendar_window.winfo_exists():
            self.calendar_window.focus()
            return
            
        self.calendar_window = ctk.CTkToplevel(self)
        self.calendar_window.title("Chọn ngày")
        self.calendar_window.geometry("300x300")
        self.calendar_window.transient(self)
        self.calendar_window.grab_set()
        self.calendar_window.configure(fg_color=PANEL_BG)
        
        self.calendar_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (300 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (300 // 2)
        self.calendar_window.geometry(f"+{x}+{y}")
        
        import tkcalendar
        
        try:
            current_date_str = self.inp_date.get()
            fmt = "%d/%m/%Y" if "/" in current_date_str else "%Y-%m-%d"
            dt = datetime.datetime.strptime(current_date_str, fmt)
            year, month, day = dt.year, dt.month, dt.day
        except:
            now = datetime.datetime.now()
            year, month, day = now.year, now.month, now.day

        cal = tkcalendar.Calendar(self.calendar_window, selectmode='day', date_pattern='dd/mm/yyyy', year=year, month=month, day=day)
        cal.pack(pady=10, padx=10, fill="both", expand=True)
        
        def set_date():
            self.inp_date.delete(0, 'end')
            self.inp_date.insert(0, cal.get_date())
            self.calendar_window.destroy()
            self.calendar_window = None
            
        btn_ok = ctk.CTkButton(self.calendar_window, text="Chọn", command=set_date, height=36, fg_color=ACCENT_BLUE, font=FONT_BUTTON)
        btn_ok.pack(pady=10)

    # Xử lý sự kiện khi người dùng chọn danh mục (bao gồm thêm mới danh mục)
    def on_category_select(self, value):
        if value == ADD_NEW_CAT_TEXT:
            self.main_app.open_category_manager()
            cats = self.main_app._get_categories()
            if cats:
                self.inp_cat.set(cats[0])



    # Thu thập dữ liệu từ biểu mẫu, kiểm tra tính hợp lệ và lưu giao dịch
    @safe_execution("Lỗi lưu giao dịch")
    def save_transaction(self):
        if not self.controller: return
        date = f"{self.inp_date.get()} {self.inp_time.get()}"
        amount_str = self.inp_amount.get().replace(',', '')
        category = self.inp_cat.get()
        t_type = self.inp_type.get()
        note = self.inp_note.get()
        
        try:
            amount = float(amount_str)
        except ValueError:
            logger.warning(f"Dữ liệu số tiền nhập vào không hợp lệ khi lưu giao dịch: '{amount_str}'")
            self.main_app.show_error("Lỗi", "Số tiền phải là một con số hợp lệ.")
            return
            
        logger.info(f"Yêu cầu lưu giao dịch: mã={self.current_edit_id or 'NEW'}, date='{date}', amount={amount}, category='{category}', type='{t_type}'")
        if self.current_edit_id:
            self.controller.update_transaction(self.current_edit_id, date, amount, category, t_type, note)
        else:
            self.controller.add_transaction(date, amount, category, t_type, note)
        
        self.destroy()

# ==========================================
# Tên file: transaction_dialog.py (nằm trong thư mục views/transactions)
# Danh sách lớp và chức năng OOP:
# Lớp: TransactionWindow
# - Chức năng: Biểu mẫu nhập liệu độc quyền dạng hộp thoại con (CTkToplevel + grab_set) phục vụ việc thêm mới hoặc cập nhật sửa đổi thông tin một giao dịch tài chính (thời gian, số tiền, loại, danh mục, ghi chú).
# Khái niệm OOP sử dụng:
# - Tính kế thừa (Inheritance): TransactionWindow kế thừa ctk.CTkToplevel để chạy như một cửa sổ con nổi lập lập, chặn tương tác với cửa sổ chính cho đến khi hoàn thành.
# - Tính đóng gói (Encapsulation): Che giấu chi tiết sinh giao diện biểu mẫu nhập liệu, phương thức vẽ nhãn phụ trợ (_create_form_label), logic tự động định dạng hiển thị tiền tệ (format_amount_input) và tự quản lý vòng đời cửa sổ (self.destroy()).
# - Giao tiếp đối tượng (Object Collaboration): Giao tiếp chặt chẽ với controller để uỷ quyền lưu/sửa giao dịch (update_transaction/add_transaction) và master (MainWindow) để lấy danh sách danh mục hoặc kích hoạt hộp thoại quản lý danh mục (open_category_manager). Tích hợp với đối tượng tkcalendar.Calendar độc lập ngoài hệ thống để chọn ngày trực quan.
# ==========================================

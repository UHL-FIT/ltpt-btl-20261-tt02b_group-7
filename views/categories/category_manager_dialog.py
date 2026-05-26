# Nhập các thư viện cần thiết cho các hộp thoại
import customtkinter as ctk
import tkinter.messagebox as mb
from views.core.theme_styles import *
from views.core.ui_decorators import safe_execution
from utils.logger import logger

# Khai báo lớp CategoryManagerWindow quản lý danh sách danh mục chi tiêu
class CategoryManagerWindow(ctk.CTkToplevel):
    # Khởi tạo hộp thoại quản lý danh mục
    def __init__(self, master, controller, **kwargs):
        """
        Hộp thoại quản lý danh mục giúp thêm, sửa hoặc xóa các danh mục chi tiêu tùy chỉnh.
        """
        super().__init__(master, **kwargs)
        self.main_app = master
        self.controller = controller
        
        self.title("Quản lý danh mục")
        self.geometry("400x500")
        self.transient(master)
        self.grab_set()
        self.configure(fg_color=PANEL_BG)
        
        # Căn giữa hộp thoại so với cửa sổ cha
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (400 // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (500 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.setup_ui()

    # Thiết lập các thành phần giao diện người dùng
    def setup_ui(self):
        lbl_title = ctk.CTkLabel(self, text="QUẢN LÝ DANH MỤC", font=FONT_TITLE)
        lbl_title.pack(pady=(20, 10))
        
        self.cat_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.cat_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.render_category_list()
        
        add_frame = ctk.CTkFrame(self, fg_color="transparent")
        add_frame.pack(fill="x", padx=20, pady=20, side="bottom")
        
        self.inp_new_cat = ctk.CTkEntry(add_frame, placeholder_text="Tên danh mục mới...", height=36)
        self.inp_new_cat.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        btn_add = ctk.CTkButton(add_frame, text="Thêm", width=60, height=36, fg_color=ACCENT_BLUE, command=self.add_new_category)
        btn_add.pack(side="left")

    # Hiển thị danh sách danh mục hiện có cùng các nút sửa, xóa
    @safe_execution("Lỗi kết xuất danh sách danh mục")
    def render_category_list(self):
        for widget in self.cat_scroll.winfo_children():
            widget.destroy()
            
        cats = self.main_app._get_categories()
        if not cats and not self.controller: return
        
        for cat in cats:
            row = ctk.CTkFrame(self.cat_scroll, fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            inp = ctk.CTkEntry(row, height=32)
            inp.insert(0, cat)
            inp.pack(side="left", fill="x", expand=True, padx=(0, 5))
            
            btn_save = ctk.CTkButton(
                row, text="Lưu", width=50, height=32, fg_color=ACCENT_GREEN, 
                command=lambda old=cat, i=inp: self.update_category(old, i.get())
            )
            btn_save.pack(side="left", padx=2)
            
            btn_del = ctk.CTkButton(
                row, text="Xóa", width=50, height=32, fg_color=ACCENT_RED, 
                command=lambda c=cat: self.delete_category(c)
            )
            btn_del.pack(side="left")

    # Thêm một danh mục chi tiêu mới vào danh sách
    @safe_execution("Lỗi thêm danh mục mới")
    def add_new_category(self):
        new_cat = self.inp_new_cat.get().strip()
        if not new_cat:
            return
        logger.info(f"Yêu cầu thêm danh mục mới: '{new_cat}'")
        if self.controller:
            self.controller.add_category(new_cat)
            self.inp_new_cat.delete(0, 'end')
            self.render_category_list()
            self.main_app.refresh_category_dropdown()

    # Cập nhật tên danh mục chi tiêu cũ thành tên mới
    @safe_execution("Lỗi sửa tên danh mục")
    def update_category(self, old_name, new_name):
        new_name = new_name.strip()
        if old_name == new_name or not new_name:
            return
        logger.info(f"Yêu cầu sửa tên danh mục: '{old_name}' -> '{new_name}'")
        if self.controller:
            self.controller.update_category(old_name, new_name)
            self.render_category_list()
            self.main_app.refresh_category_dropdown()
            
    # Xóa một danh mục chi tiêu khỏi danh sách sau khi người dùng xác nhận
    @safe_execution("Lỗi xóa danh mục")
    def delete_category(self, name):
        logger.info(f"Yêu cầu xóa danh mục: '{name}'")
        if mb.askyesno("Xác nhận", f"Xóa danh mục '{name}'?", parent=self, icon="warning"):
            if self.controller:
                self.controller.delete_category(name)
                self.render_category_list()
                self.main_app.refresh_category_dropdown()

# ==========================================
# Tên file: category_dialog.py (nằm trong thư mục views/dialogs)
# Danh sách lớp và chức năng OOP:
# Lớp: CategoryManagerWindow
# - Chức năng: Hộp thoại con độc quyền (CTkToplevel + grab_set) phục vụ việc quản lý (CRUD) danh sách các danh mục chi tiêu tùy chỉnh của người dùng.
# Khái niệm OOP sử dụng:
# - Tính kế thừa (Inheritance): Lớp CategoryManagerWindow kế thừa ctk.CTkToplevel để nhanh chóng thừa hưởng các thuộc tính quản lý cửa sổ dạng hộp thoại trồi lên (Popup Dialog).
# - Tính đóng gói (Encapsulation): Đóng gói kín kẽ các widgets giao diện của riêng mình và hành vi tương ứng (CategoryManagerWindow quản lý danh sách cuộn danh mục).
# - Giao tiếp đối tượng (Object Collaboration): CategoryManagerWindow giao tiếp chặt chẽ với controller để thay đổi dữ liệu danh mục ở SQLite và phối hợp thông báo cập nhật lại dropdown của lớp master (MainWindow) qua main_app.refresh_category_dropdown().
# ==========================================

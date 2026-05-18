import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from models import diemdanh
import views.gui_view as gui_view
from utils.logger import setup_logger

logger = setup_logger()

# Các biến toàn cục (module-level state)
app_df = pd.DataFrame()
app_ui = {}
app_root = None
app_edit_widget = None

def _tai_du_lieu():
    """Tải và hiển thị danh sách sinh viên lên bảng (kết hợp bộ lọc nếu có)."""
    global app_df
    app_df, ok = diemdanh.lay_danh_sach()
    if not ok:
        messagebox.showerror("Lỗi", "Không thể tải dữ liệu điểm danh.")
        return
        
    # Áp dụng bộ lọc tìm kiếm
    search_text = app_ui['ent_search'].get().strip().lower()
    search_by = app_ui['cbo_search_by'].get()
    
    display_df = app_df.copy()
    if search_text and not display_df.empty:
        if search_by == "MSV":
            display_df = display_df[display_df['msv'].astype(str).str.lower().str.contains(search_text, na=False)]
        elif search_by == "Họ Tên":
            display_df = display_df[display_df['ho_ten'].astype(str).str.lower().str.contains(search_text, na=False)]
        elif search_by == "Giới tính":
            display_df = display_df[display_df['gioi_tinh'].astype(str).str.lower().str.contains(search_text, na=False)]
        elif search_by == "SĐT":
            display_df = display_df[display_df['sdt'].astype(str).str.lower().str.contains(search_text, na=False)]
        else: # "Tất cả"
            # Tìm trên tất cả các cột
            mask = display_df.apply(lambda row: row.astype(str).str.lower().str.contains(search_text).any(), axis=1)
            display_df = display_df[mask]
            
    gui_view.hien_thi_bang(app_ui, display_df)
    
    # Cập nhật thống kê dựa trên dữ liệu hiện đang hiển thị (danh sách đã lọc)
    stats = diemdanh.thong_ke(display_df)
    gui_view.cap_nhat_thong_ke(app_ui, stats)


def on_search():
    """Xử lý sự kiện click nút Tìm kiếm."""
    logger.info("Người dùng thực hiện tìm kiếm.")
    _tai_du_lieu()


def on_clear_search():
    """Xóa trạng thái tìm kiếm và hiển thị lại toàn bộ danh sách."""
    logger.info("Người dùng xóa bộ lọc tìm kiếm.")
    app_ui['ent_search'].delete(0, tk.END)
    app_ui['cbo_search_by'].set("Tất cả")
    _tai_du_lieu()


def on_them_sv():
    """Bật cửa sổ Pop-up để thêm mới 1 sinh viên."""
    logger.info("Người dùng click Thêm Sinh viên.")
    global app_df
    data = gui_view.hien_thi_form_sinh_vien(app_root, is_edit=False)
    if data:
        app_df, ok, msg = diemdanh.them_sinh_vien(app_df, data)
        if ok:
            _tai_du_lieu()
        else:
            messagebox.showerror("Lỗi", msg)


def on_sua_sv():
    """Bật cửa sổ Pop-up để sửa thông tin sinh viên được tick chọn."""
    logger.info("Người dùng click Sửa Sinh viên.")
    global app_df
    tree = app_ui['tree']
    
    # Ưu tiên lấy các sinh viên được tick checkbox
    selected = []
    for item_id in tree.get_children():
        values = tree.item(item_id, 'values')
        if values[0] == "☑":
            selected.append(item_id)
            
    # Nếu không có ô checkbox nào được tick, thử lấy dòng đang được bôi xanh (highlight)
    if not selected:
        selected = list(tree.selection())

    if not selected:
        messagebox.showwarning("Cảnh báo", "Vui lòng tick chọn (☑) hoặc bấm chọn 1 sinh viên để sửa!")
        return
        
    if len(selected) > 1:
        messagebox.showwarning("Cảnh báo", "Bạn đang chọn nhiều hơn 1 sinh viên. Vui lòng chỉ chọn 1 sinh viên để sửa thông tin!")
        return
        
    item = tree.item(selected[0])
    msv = item['values'][2]
    hoten = item['values'][3]
    gioi_tinh = item['values'][4]
    lop = item['values'][5]
    sdt = item['values'][6]
    
    current_data = {"msv": msv, "ho_ten": hoten, "gioi_tinh": gioi_tinh, "lop": lop, "sdt": sdt}
    
    data = gui_view.hien_thi_form_sinh_vien(app_root, is_edit=True, current_data=current_data)
    if data:
        app_df, ok, msg = diemdanh.sua_sinh_vien(app_df, msv, data)
        if ok:
            _tai_du_lieu()
        else:
            messagebox.showerror("Lỗi", msg)


def on_xoa_sv():
    """Xóa các sinh viên được tick chọn khỏi danh sách."""
    logger.info("Người dùng click Xóa Sinh viên.")
    global app_df
    tree = app_ui['tree']
    msv_to_delete = []
    for item_id in tree.get_children():
        values = tree.item(item_id, 'values')
        if values[0] == "☑":
            msv_to_delete.append(values[2])
            
    if not msv_to_delete:
        messagebox.showwarning("Cảnh báo", "Vui lòng tick chọn (☑) ít nhất 1 sinh viên ở cột 'Chọn' để xóa!")
        return
        
    if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa {len(msv_to_delete)} sinh viên đã chọn?"):
        app_df, ok, msg = diemdanh.xoa_nhieu_sinh_vien(app_df, msv_to_delete)
        if ok:
            _tai_du_lieu()
        else:
            messagebox.showerror("Lỗi", msg)


def on_import():
    """Import danh sách sinh viên từ một file CSV bên ngoài."""
    logger.info("Người dùng click Import CSV.")
    global app_df
    filepath = filedialog.askopenfilename(
        title="Chọn file CSV danh sách sinh viên",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    if not filepath:
        return
        
    try:
        df_import = pd.read_csv(filepath, dtype=str)
        if "ho_ten" not in df_import.columns or "sdt" not in df_import.columns:
            messagebox.showerror("Lỗi", "File CSV phải có cột 'ho_ten' và 'sdt'.")
            return
            
        for _, row in df_import.iterrows():
            data = {
                "msv": row.get("msv", ""),
                "ho_ten": row.get("ho_ten", ""),
                "lop": row.get("lop", ""),
                "sdt": row.get("sdt", "")
            }
            app_df, _, _ = diemdanh.them_sinh_vien(app_df, data)
            
        _tai_du_lieu()
        messagebox.showinfo("Thành công", f"Đã import thành công danh sách từ {filepath}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể import file: {e}")


def on_export():
    """Xuất danh sách sinh viên hiện tại ra một file CSV."""
    logger.info("Người dùng click Export CSV.")
    global app_df
    filepath = filedialog.asksaveasfilename(
        title="Lưu file báo cáo điểm danh",
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        initialfile="baocao_diemdanh.csv"
    )
    if not filepath:
        return
        
    try:
        app_df.to_csv(filepath, index=False, encoding="utf-8-sig")
        messagebox.showinfo("Thành công", f"Đã lưu báo cáo tại {filepath}")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")


def on_about():
    """Hiển thị thông tin giới thiệu phần mềm."""
    logger.info("Người dùng click Giới thiệu.")
    about_text = (
        "📘 PHẦN MỀM: SMARTATTEND\n"
        "------------------------------------\n"
        "🔹 Phiên bản: 1.0.0\n"
        "🔹 Tác giả: ThS. Vũ Duy Sơn\n"
        "🔹 Đơn vị: Trường Đại học Hạ Long (UHL)\n"
        "🔹 Ngày phát hành: 03/05/2026\n"
        "------------------------------------\n"
        "Phần mềm hỗ trợ quản lý sinh viên và điểm danh chuyên cần tự động."
    )
    messagebox.showinfo("Giới thiệu", about_text)


def on_single_click(event):
    tree = app_ui['tree']
    region = tree.identify_region(event.x, event.y)
    column_str = tree.identify_column(event.x)
    
    if not column_str:
        return
        
    col_idx = int(column_str.replace("#", "")) - 1
    col_name = app_ui['cols'][col_idx]
    
    if region == "heading" and col_name == "Chọn":
        current_heading = tree.heading("Chọn", "text")
        if "☐" in current_heading:
            new_heading = "☑"
            new_val = "☑"
        else:
            new_heading = "☐"
            new_val = "☐"
            
        tree.heading("Chọn", text=new_heading)
        for item_id in tree.get_children():
            values = list(tree.item(item_id, "values"))
            values[0] = new_val
            tree.item(item_id, values=values)
        return
        
    if region == "cell" and col_name == "Chọn":
        item_id = tree.identify_row(event.y)
        if item_id:
            values = list(tree.item(item_id, 'values'))
            values[0] = "☑" if values[0] == "☐" else "☐"
            tree.item(item_id, values=values)


def on_double_click(event):
    global app_edit_widget, app_df
    if app_edit_widget:
        app_edit_widget.destroy()
        app_edit_widget = None
        
    tree = app_ui['tree']
    region = tree.identify_region(event.x, event.y)
    if region != "cell":
        return
        
    column_str = tree.identify_column(event.x)
    item_id = tree.identify_row(event.y)
    
    if not item_id or not column_str:
        return
        
    col_idx = int(column_str.replace("#", "")) - 1
    col_name = app_ui['cols'][col_idx]
    
    values = tree.item(item_id, 'values')
    current_val = str(values[col_idx]).split(" ")[0]
    msv = values[2]
    
    is_tuan = col_name.startswith("T") and len(col_name) <= 3
    is_so_lan_bt = col_name == "Số lần làm BT"
    is_vi_pham = col_name == "Vi phạm"
    
    if not (is_tuan or is_so_lan_bt or is_vi_pham):
        return
        
    x, y, w, h = tree.bbox(item_id, column_str)
    
    if is_tuan:
        cb = ttk.Combobox(tree, values=["M", "P 🟢", "K 🟥"], state="readonly")
        val_map = {"M": "M", "P": "P 🟢", "K": "K 🟥"}
        cb.set(val_map.get(current_val, "M"))
        
        cb.place(x=x, y=y, width=w, height=h)
        cb.focus_set()
        
        def save_tuan(e):
            global app_df
            new_val = cb.get().split(" ")[0]
            cb.destroy()
            if new_val != current_val:
                tuan_col = col_name.lower()
                app_df, ok = diemdanh.cap_nhat_diem_danh(app_df, msv, tuan_col, new_val)
                if ok:
                    _tai_du_lieu()
        
        cb.bind("<<ComboboxSelected>>", save_tuan)
        cb.bind("<FocusOut>", lambda e: cb.destroy())
        app_edit_widget = cb
        
    elif is_so_lan_bt or is_vi_pham:
        ent = ttk.Entry(tree)
        ent.insert(0, str(values[col_idx]))
        ent.place(x=x, y=y, width=w, height=h)
        ent.focus_set()
        ent.select_range(0, tk.END)
        
        def save_diem(e):
            global app_df
            val_str = ent.get().strip()
            ent.destroy()
            try:
                new_val = float(val_str)
                if new_val >= 0:
                    if is_so_lan_bt:
                        app_df, ok = diemdanh.cap_nhat_so_lan_bt(app_df, msv, new_val)
                    else:
                        app_df, ok = diemdanh.cap_nhat_vi_pham(app_df, msv, new_val)
                    
                    if ok:
                        _tai_du_lieu()
                else:
                    messagebox.showwarning("Lỗi", "Giá trị phải >= 0.")
            except ValueError:
                messagebox.showwarning("Lỗi", "Giá trị phải là số hợp lệ.")
        
        ent.bind("<Return>", save_diem)
        ent.bind("<FocusOut>", lambda e: ent.destroy())
        app_edit_widget = ent


def _bind_events():
    app_ui['btn_them'].config(command=on_them_sv)
    app_ui['btn_sua'].config(command=on_sua_sv)
    app_ui['btn_xoa'].config(command=on_xoa_sv)
    app_ui['btn_import'].config(command=on_import)
    app_ui['btn_export'].config(command=on_export)
    app_ui['btn_about'].config(command=on_about)
    
    app_ui['btn_search'].config(command=on_search)
    app_ui['btn_clear_search'].config(command=on_clear_search)
    app_ui['ent_search'].bind("<Return>", lambda e: on_search())
    
    tree = app_ui['tree']
    tree.bind("<Double-1>", on_double_click)
    tree.bind("<ButtonRelease-1>", on_single_click)


def chay_ung_dung():
    """Khởi chạy ứng dụng GUI."""
    global app_root, app_ui
    logger.info("Khởi động ứng dụng Điểm danh Sinh viên (GUI)")
    app_root = tk.Tk()
    
    app_ui = gui_view.tao_giao_dien_chinh(app_root)
    _bind_events()
    _tai_du_lieu()
    
    app_root.mainloop()
    logger.info("Thoát ứng dụng (GUI)")

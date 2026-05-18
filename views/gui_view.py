import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

def sort_treeview(tree, col, reverse):
    """
    Sắp xếp Treeview khi người dùng click vào tiêu đề cột.

    Args:
        tree (ttk.Treeview): Đối tượng bảng hiển thị.
        col (str): Tên cột cần sắp xếp.
        reverse (bool): Hướng sắp xếp (True = Z-A, False = A-Z).
    """
    if col == "Chọn":
        return
        
    # Lấy toàn bộ dữ liệu hiện tại
    l = [(tree.set(k, col), k) for k in tree.get_children('')]
    
    # Cố gắng ép kiểu về float để sắp xếp số học chính xác, nếu lỗi thì sắp xếp theo chuỗi
    try:
        # Nếu cột chứa dữ liệu dạng "P 🟢", "K 🔴", tách lấy ký tự đầu
        def convert_val(x):
            val = str(x).split(" ")[0]
            return float(val)
        l.sort(key=lambda t: convert_val(t[0]), reverse=reverse)
    except ValueError:
        l.sort(reverse=reverse)

    # Đảo lại vị trí các hàng trên giao diện
    for index, (val, k) in enumerate(l):
        tree.move(k, '', index)

    # Gán lại sự kiện để lần click tiếp theo sẽ sắp xếp ngược lại
    tree.heading(col, command=lambda: sort_treeview(tree, col, not reverse))


def tao_giao_dien_chinh(root):
    """
    Khởi tạo giao diện chính và bố cục hệ thống.

    Args:
        root (tk.Tk): Cửa sổ gốc của ứng dụng.

    Returns:
        dict: Chứa các tham chiếu tới các widget (nút, bảng, ô nhập liệu...).
    """
    import sys
    import os
    
    root.title("SmartAttend")
    root.geometry("1200x600")
    
    # Thiết lập icon
    try:
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        icon_path = os.path.join(base_path, "assets", "app_icon.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(default=icon_path)
    except Exception as e:
        print(f"Lỗi load icon: {e}")
    
    # Style
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
    style.configure("Treeview", font=('Segoe UI Emoji', 10), rowheight=25)
    
    ui = {}
    
    # ─── TOOLBAR (TOP) ───
    frame_top = tk.Frame(root, pady=10, padx=10)
    frame_top.pack(fill=tk.X)
    
    # Khu vực thao tác (bên trái)
    frame_actions = tk.Frame(frame_top)
    frame_actions.pack(side=tk.LEFT)
    
    ui['btn_them'] = ttk.Button(frame_actions, text="+ Thêm Sinh viên")
    ui['btn_them'].pack(side=tk.LEFT, padx=2)
    
    ui['btn_sua'] = ttk.Button(frame_actions, text="Sửa thông tin")
    ui['btn_sua'].pack(side=tk.LEFT, padx=2)
    
    ui['btn_xoa'] = ttk.Button(frame_actions, text="Xóa SV")
    ui['btn_xoa'].pack(side=tk.LEFT, padx=2)
    
    ttk.Separator(frame_actions, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
    
    ui['btn_import'] = ttk.Button(frame_actions, text="📂 Import CSV")
    ui['btn_import'].pack(side=tk.LEFT, padx=2)
    
    ui['btn_export'] = ttk.Button(frame_actions, text="💾 Export CSV")
    ui['btn_export'].pack(side=tk.LEFT, padx=2)
    
    ui['btn_about'] = ttk.Button(frame_actions, text="ℹ️ Giới thiệu")
    ui['btn_about'].pack(side=tk.LEFT, padx=2)
    
    # Khu vực tìm kiếm (bên phải)
    frame_search = tk.Frame(frame_top)
    frame_search.pack(side=tk.RIGHT)
    
    tk.Label(frame_search, text="Tìm theo:").pack(side=tk.LEFT, padx=(10, 2))
    
    ui['cbo_search_by'] = ttk.Combobox(frame_search, values=["Tất cả", "MSV", "Họ Tên", "Giới tính", "SĐT"], state="readonly", width=10)
    ui['cbo_search_by'].set("Tất cả")
    ui['cbo_search_by'].pack(side=tk.LEFT, padx=2)
    
    ui['ent_search'] = ttk.Entry(frame_search, width=20)
    ui['ent_search'].pack(side=tk.LEFT, padx=2)
    
    ui['btn_search'] = ttk.Button(frame_search, text="🔍 Tìm", width=8)
    ui['btn_search'].pack(side=tk.LEFT, padx=2)
    
    ui['btn_clear_search'] = ttk.Button(frame_search, text="✖ Hủy", width=8)
    ui['btn_clear_search'].pack(side=tk.LEFT, padx=2)
    
    # ─── TREEVIEW (MIDDLE) ───
    frame_mid = tk.Frame(root, padx=10)
    frame_mid.pack(fill=tk.BOTH, expand=True)
    
    # Scrollbars
    scroll_y = ttk.Scrollbar(frame_mid)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    scroll_x = ttk.Scrollbar(frame_mid, orient=tk.HORIZONTAL)
    scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Columns definition
    cols = ["Chọn", "STT", "MSV", "Họ Tên", "Giới tính", "Lớp", "SĐT"] + [f"T{i}" for i in range(1, 16)] + ["Số lần làm BT", "Vi phạm", "Chuyên Cần", "Cảnh Báo"]
    ui['cols'] = cols
    
    tree = ttk.Treeview(frame_mid, columns=cols, show="headings", 
                             yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    ui['tree'] = tree
    
    scroll_y.config(command=tree.yview)
    scroll_x.config(command=tree.xview)
    
    # Configure headings and columns
    for col in cols:
        heading_text = "☐" if col == "Chọn" else col
        if col != "Chọn":
            tree.heading(col, text=heading_text, command=lambda _col=col: sort_treeview(tree, _col, False))
        else:
            tree.heading(col, text=heading_text)
        
        if col == "Chọn": w = 45
        elif col == "STT": w = 40
        elif col == "MSV": w = 80
        elif col == "Họ Tên": w = 180
        elif col == "Giới tính": w = 70
        elif col == "Lớp": w = 80
        elif col == "SĐT": w = 100
        elif col.startswith("T"): w = 45
        elif col in ["Số lần làm BT", "Vi phạm", "Chuyên Cần"]: w = 90
        else: w = 100
        tree.column(col, width=w, anchor=tk.CENTER if col != "Họ Tên" else tk.W)
        
    tree.pack(fill=tk.BOTH, expand=True)
    
    # ─── STATS BAR (BOTTOM) ───
    frame_bot = tk.Frame(root, pady=10, padx=10, bg="#e0e0e0")
    frame_bot.pack(fill=tk.X)
    
    ui['lbl_si_so'] = tk.Label(frame_bot, text="Sĩ số: 0", font=('Arial', 11, 'bold'), bg="#e0e0e0")
    ui['lbl_si_so'].pack(side=tk.LEFT, padx=20)
    
    ui['lbl_canh_bao'] = tk.Label(frame_bot, text="Cấm thi: 0", font=('Arial', 11, 'bold'), fg="red", bg="#e0e0e0")
    ui['lbl_canh_bao'].pack(side=tk.LEFT, padx=20)
    
    ui['lbl_diem_tb'] = tk.Label(frame_bot, text="Điểm CC TB: 0.00", font=('Arial', 11, 'bold'), bg="#e0e0e0")
    ui['lbl_diem_tb'].pack(side=tk.LEFT, padx=20)
    
    lbl_cong_thuc = tk.Label(frame_bot, text="Công thức CC = 10 - (K * 2) + (BT / 2) - Vi_phạm", font=('Arial', 10, 'italic'), bg="#e0e0e0", fg="#333")
    lbl_cong_thuc.pack(side=tk.LEFT, padx=20)
    
    lbl_huong_dan = tk.Label(frame_bot, text="💡 Double-click vào ô Tuần/BT/VP để chỉnh sửa", font=('Arial', 10, 'italic'), bg="#e0e0e0", fg="#555")
    lbl_huong_dan.pack(side=tk.RIGHT, padx=10)

    return ui


def hien_thi_bang(ui, df):
    """
    Xóa dữ liệu cũ trên bảng và nạp lại toàn bộ dữ liệu từ DataFrame.

    Args:
        ui (dict): Dictionary chứa các widget giao diện.
        df (pandas.DataFrame): Bảng dữ liệu sinh viên.
    """
    tree = ui['tree']
    tree.heading("Chọn", text="☐")  # Reset header
    
    for row in tree.get_children():
        tree.delete(row)
        
    if df.empty:
        return
        
    for idx, (_, row) in enumerate(df.iterrows(), start=1):
        values = [
            "☐",  # Mặc định là chưa chọn
            str(idx), # STT
            row.get("msv", ""),
            row.get("ho_ten", ""),
            row.get("gioi_tinh", "Nam"),
            row.get("lop", ""),
            row.get("sdt", "")
        ]
        # Các tuần
        for i in range(1, 16):
            t_val = row.get(f"t{i}", "M")
            if t_val == "K":
                t_val = "K 🟥"
            elif t_val == "P":
                t_val = "P 🟢"
            values.append(t_val)
            
        # Điểm & cảnh báo
        values.append(f"{float(row.get('so_lan_bt', 0)):.1f}")
        values.append(f"{float(row.get('vi_pham', 0)):.1f}")
        values.append(f"{float(row.get('chuyen_can', 0)):.1f}")
        
        cb = row.get("canh_bao", "")
        values.append(cb)
        
        # Insert row, tag 'cam_thi' to color red if needed
        item_id = tree.insert("", tk.END, values=values)
        if cb == "Cấm thi":
            tree.item(item_id, tags=('cam_thi',))
        elif cb == "Cẩn thận cấm thi":
            tree.item(item_id, tags=('canh_bao_cam_thi',))
            
    tree.tag_configure('cam_thi', foreground='red')
    tree.tag_configure('canh_bao_cam_thi', foreground='orange')


def cap_nhat_thong_ke(ui, stats):
    """
    Cập nhật các nhãn văn bản hiển thị thống kê tổng quan ở góc dưới màn hình.

    Args:
        ui (dict): Dictionary chứa các widget giao diện.
        stats (dict): Dictionary chứa dữ liệu thống kê từ model.
    """
    tong_sv = stats.get('tong_sv', 0)
    nam = stats.get('nam', 0)
    nu = stats.get('nu', 0)
    ui['lbl_si_so'].config(text=f"Sĩ số: {tong_sv} (Nam: {nam}, Nữ: {nu})")
    ui['lbl_canh_bao'].config(text=f"Cấm thi: {stats.get('cam_thi', 0)}")
    ui['lbl_diem_tb'].config(text=f"Điểm CC TB: {stats.get('diem_cc_tb', 0):.2f}")


def hien_thi_form_sinh_vien(parent_root, is_edit=False, current_data=None):
    """
    Hiển thị cửa sổ Pop-up để Thêm hoặc Sửa thông tin Sinh viên.

    Args:
        parent_root (tk.Tk): Cửa sổ cha để popup luôn nổi lên trên.
        is_edit (bool): True nếu là chế độ Sửa, False nếu là Thêm mới.
        current_data (dict): Dữ liệu của sinh viên đang được sửa (nếu có).

    Returns:
        dict/None: Dictionary chứa dữ liệu người dùng nhập hoặc None nếu Hủy.
    """
    top = tk.Toplevel(parent_root)
    top.title("Sửa Sinh viên" if is_edit else "Thêm Sinh viên")
    top.resizable(False, False)
    top.grab_set()
    
    result = []  # Sử dụng list để lưu kết quả (để có thể thay đổi trong inner function)
    
    main_frame = tk.Frame(top, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # --- Form fields ---
    tk.Label(main_frame, text="MSV (*):").grid(row=0, column=0, padx=(0, 10), pady=10, sticky=tk.E)
    ent_msv = ttk.Entry(main_frame, width=35)
    ent_msv.grid(row=0, column=1, pady=10, sticky=tk.W)

    tk.Label(main_frame, text="Họ tên (*):").grid(row=1, column=0, padx=(0, 10), pady=10, sticky=tk.E)
    ent_hoten = ttk.Entry(main_frame, width=35)
    ent_hoten.grid(row=1, column=1, pady=10, sticky=tk.W)
    
    tk.Label(main_frame, text="Giới tính:").grid(row=2, column=0, padx=(0, 10), pady=10, sticky=tk.E)
    cbo_gioitinh = ttk.Combobox(main_frame, values=["Nam", "Nữ", "Khác"], state="readonly", width=32)
    cbo_gioitinh.set("Nam")
    cbo_gioitinh.grid(row=2, column=1, pady=10, sticky=tk.W)
    
    tk.Label(main_frame, text="Lớp:").grid(row=3, column=0, padx=(0, 10), pady=10, sticky=tk.E)
    ent_lop = ttk.Entry(main_frame, width=35)
    ent_lop.grid(row=3, column=1, pady=10, sticky=tk.W)

    tk.Label(main_frame, text="SĐT:").grid(row=4, column=0, padx=(0, 10), pady=10, sticky=tk.E)
    ent_sdt = ttk.Entry(main_frame, width=35)
    ent_sdt.grid(row=4, column=1, pady=10, sticky=tk.W)
    
    if is_edit and current_data:
        ent_msv.insert(0, current_data.get("msv", ""))
        ent_hoten.insert(0, current_data.get("ho_ten", ""))
        cbo_gioitinh.set(current_data.get("gioi_tinh", "Nam"))
        ent_lop.insert(0, current_data.get("lop", ""))
        ent_sdt.insert(0, current_data.get("sdt", ""))
        
    def on_luu():
        msv = ent_msv.get().strip()
        hoten = ent_hoten.get().strip()
        gioi_tinh = cbo_gioitinh.get()
        lop = ent_lop.get().strip()
        sdt = ent_sdt.get().strip()
        
        if not msv:
            messagebox.showwarning("Lỗi", "MSV không được để trống!", parent=top)
            return
        if not hoten:
            messagebox.showwarning("Lỗi", "Họ tên không được để trống!", parent=top)
            return
            
        result.append({
            "msv": msv,
            "ho_ten": hoten,
            "gioi_tinh": gioi_tinh,
            "lop": lop,
            "sdt": sdt
        })
        top.destroy()

    # --- Buttons ---
    frame_btn = tk.Frame(main_frame)
    frame_btn.grid(row=5, column=0, columnspan=2, pady=(20, 0))
    
    btn_luu = ttk.Button(frame_btn, text="Lưu", command=on_luu)
    btn_luu.pack(side=tk.LEFT, padx=10)
    
    btn_huy = ttk.Button(frame_btn, text="Hủy", command=top.destroy)
    btn_huy.pack(side=tk.LEFT, padx=10)
    
    # Canh giữa popup
    top.update_idletasks()
    x = parent_root.winfo_x() + (parent_root.winfo_width() - top.winfo_reqwidth()) // 2
    y = parent_root.winfo_y() + (parent_root.winfo_height() - top.winfo_reqheight()) // 2
    top.geometry(f"+{x}+{y}")
    
    top.wait_window()
    return result[0] if result else None

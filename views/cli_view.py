"""
views/cli_view.py
=================
Module hiển thị giao diện CLI trên Terminal cho Quản lý Điểm danh.
"""

def hien_menu_chinh():
    """
    Hiển thị menu chính và nhận đầu vào từ bàn phím.

    Returns:
        str: Lựa chọn của người dùng (từ '0' đến '7').
    """
    print()
    print("╔══════════════════════════════════════════╗")
    print("║          📅 SMARTATTEND (CLI)            ║")
    print("╠══════════════════════════════════════════╣")
    print("║  1. Xem danh sách điểm danh             ║")
    print("║  2. Thêm sinh viên                      ║")
    print("║  3. Sửa thông tin sinh viên             ║")
    print("║  4. Xóa sinh viên                       ║")
    print("║  5. Điểm danh theo tuần                 ║")
    print("║  6. Cập nhật Số lần BT / Vi phạm        ║")
    print("║  7. Xem thống kê                        ║")
    print("║  0. Thoát                               ║")
    print("╚══════════════════════════════════════════╝")
    lua_chon = input("  Chọn chức năng: ").strip()
    return lua_chon


def hien_bang_diemdanh(df):
    """
    Hiển thị danh sách điểm danh dạng bảng văn bản trên Terminal.

    Args:
        df (pandas.DataFrame): Bảng dữ liệu điểm danh.
    """
    if df.empty:
        print("\n  (Chưa có sinh viên nào)")
        return

    print("\n  BẢNG ĐIỂM DANH LỚP HỌC")
    # Header format: MSV(6) | HoTen(18) | GT(4) | Lop(10) | T1..T15(2 each) | BT(4) | VP(4) | CC(4) | CB(8)
    header = f"  {'MSV':<6} {'Họ tên':<18} {'GT':<4} {'Lớp':<10} "
    for i in range(1, 16):
        header += f"{i:02d} "
    header += f"{'BT':>4} {'VP':>4} {'CC':>5} {'Cảnh báo'}"
    
    print(header)
    print("  " + "─" * len(header.strip()))

    for _, row in df.iterrows():
        msv = row['msv']
        ho_ten = str(row['ho_ten'])[:17]  # Truncate to 17 chars
        gt = str(row.get('gioi_tinh', 'Nam'))[:4]
        lop = str(row.get('lop', ''))[:9]
        
        row_str = f"  {msv:<6} {ho_ten:<18} {gt:<4} {lop:<10} "
        for i in range(1, 16):
            t = str(row.get(f"t{i}", "M"))
            row_str += f"{t:<2} "
            
        bt = float(row.get('so_lan_bt', 0))
        vp = float(row.get('vi_pham', 0))
        cc = float(row.get('chuyen_can', 0))
        cb = row.get('canh_bao', "")
        
        row_str += f"{bt:>4.1f} {vp:>4.1f} {cc:>5.1f}  {cb}"
        print(row_str)

    print(f"\n  Tổng: {len(df)} sinh viên")


def hien_thong_ke(stats):
    """
    Hiển thị khung thống kê lớp học.

    Args:
        stats (dict): Dictionary chứa các số liệu tổng hợp.
    """
    if not stats or stats.get("tong_sv", 0) == 0:
        print("\n  (Chưa có dữ liệu thống kê)")
        return

    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║            📊 THỐNG KÊ LỚP HỌC          ║")
    print("  ╠══════════════════════════════════════════╣")
    si_so_str = f"{stats['tong_sv']} (Nam: {stats.get('nam', 0)}, Nữ: {stats.get('nu', 0)})"
    print(f"  ║  Sĩ số lớp      : {si_so_str:<21} ║")
    print(f"  ║  Số SV cấm thi  : {stats.get('cam_thi', 0):<21} ║")
    print(f"  ║  Điểm CC TB     : {stats.get('diem_cc_tb', 0):<21.2f} ║")
    print("  ╚══════════════════════════════════════════╝")


# ─── NHẬP LIỆU ──────────────────────────────────

def nhap_thong_tin_sv(current_msv=""):
    """
    Hỗ trợ nhập liệu thông tin cá nhân của sinh viên từ Terminal.

    Args:
        current_msv (str): Mã sinh viên hiện tại (dùng khi sửa thông tin).

    Returns:
        dict/None: Thông tin sinh viên hoặc None nếu nhập thiếu.
    """
    print("\n  ── Nhập thông tin sinh viên ──")
    if current_msv:
        msv = input(f"  MSV mới (Enter để giữ {current_msv}): ").strip() or current_msv
    else:
        msv = input("  MSV        : ").strip()
        
    ho_ten = input("  Họ tên     : ").strip()
    lop = input("  Lớp        : ").strip()
    sdt = input("  SĐT        : ").strip()

    if not msv or not ho_ten:
        thong_bao("❌ MSV và Họ tên không được để trống!")
        return None

    return {
        "msv": msv,
        "ho_ten": ho_ten,
        "lop": lop,
        "sdt": sdt,
    }


def nhap_msv():
    """Nhập mã sinh viên."""
    return input("\n  Nhập MSV (VD: SV001): ").strip().upper()


def nhap_tuan_diem_danh():
    """Nhập số tuần để điểm danh cả lớp."""
    tuan = input("\n  Nhập số tuần cần điểm danh (1-15): ").strip()
    try:
        t_int = int(tuan)
        if t_int < 1 or t_int > 15:
            thong_bao("❌ Tuần phải từ 1 đến 15!")
            return None
        return f"t{t_int}"
    except:
        thong_bao("❌ Vui lòng nhập số nguyên!")
        return None


def nhap_trang_thai_sv(msv, ho_ten):
    """Nhập trạng thái điểm danh cho 1 sinh viên cụ thể."""
    while True:
        tt = input(f"  [{msv}] {ho_ten:<20} - Trạng thái (M/P/K, Enter để mặc định là M): ").strip().upper()
        if not tt:
            return "M"
        if tt in ["M", "P", "K"]:
            return tt
        print("  ❌ Không hợp lệ. Chỉ nhập M (Có mặt), P (Phép), K (Không phép).")


def nhap_cap_nhat_diem():
    """Trả về (loai_diem, gia_tri)"""
    loai = input("  Bạn muốn cập nhật (1) Số lần BT hay (2) Vi phạm?: ").strip()
    if loai not in ["1", "2"]:
        thong_bao("❌ Lựa chọn không hợp lệ!")
        return None, None
        
    try:
        if loai == "1":
            diem = float(input("  Nhập Số lần làm Bài tập: ").strip())
        else:
            diem = float(input("  Nhập số điểm trừ Vi phạm: ").strip())
            
        if diem < 0:
            thong_bao("❌ Giá trị phải >= 0!")
            return None, None
            
        return loai, diem
    except:
        thong_bao("❌ Vui lòng nhập số hợp lệ!")
        return None, None

# ─── TIỆN ÍCH ──────────────────────────────────

def thong_bao(msg):
    """Hiển thị thông báo."""
    print(f"\n  {msg}")

def xac_nhan(msg):
    """Hỏi xác nhận yes/no."""
    tra_loi = input(f"\n  {msg} (y/n): ").strip().lower()
    return tra_loi in ("y", "yes")

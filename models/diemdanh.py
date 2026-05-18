import os
import sys
import shutil
import pandas as pd
import numpy as np
from utils.logger import setup_logger

logger = setup_logger()

# ─── Đường dẫn file CSV ──────────────────────────
if getattr(sys, 'frozen', False):
    _USER_DIR = os.path.join(os.path.expanduser("~"), "SmartAttend_Data")
    _BASE_DIR = _USER_DIR
    
    _INSTALL_DATA = os.path.join(os.path.dirname(sys.executable), "data")
    _USER_DATA = os.path.join(_BASE_DIR, "data")
    
    if not os.path.exists(_USER_DATA):
        os.makedirs(_USER_DATA, exist_ok=True)
        for f in ["diemdanh.csv"]:
            src = os.path.join(_INSTALL_DATA, f)
            dst = os.path.join(_USER_DATA, f)
            if os.path.exists(src):
                shutil.copy2(src, dst)
else:
    _BASE_DIR = os.path.dirname(os.path.dirname(__file__))

FILE_DIEMDANH = os.path.join(_BASE_DIR, "data", "diemdanh.csv")


def khoi_tao_csv():
    """
    Tạo file csv rỗng nếu chưa tồn tại.
    Khởi tạo các cột cơ bản và 15 tuần điểm danh.
    """
    os.makedirs(os.path.dirname(FILE_DIEMDANH), exist_ok=True)
    if not os.path.exists(FILE_DIEMDANH):
        cols = ["msv", "ho_ten", "lop", "sdt"] + [f"t{i}" for i in range(1, 16)] + ["so_lan_bt", "vi_pham"]
        df_empty = pd.DataFrame(columns=cols)
        df_empty.to_csv(FILE_DIEMDANH, index=False, encoding="utf-8-sig")
        logger.info(f"Đã tạo file mới: {FILE_DIEMDANH}")


def lay_danh_sach():
    """
    Đọc dữ liệu từ CSV và dùng Numpy tính toán realtime các cột:
    - tong_vang_kp: Tổng số buổi vắng không phép (K)
    - tong_vang_p: Tổng số buổi vắng có phép (P)
    - chuyen_can: Điểm chuyên cần cuối cùng
    - canh_bao: Cảnh báo "Cấm thi" nếu tổng vắng > 3

    Returns:
        tuple: (pandas.DataFrame chứa dữ liệu, bool Trạng thái thành công)
    """
    khoi_tao_csv()
    try:
        df = pd.read_csv(FILE_DIEMDANH, encoding="utf-8-sig", dtype=str)
    except Exception as e:
        logger.error(f"Lỗi đọc file: {e}")
        return pd.DataFrame(), False
    
    if df.empty:
        return df, True

    # Đảm bảo các cột số/chữ tồn tại để tương thích file cũ, và xử lý giá trị rỗng/NaN
    for text_col in ["msv", "ho_ten", "gioi_tinh", "lop", "sdt"]:
        if text_col not in df.columns:
            df[text_col] = "-"
        df[text_col] = df[text_col].fillna("-").replace("", "-")
        # Fix trường hợp chuỗi "nan" từ pandas
        df[text_col] = df[text_col].astype(str).replace("nan", "-")

    if "so_lan_bt" not in df.columns:
        df["so_lan_bt"] = 0.0
    if "vi_pham" not in df.columns:
        df["vi_pham"] = 0.0
        
    # Ép kiểu các cột số về float, nếu lỗi NaN thì cho = 0
    df["so_lan_bt"] = pd.to_numeric(df["so_lan_bt"], errors="coerce").fillna(0)
    df["vi_pham"] = pd.to_numeric(df["vi_pham"], errors="coerce").fillna(0)
    
    # Lấy ra danh sách các cột điểm danh (t1 đến t15)
    t_cols = [f"t{i}" for i in range(1, 16)]
    
    # Đảm bảo các cột t1..t15 đều tồn tại
    for col in t_cols:
        if col not in df.columns:
            df[col] = "M"
            
    # Chuyển các cột tuần về chuỗi in hoa, điền thiếu bằng 'M'
    for col in t_cols:
        df[col] = df[col].fillna("M").str.upper()

    # TÍNH TOÁN BẰNG NUMPY (Vectorization)
    arr_t = df[t_cols].values  # Ma trận 2D
    
    # Đếm số buổi K, P trên mỗi dòng (mỗi sinh viên)
    tong_vang_kp = np.sum(arr_t == "K", axis=1)
    tong_vang_p = np.sum(arr_t == "P", axis=1)
    
    # Tổng vắng
    tong_vang = tong_vang_kp + tong_vang_p
    
    # Điều kiện cảnh báo: vắng > 3 buổi -> "Cấm thi", vắng == 3 -> "Cẩn thận cấm thi", ngược lại rỗng
    canh_bao = np.where(tong_vang > 3, "Cấm thi", np.where(tong_vang == 3, "Cẩn thận cấm thi", ""))
    
    # Tính điểm chuyên cần
    # Công thức: 10 - (KP * 2) + (so_lan_bt * 0.5) - vi_pham
    so_lan_bt_arr = df["so_lan_bt"].values
    vi_pham_arr = df["vi_pham"].values
    diem_cc = 10.0 - (tong_vang_kp * 2.0) + (so_lan_bt_arr * 0.5) - vi_pham_arr
    
    # Giới hạn min=0, max=10
    diem_cc = np.clip(diem_cc, 0, 10)
    
    # Nếu cấm thi -> điểm CC = 0
    diem_cc = np.where(canh_bao == "Cấm thi", 0.0, diem_cc)
    
    # Gán ngược lại vào DataFrame để View hiển thị
    df["tong_vang_kp"] = tong_vang_kp
    df["tong_vang_p"] = tong_vang_p
    df["chuyen_can"] = diem_cc
    df["canh_bao"] = canh_bao

    return df, True


def luu_danh_sach(df):
    """
    Ghi DataFrame hiện tại xuống CSV (chỉ ghi các cột cơ bản, không ghi cột tính toán).

    Args:
        df (pandas.DataFrame): Dữ liệu cần lưu.

    Returns:
        bool: True nếu lưu thành công, False nếu thất bại.
    """
    try:
        # Lọc ra chỉ các cột cần lưu
        cols_to_save = ["msv", "ho_ten", "gioi_tinh", "lop", "sdt"] + [f"t{i}" for i in range(1, 16)] + ["so_lan_bt", "vi_pham"]
        df_save = df[cols_to_save]
        df_save.to_csv(FILE_DIEMDANH, index=False, encoding="utf-8-sig")
        logger.debug(f"Ghi file diemdanh.csv ({len(df)} dòng)")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi ghi file: {e}")
        return False


def them_sinh_vien(df, data):
    """
    Thêm SV mới vào DataFrame.

    Args:
        df (pandas.DataFrame): Bảng dữ liệu hiện tại.
        data (dict): Thông tin SV (msv, ho_ten, gioi_tinh, lop, sdt).

    Returns:
        tuple: (DataFrame mới, bool Trạng thái, str Thông báo)
    """
    msv_moi = str(data.get("msv", "")).strip().upper()
    if not msv_moi:
        return df, False, "Mã sinh viên không được để trống!"
        
    if msv_moi in df["msv"].values:
        return df, False, "Mã sinh viên đã tồn tại!"

    row = {
        "msv": msv_moi,
        "ho_ten": data.get("ho_ten", ""),
        "gioi_tinh": data.get("gioi_tinh", "Nam"),
        "lop": data.get("lop", ""),
        "sdt": data.get("sdt", ""),
        "so_lan_bt": 0.0,
        "vi_pham": 0.0
    }
    # Tự động gán M (Có mặt) cho 15 tuần
    for i in range(1, 16):
        row[f"t{i}"] = "M"

    df_new = pd.DataFrame([row])
    df = pd.concat([df, df_new], ignore_index=True)
    luu_danh_sach(df)
    logger.info(f"Đã thêm: {row['ho_ten']} ({msv_moi})")
    return df, True, f"Thêm SV thành công: {msv_moi}"


def sua_sinh_vien(df, old_msv, data):
    """
    Cập nhật thông tin sinh viên đã tồn tại.

    Args:
        df (pandas.DataFrame): Bảng dữ liệu hiện tại.
        old_msv (str): Mã sinh viên cũ cần sửa.
        data (dict): Thông tin mới của sinh viên.

    Returns:
        tuple: (DataFrame mới, bool Trạng thái, str Thông báo)
    """
    idx = df.index[df["msv"] == old_msv]
    if len(idx) == 0:
        return df, False, "Không tìm thấy mã sinh viên!"
    
    new_msv = str(data.get("msv", "")).strip().upper()
    if not new_msv:
        return df, False, "Mã sinh viên không được để trống!"
        
    if new_msv != old_msv and new_msv in df["msv"].values:
        return df, False, "Mã sinh viên mới đã tồn tại!"
    
    df.loc[idx, "msv"] = new_msv
    df.loc[idx, "ho_ten"] = data.get("ho_ten", "")
    df.loc[idx, "gioi_tinh"] = data.get("gioi_tinh", "Nam")
    df.loc[idx, "lop"] = data.get("lop", "")
    df.loc[idx, "sdt"] = data.get("sdt", "")
    luu_danh_sach(df)
    logger.info(f"Đã sửa SV: {old_msv} -> {new_msv}")
    return df, True, f"Sửa SV thành công: {new_msv}"


def xoa_sinh_vien(df, msv):
    """
    Xóa sinh viên khỏi danh sách.

    Args:
        df (pandas.DataFrame): Bảng dữ liệu hiện tại.
        msv (str): Mã sinh viên cần xóa.

    Returns:
        tuple: (DataFrame mới, bool Trạng thái, str Thông báo)
    """
    idx = df.index[df["msv"] == msv]
    if len(idx) == 0:
        return df, False, "Không tìm thấy mã sinh viên!"
    
    df = df.drop(idx)
    luu_danh_sach(df)
    return df, True, "Xóa thành công!"

def xoa_nhieu_sinh_vien(df, msv_list):
    """
    Xóa nhiều sinh viên cùng lúc dựa trên danh sách msv.

    Args:
        df (pandas.DataFrame): Bảng dữ liệu hiện tại.
        msv_list (list): Danh sách các mã sinh viên cần xóa.

    Returns:
        tuple: (DataFrame mới, bool Trạng thái, str Thông báo)
    """
    if not msv_list:
        return df, False, "Danh sách trống!"
        
    df = df[~df["msv"].isin(msv_list)]
    luu_danh_sach(df)
    return df, True, f"Đã xóa {len(msv_list)} sinh viên!"


def cap_nhat_diem_danh(df, msv, tuan, trang_thai):
    """
    Cập nhật trạng thái điểm danh của 1 tuần (tuan là chuỗi 't1', 't2'...).

    Args:
        df (pandas.DataFrame): Bảng dữ liệu hiện tại.
        msv (str): Mã sinh viên.
        tuan (str): Mã tuần (vd: 't1').
        trang_thai (str): Trạng thái (M, P, K).

    Returns:
        tuple: (DataFrame mới, bool Trạng thái)
    """
    idx = df.index[df["msv"] == msv]
    if len(idx) == 0:
        return df, False
    
    df.loc[idx, tuan] = trang_thai
    luu_danh_sach(df)
    return df, True


def cap_nhat_so_lan_bt(df, msv, so_lan):
    """
    Cập nhật số lần làm bài tập.

    Args:
        df (pandas.DataFrame): Bảng dữ liệu hiện tại.
        msv (str): Mã sinh viên.
        so_lan (int/float): Số lần hoàn thành bài tập.

    Returns:
        tuple: (DataFrame mới, bool Trạng thái)
    """
    idx = df.index[df["msv"] == msv]
    if len(idx) == 0:
        return df, False
    
    df.loc[idx, "so_lan_bt"] = so_lan
    luu_danh_sach(df)
    return df, True

def cap_nhat_vi_pham(df, msv, diem_tru):
    """
    Cập nhật điểm trừ vi phạm.

    Args:
        df (pandas.DataFrame): Bảng dữ liệu hiện tại.
        msv (str): Mã sinh viên.
        diem_tru (int/float): Số điểm trừ vi phạm.

    Returns:
        tuple: (DataFrame mới, bool Trạng thái)
    """
    idx = df.index[df["msv"] == msv]
    if len(idx) == 0:
        return df, False
    
    df.loc[idx, "vi_pham"] = diem_tru
    luu_danh_sach(df)
    return df, True


def thong_ke(df):
    """
    Trích xuất từ dữ liệu để tạo Dict thống kê cho UI/CLI.

    Args:
        df (pandas.DataFrame): Bảng dữ liệu hiện tại.

    Returns:
        dict: Chứa các trường thống kê (tong_sv, cam_thi, diem_cc_tb, nam, nu).
    """
    if df.empty:
        return {}
    
    stats = {
        "tong_sv": len(df),
        "cam_thi": int(np.sum(df["canh_bao"] == "Cấm thi")),
        "diem_cc_tb": float(np.mean(df["chuyen_can"])),
        "nam": int(np.sum(df["gioi_tinh"].str.strip().str.lower() == "nam")),
        "nu": int(np.sum(df["gioi_tinh"].str.strip().str.lower() == "nữ"))
    }
    return stats

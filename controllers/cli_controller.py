"""
controllers/cli_controller.py
=============================
Controller điều phối luồng xử lý cho giao diện CLI.
Kết nối giữa cli_view và mô hình dữ liệu (models/diemdanh.py).
"""

import sys
from views import cli_view
from models import diemdanh
from utils.logger import setup_logger

logger = setup_logger()

def _xem_danh_sach():
    """Lấy danh sách từ models và gửi sang views để in ra màn hình."""
    logger.info("CLI: Người dùng xem danh sách.")
    df, ok = diemdanh.lay_danh_sach()
    if ok:
        cli_view.hien_bang_diemdanh(df)
    else:
        cli_view.thong_bao("❌ Lỗi khi đọc dữ liệu điểm danh.")

def _them_sinh_vien():
    """Điều phối luồng nhập liệu từ views và lưu vào models."""
    logger.info("CLI: Người dùng chọn chức năng Thêm sinh viên.")
    df, ok = diemdanh.lay_danh_sach()
    data = cli_view.nhap_thong_tin_sv()
    if data:
        _, ok_them, msg = diemdanh.them_sinh_vien(df, data)
        cli_view.thong_bao(f"✅ {msg}" if ok_them else f"❌ {msg}")

def _sua_sinh_vien():
    """Điều phối luồng tìm kiếm sinh viên cũ và cập nhật thông tin mới."""
    logger.info("CLI: Người dùng chọn chức năng Sửa sinh viên.")
    df, ok = diemdanh.lay_danh_sach()
    msv = cli_view.nhap_msv()
    if not msv: return
    data = cli_view.nhap_thong_tin_sv(current_msv=msv)
    if data:
        _, ok_sua, msg = diemdanh.sua_sinh_vien(df, msv, data)
        cli_view.thong_bao(f"✅ {msg}" if ok_sua else f"❌ {msg}")

def _xoa_sinh_vien():
    """Xóa sinh viên sau khi yêu cầu xác nhận từ CLI View."""
    logger.info("CLI: Người dùng chọn chức năng Xóa sinh viên.")
    df, ok = diemdanh.lay_danh_sach()
    msv = cli_view.nhap_msv()
    if not msv: return
    if cli_view.xac_nhan(f"Bạn có chắc muốn xóa MSV {msv}?"):
        _, ok_xoa, msg = diemdanh.xoa_sinh_vien(df, msv)
        cli_view.thong_bao(f"✅ {msg}" if ok_xoa else f"❌ {msg}")

def _diem_danh():
    """Luồng điểm danh hàng loạt: Hỏi tuần, sau đó lặp qua từng sinh viên."""
    logger.info("CLI: Người dùng chọn chức năng Điểm danh lớp.")
    df, ok = diemdanh.lay_danh_sach()
    if df.empty:
        cli_view.thong_bao("❌ Chưa có sinh viên nào trong danh sách!")
        return
        
    tuan = cli_view.nhap_tuan_diem_danh()
    if not tuan: return
    
    print(f"\n  ── Bắt đầu điểm danh {tuan.upper()} ──")
    for _, row in df.iterrows():
        msv = row["msv"]
        ho_ten = row["ho_ten"]
        trang_thai = cli_view.nhap_trang_thai_sv(msv, ho_ten)
        df, _ = diemdanh.cap_nhat_diem_danh(df, msv, tuan, trang_thai)
        
    cli_view.thong_bao("✅ Hoàn thành điểm danh lớp!")

def _cap_nhat_bt_vp():
    """Điều phối luồng cập nhật số lần làm bài tập hoặc điểm trừ vi phạm."""
    logger.info("CLI: Người dùng chọn chức năng Cập nhật Bài tập/Vi phạm.")
    df, ok = diemdanh.lay_danh_sach()
    msv = cli_view.nhap_msv()
    if not msv: return
    loai, diem = cli_view.nhap_cap_nhat_diem()
    if loai == "1":
        _, ok_update = diemdanh.cap_nhat_so_lan_bt(df, msv, diem)
    elif loai == "2":
        _, ok_update = diemdanh.cap_nhat_vi_pham(df, msv, diem)
    else:
        return
        
    if ok_update:
        cli_view.thong_bao("✅ Cập nhật thành công!")
    else:
        cli_view.thong_bao("❌ Không tìm thấy MSV hoặc có lỗi xảy ra.")

def _thong_ke():
    """Tính toán dữ liệu thống kê từ models và gửi in ra views."""
    logger.info("CLI: Người dùng xem thống kê.")
    df, ok = diemdanh.lay_danh_sach()
    if ok:
        stats = diemdanh.thong_ke(df)
        cli_view.hien_thong_ke(stats)
    else:
        cli_view.thong_bao("❌ Lỗi khi đọc dữ liệu điểm danh.")


def chay_ung_dung():
    """Khởi chạy ứng dụng điểm danh trên CLI."""
    logger.info("Khởi động ứng dụng (CLI)")
    try:
        while True:
            lua_chon = cli_view.hien_menu_chinh()

            if lua_chon == "1":
                _xem_danh_sach()
            elif lua_chon == "2":
                _them_sinh_vien()
            elif lua_chon == "3":
                _sua_sinh_vien()
            elif lua_chon == "4":
                _xoa_sinh_vien()
            elif lua_chon == "5":
                _diem_danh()
            elif lua_chon == "6":
                _cap_nhat_bt_vp()
            elif lua_chon == "7":
                _thong_ke()
            elif lua_chon == "0":
                print("\n  Cảm ơn bạn đã sử dụng chương trình!")
                logger.info("Người dùng thoát chương trình.")
                break
            else:
                cli_view.thong_bao("❌ Lựa chọn không hợp lệ, vui lòng thử lại!")
    except KeyboardInterrupt:
        print("\n\n  Thoát chương trình đột ngột (Ctrl+C).")
        logger.warning("Thoát đột ngột do KeyboardInterrupt.")
        sys.exit(0)
    except Exception as e:
        cli_view.thong_bao(f"❌ Có lỗi bất ngờ xảy ra: {e}")
        logger.error(f"Ngoại lệ chưa bắt: {e}", exc_info=True)

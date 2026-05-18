import os
import unittest
import pandas as pd
from models import diemdanh

class TestDiemDanhModel(unittest.TestCase):
    """Bộ kiểm thử cho các logic tính toán và xử lý dữ liệu trong models/diemdanh.py"""
    
    def setUp(self):
        """Hàm chạy trước mỗi test case. Thiết lập môi trường test giả lập."""
        # Chuyển hướng lưu file sang một file test tạm thời để không làm hỏng dữ liệu thật
        self.test_file = os.path.join(os.path.dirname(__file__), "test_diemdanh.csv")
        diemdanh.FILE_DIEMDANH = self.test_file
        
        # Đảm bảo môi trường sạch
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """Hàm chạy sau mỗi test case. Dọn dẹp rác."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_khoi_tao_csv(self):
        """Test việc hệ thống tự động tạo file CSV rỗng đúng cấu trúc khi chưa có file."""
        df, ok = diemdanh.lay_danh_sach()
        
        self.assertTrue(ok)
        self.assertTrue(df.empty)
        self.assertTrue(os.path.exists(self.test_file))

    def test_them_sinh_vien(self):
        """Test luồng thêm sinh viên và validate trùng MSV."""
        df, _ = diemdanh.lay_danh_sach()
        data = {
            "msv": "SV001",
            "ho_ten": "Nguyen Van A",
            "gioi_tinh": "Nam",
            "lop": "K21A",
            "sdt": "01234"
        }
        
        # Thêm lần 1 (Kỳ vọng: Thành công)
        df, ok, msg = diemdanh.them_sinh_vien(df, data)
        self.assertTrue(ok)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["msv"], "SV001")
        
        # Thêm trùng lần 2 (Kỳ vọng: Thất bại, chặn trùng)
        df, ok_trung, msg_trung = diemdanh.them_sinh_vien(df, data)
        self.assertFalse(ok_trung)
        self.assertEqual(len(df), 1)
        self.assertIn("đã tồn tại", msg_trung)

    def test_tinh_chuyen_can(self):
        """Test logic tính toán điểm chuyên cần và cảnh báo cấm thi của Numpy."""
        df, _ = diemdanh.lay_danh_sach()
        # Thêm 1 sinh viên để test
        data = {"msv": "SV002", "ho_ten": "Tran B"}
        df, _, _ = diemdanh.them_sinh_vien(df, data)
        
        # Cập nhật điểm danh: Vắng 1 không phép (K), Vắng 1 có phép (P), còn lại Có mặt (M) mặc định
        df, _ = diemdanh.cap_nhat_diem_danh(df, "SV002", "t1", "K")
        df, _ = diemdanh.cap_nhat_diem_danh(df, "SV002", "t2", "P")
        
        # Cập nhật số lần làm BT (0.5 điểm/lần) và Vi phạm (-1 điểm)
        df, _ = diemdanh.cap_nhat_so_lan_bt(df, "SV002", 2) # +1.0
        df, _ = diemdanh.cap_nhat_vi_pham(df, "SV002", 1)  # -1.0
        
        # Lấy danh sách lại để kích hoạt hàm tính toán Vectorization của Numpy
        df_tinh, ok = diemdanh.lay_danh_sach()
        self.assertTrue(ok)
        
        # Công thức: 10 - (K*2) + (BT*0.5) - VP
        # = 10 - (1*2) + (2*0.5) - 1 = 10 - 2 + 1 - 1 = 8.0
        cc = df_tinh.iloc[0]["chuyen_can"]
        self.assertEqual(cc, 8.0)
        
        # Test Cảnh báo "Cấm thi" (nếu vắng > 3 buổi tổng cộng)
        df, _ = diemdanh.cap_nhat_diem_danh(df, "SV002", "t3", "K")
        df, _ = diemdanh.cap_nhat_diem_danh(df, "SV002", "t4", "K")
        df_tinh, _ = diemdanh.lay_danh_sach()
        
        # Tổng vắng: t1(K) + t2(P) + t3(K) + t4(K) = 4 buổi -> Bị cấm thi!
        cb = df_tinh.iloc[0]["canh_bao"]
        self.assertEqual(cb, "Cấm thi")
        # Khi bị cấm thi thì điểm CC tự ép về 0
        self.assertEqual(df_tinh.iloc[0]["chuyen_can"], 0.0)

    def test_sua_sinh_vien(self):
        """Test luồng sửa thông tin sinh viên."""
        df, _ = diemdanh.lay_danh_sach()
        data = {"msv": "SV001", "ho_ten": "A", "gioi_tinh": "Nam", "lop": "K1", "sdt": "111"}
        df, _, _ = diemdanh.them_sinh_vien(df, data)
        data2 = {"msv": "SV002", "ho_ten": "B"}
        df, _, _ = diemdanh.them_sinh_vien(df, data2)
        
        # Sửa SV001 thành SV003
        data_sua = {"msv": "SV003", "ho_ten": "A_updated"}
        df, ok, msg = diemdanh.sua_sinh_vien(df, "SV001", data_sua)
        self.assertTrue(ok)
        self.assertEqual(df.loc[df["msv"] == "SV003", "ho_ten"].values[0], "A_updated")
        self.assertEqual(len(df.index[df["msv"] == "SV001"]), 0)
        
        # Sửa SV003 thành SV002 (bị trùng)
        data_sua_trung = {"msv": "SV002", "ho_ten": "A_updated"}
        df, ok_trung, msg_trung = diemdanh.sua_sinh_vien(df, "SV003", data_sua_trung)
        self.assertFalse(ok_trung)
        self.assertIn("đã tồn tại", msg_trung)

    def test_xoa_sinh_vien(self):
        """Test xoá 1 sinh viên."""
        df, _ = diemdanh.lay_danh_sach()
        df, _, _ = diemdanh.them_sinh_vien(df, {"msv": "SV999", "ho_ten": "X"})
        
        df, ok, _ = diemdanh.xoa_sinh_vien(df, "SV999")
        self.assertTrue(ok)
        self.assertEqual(len(df.index[df["msv"] == "SV999"]), 0)

    def test_xoa_nhieu_sinh_vien(self):
        """Test xoá nhiều sinh viên."""
        df, _ = diemdanh.lay_danh_sach()
        df, _, _ = diemdanh.them_sinh_vien(df, {"msv": "SV01", "ho_ten": "A"})
        df, _, _ = diemdanh.them_sinh_vien(df, {"msv": "SV02", "ho_ten": "B"})
        df, _, _ = diemdanh.them_sinh_vien(df, {"msv": "SV03", "ho_ten": "C"})
        
        df, ok, _ = diemdanh.xoa_nhieu_sinh_vien(df, ["SV01", "SV03"])
        self.assertTrue(ok)
        self.assertEqual(len(df.index[df["msv"] == "SV02"]), 1)
        self.assertEqual(len(df.index[df["msv"] == "SV01"]), 0)

    def test_thong_ke(self):
        """Test hàm thống kê."""
        df, _ = diemdanh.lay_danh_sach()
        df, _, _ = diemdanh.them_sinh_vien(df, {"msv": "SV1", "gioi_tinh": "Nam"})
        df, _, _ = diemdanh.them_sinh_vien(df, {"msv": "SV2", "gioi_tinh": "Nữ"})
        df, _, _ = diemdanh.them_sinh_vien(df, {"msv": "SV3", "gioi_tinh": "Nữ"})
        
        # Cho SV1 bị cấm thi (vắng 4 buổi)
        for i in range(1, 5):
            df, _ = diemdanh.cap_nhat_diem_danh(df, "SV1", f"t{i}", "K")
        
        # Cần lấy lại danh sách để kích hoạt logic tính điểm numpy
        df_tinh, _ = diemdanh.lay_danh_sach()
        stats = diemdanh.thong_ke(df_tinh)
        
        self.assertEqual(stats["tong_sv"], 3)
        self.assertEqual(stats["nam"], 1)
        self.assertEqual(stats["nu"], 2)
        self.assertEqual(stats["cam_thi"], 1)
        # SV1 cấm thi (0 điểm), SV2 và SV3 10 điểm -> TB = (0 + 10 + 10) / 3 = 6.666
        self.assertAlmostEqual(stats["diem_cc_tb"], 20.0 / 3.0, places=2)

if __name__ == '__main__':
    unittest.main()

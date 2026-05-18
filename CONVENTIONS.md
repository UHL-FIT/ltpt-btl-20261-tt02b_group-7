# Mã nguồn chuẩn (Coding Conventions)

Dự án `SmartAttend` hướng đến độ ổn định, khả năng bảo trì và có thể bàn giao thương mại (Client-ready). Mọi đoạn code được viết ra phải tuân thủ nghiêm ngặt các tiêu chuẩn sau:

## 1. Naming Conventions (Quy chuẩn Đặt tên)
Áp dụng tiêu chuẩn **PEP 8**:
- **Biến và Hàm (Variables & Functions)**: Sử dụng `snake_case`. (Ví dụ: `lay_danh_sach()`, `tong_sv`).
- **Hằng số (Constants)**: Sử dụng `UPPER_SNAKE_CASE`. (Ví dụ: `FILE_DIEMDANH`, `MAX_WEEKS`).
- **Lớp (Classes - Nếu có)**: Sử dụng `PascalCase`. (Ví dụ: `StudentManager`).

## 2. Quản lý Phiên bản (Versioning)
Sử dụng **Semantic Versioning (SemVer)** `v[MAJOR].[MINOR].[PATCH]` để đánh dấu các bản release.
- **`MAJOR`**: Thay đổi cấu trúc dữ liệu hoặc luồng lớn khiến phiên bản cũ không còn tương thích (Ví dụ từ `v1.x` lên `v2.0.0`).
- **`MINOR`**: Thêm tính năng mới (Ví dụ: Thêm cột giới tính, lọc theo danh sách).
- **`PATCH`**: Vá lỗi (Bug fixes), chỉnh sửa UI nhỏ giọt.
- Phiên bản hiện tại của app được đánh dấu toàn cục ở `__version__ = "1.0.0"` tại file entry point.

## 3. Khối Chú thích (Docstrings)
Mọi hàm, module bắt buộc phải có Docstring mô tả theo cấu trúc **Google Python Style Guide**:
```python
def cap_nhat_diem_danh(df, msv, tuan, trang_thai):
    """
    Cập nhật trạng thái điểm danh của một sinh viên trong một tuần học cụ thể.

    Args:
        df (pandas.DataFrame): Bảng dữ liệu điểm danh hiện tại.
        msv (str): Mã sinh viên cần cập nhật.
        tuan (str): Chuỗi định danh của tuần (Ví dụ: 't1', 't2').
        trang_thai (str): Trạng thái điểm danh (M/P/K).

    Returns:
        tuple: (DataFrame mới, bool True nếu thành công / False nếu thất bại)
    """
```

## 4. Hệ thống Vết (Logging)
Thay vì sử dụng `print()`, toàn bộ hành vi quan trọng phải sử dụng module `utils/logger.py`. Log sẽ được tự động xuất ra file `data/app.log`.
- `logger.debug()`: Dùng cho các vòng lặp, chi tiết xử lý nội bộ (Dev đọc).
- `logger.info()`: Dùng để ghi lại VẾT thao tác của user: *Thêm/Sửa/Xóa/Tìm kiếm*.
- `logger.warning()`: Dùng cho các lỗi logic nhỏ, cảnh báo tài nguyên.
- `logger.error()`: Bắt buộc dùng trong mọi block `try...except` để lưu chi tiết mã lỗi (Traceback) phục vụ debug/bảo hành.

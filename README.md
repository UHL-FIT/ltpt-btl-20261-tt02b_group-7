# Phần Mềm Quản Lý Chi Tiêu Cá Nhân (Personal Finance Manager)

## Giới thiệu chung
Dự án là một ứng dụng quản lý chi tiêu cá nhân trên máy tính được phát triển bằng Python với giao diện người dùng đồ họa (GUI) hiện đại sử dụng `customtkinter`. Hệ thống giúp người dùng dễ dàng theo dõi, kiểm soát và phân tích các khoản thu chi, quản lý ngân sách, cũng như lên kế hoạch tiết kiệm hiệu quả. Dự án được xây dựng theo mô hình **MVC (Model - View - Controller)** kết hợp với **Service Layer**, giúp tách biệt rõ ràng giữa giao diện, logic xử lý và cơ sở dữ liệu.

## Tính năng chính
- **Quản lý Giao dịch:** Thêm, sửa, xóa, nhân bản và tìm kiếm các giao dịch (thu/chi). Hỗ trợ lọc giao dịch nâng cao theo danh mục, loại và khoảng thời gian.
- **Thao tác hàng loạt:** Chọn nhiều giao dịch cùng lúc qua checkbox để xóa hoặc xuất dữ liệu nhanh chóng.
- **Thống kê & Báo cáo:** Hiển thị thẻ tổng quan thu chi, số dư ngay trên màn hình chính. Cung cấp Dashboard thống kê trực quan với biểu đồ (Pie Chart & Line Chart) để phân tích xu hướng chi tiêu bằng thư viện `matplotlib` và `pandas`.
- **Ngân sách & Tiết kiệm:** Thiết lập hạn mức chi tiêu hàng tháng, tự động cảnh báo khi chi tiêu vượt ngân sách và theo dõi tiến độ của các mục tiêu tiết kiệm.
- **Quản lý Danh mục:** Tùy biến linh hoạt danh mục thu chi (Thêm, sửa, xóa).
- **Import/Export:** Nhập dữ liệu giao dịch hàng loạt từ file CSV hoặc xuất dữ liệu ra file CSV để sao lưu và làm báo cáo.

## Công nghệ và Cấu trúc thư mục
- **Ngôn ngữ:** Python
- **Giao diện:** `customtkinter`
- **Cơ sở dữ liệu:** SQLite (`sqlite3` - tích hợp sẵn trong Python)
- **Xử lý & Phân tích Dữ liệu:** `pandas`
- **Biểu đồ trực quan:** `matplotlib`
- **Kiến trúc:** MVC + Service Layer

**Cấu trúc thư mục dự án:**
- `main.py`: Điểm khởi chạy ứng dụng (Entry Point). Khởi tạo cơ sở dữ liệu và liên kết các thành phần MVC.
- `models/database.py`: Chịu trách nhiệm quản lý kết nối và khởi tạo cấu trúc cơ sở dữ liệu SQLite (`data/finance.db`).
- `views/main_window.py`: Nơi thiết kế toàn bộ giao diện bằng `customtkinter` (Thanh công cụ, thẻ tổng quan, bảng dữ liệu) và quản lý các popup/cửa sổ phụ như bộ lọc, thống kê, ngân sách.
- `controllers/main_controller.py`: Lớp điều phối (Controller), nhận yêu cầu từ người dùng (View), xử lý đa luồng (nếu có) và gọi đến Service.
- `services/finance_service.py`: Lớp chứa toàn bộ logic xử lý dữ liệu, phân tích Pandas (tính trung bình, gom nhóm, xu hướng) và thực thi SQL CRUD.
- `data/`: Thư mục chứa file dữ liệu cục bộ `finance.db` (tự động tạo nếu chưa có).

## Hướng dẫn cài đặt và sử dụng

1. **Yêu cầu hệ thống:**
   - Máy tính cài đặt sẵn Python 3.8 trở lên.

2. **Cài đặt thư viện:**
   Mở terminal / command prompt tại thư mục dự án và cài đặt các thư viện cần thiết bằng lệnh:
   ```bash
   pip install customtkinter pandas matplotlib
   ```

3. **Chạy ứng dụng:**
   Khởi động phần mềm bằng cách chạy file chính:
   ```bash
   python main.py
   ```

4. **Phím tắt hỗ trợ trong ứng dụng:**
   - `Ctrl + N`: Mở form thêm giao dịch mới.
   - `Ctrl + F`: Đưa con trỏ chuột vào thanh tìm kiếm nhanh.
   - `Delete`: Xóa các giao dịch đã tick chọn trong bảng.
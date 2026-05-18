# Software Architecture Document (SAD) - SmartAttend

## 1. Giới thiệu
Tài liệu này cung cấp một cái nhìn tổng quan về kiến trúc phần mềm của ứng dụng SmartAttend. Nó phác thảo các quyết định kiến trúc, mô hình tổ chức source code và luồng dữ liệu của hệ thống.

---

## 2. Kiến trúc Tổng thể (Architectural Pattern)
SmartAttend được xây dựng hoàn toàn dựa trên kiến trúc **MVC (Model - View - Controller)** kết hợp với mô hình ứng dụng phân lớp đơn giản dành cho Desktop.
Điều này giúp tách biệt rõ ràng giữa logic dữ liệu, giao diện hiển thị và bộ điều phối:
* **Model**: Chịu trách nhiệm trực tiếp giao tiếp với Data Source (lưu trữ dưới dạng file **CSV**) và bắt buộc sử dụng thư viện **Numpy/Pandas** để xử lý tính toán số liệu nặng.
* **View**: Giao diện hiển thị với người dùng xây dựng bằng **Tkinter**. Ứng dụng bao gồm tối thiểu **03 windows** (01 Main window chứa bảng dữ liệu, tìm kiếm, các label thống kê, và 02 Sub windows dạng popup dùng để Thêm và Sửa thông tin). View hỗ trợ auto resize/align, tuỳ chỉnh màu sắc và icon.
* **Controller**: Viết bằng **Python cơ bản**, đóng vai trò điều phối. Nó nhận hành động từ View, thực hiện **Input validation** (kiểm tra rỗng, sai kiểu dữ liệu, chọn nhiều dòng - và hiển thị messagebox cảnh báo), gọi Model xử lý, sau đó trả kết quả về View để render lại UI.

---

## 3. Cấu trúc Source Code

```text
ltpt_example/
├── data/
│   └── diemdanh.csv            # Data Source: Lưu trữ dữ liệu dạng bảng.
├── models/
│   └── diemdanh.py             # Layer Model: Thực hiện các nghiệp vụ CRUD, dùng Vectorization để tính toán chuyên cần.
├── views/
│   ├── gui_view.py             # Layer View (Đồ hoạ): Sử dụng Tkinter cơ bản, Treeview hiển thị dữ liệu.
│   └── cli_view.py             # Layer View (Dòng lệnh): Sử dụng Colorama, In bảng dữ liệu ra terminal.
├── controllers/
│   ├── gui_controller.py       # Layer Controller (Cho GUI): Bắt sự kiện click chuột, gọi models và render lại UI.
│   └── cli_controller.py       # Layer Controller (Cho CLI): Phân tích lệnh arg, gọi models và in kết quả.
├── utils/
│   └── logger.py               # Utility: Hỗ trợ ghi log các hoạt động (Debug, Info, Error).
└── main.py                     # Entry Point: File khởi chạy ứng dụng. Cấu hình chọn chạy chế độ GUI hay CLI.
```

---

## 4. Công nghệ sử dụng
* **Ngôn ngữ lõi**: Python 3.9+
* **Xử lý Dữ liệu**: `pandas` (Quản lý dataframe, import/export csv) và `numpy` (Tính toán mảng lớn nhanh chóng, thay thế cho vòng lặp thông thường).
* **Giao diện (GUI)**: Thư viện chuẩn `tkinter` (Giao diện cơ bản, dễ hiểu, phù hợp cho sinh viên học tập). Sử dụng các widget cơ bản: button (kèm icon), edit text, label text, table (Treeview). Đảm bảo bố cục hài hoà và có khả năng auto resize.
* **Giao diện (CLI)**: Thư viện chuẩn `argparse` và thư viện `colorama` để in text có màu.
* **Đóng gói**: `pyinstaller` dùng để chuyển file Python script thành file thực thi `.exe` độc lập trên Windows.
* **Kiểm thử**: Sử dụng thư viện `unittest` tiêu chuẩn của Python.

---

## 5. Luồng dữ liệu (Data Flow) - Ví dụ: Sửa sinh viên
1. **View (gui_view.py)**: Người dùng chọn 1 hàng trong bảng, nhập thông tin mới và bấm "Cập nhật". Gửi thông tin (Mã cũ, Dữ liệu mới) đến Controller.
2. **Controller (gui_controller.py)**: Nhận yêu cầu, gọi hàm `models.diemdanh.sua_sinh_vien(df, old_msv, new_data)`.
3. **Model (diemdanh.py)**: Tìm vị trí (Index) sinh viên trong Pandas DataFrame. Kiểm tra điều kiện trùng mã SV. Nếu thoả mãn, tiến hành gán đè dữ liệu mới. Sau đó lưu lại file `diemdanh.csv`.
4. **Model -> Controller**: Trả về một Tuple (DataFrame_mới, Trạng_thái_Boolean, Thông_báo).
5. **Controller -> View**: Controller thông báo thành công. View sẽ nhận DataFrame mới, xoá toàn bộ hiển thị cũ, sau đó render lại bảng UI.

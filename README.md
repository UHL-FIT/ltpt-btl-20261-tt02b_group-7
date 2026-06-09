# 📊 Quản Lý Chi Tiêu Cá Nhân (Personal Finance Manager) - FINAL VERSION

Chào mừng bạn đến với ứng dụng **Quản Lý Chi Tiêu Cá Nhân (Bản Hoàn Thiện)**. 
Đây là một dự án ứng dụng Desktop chuyên nghiệp được xây dựng bằng Python, giao diện đồ họa **CustomTkinter** siêu hiện đại và cơ sở dữ liệu **SQLite** gọn nhẹ. 

Hệ thống được thiết kế theo tiêu chuẩn công nghiệp với kiến trúc **MVC (Model - View - Controller)** kết hợp **Service Layer**, phân tách cực kỳ khoa học giữa logic xử lý tính toán, luồng dữ liệu giao diện và lớp lưu trữ.

---

## 🌟 TÍNH NĂNG NỔI BẬT

- 💸 **Quản lý thu chi siêu tốc:** Thêm, Sửa, Xóa, Nhân bản giao dịch cực nhanh.
- 📈 **Bảng điều khiển (Dashboard) phân tích thông minh:** Trực quan hóa dữ liệu bằng các biểu đồ Pie Chart (cơ cấu) và Line Chart (xu hướng) thông qua thư viện Matplotlib.
- 🎯 **Quản lý Ngân sách & Tiết kiệm:** Theo dõi hạn mức chi tiêu mỗi tháng, cảnh báo vượt hạn mức (Vàng/Đỏ) và theo dõi tiến độ tích lũy cá nhân.
- 📂 **Xử lý CSV mạnh mẽ:** Hỗ trợ Import/Export file CSV với số lượng lớn (thử nghiệm trên 1000+ dòng). Cơ chế tự động dọn dẹp dữ liệu, tự động phân tích mọi định dạng ngày tháng mà không sợ lỗi nhờ sức mạnh của Pandas.
- 🎨 **Giao diện "Dark Mode" Premium:** Thiết kế tối màu hiện đại, sang trọng, hiệu ứng di chuột (hover) mượt mà, thông báo nổi (Toast Notification) thời thượng.

---

## 📁 CẤU TRÚC DỰ ÁN 

Dự án được phân rã thành các gói chuyên biệt để tối ưu hóa việc nâng cấp và bảo trì:

```text
finance_manager/
├── main.py                          # Entry point khởi chạy toàn bộ ứng dụng
├── generate_data.py                 # Kịch bản sinh ngẫu nhiên 1000 dòng dữ liệu mẫu
├── requirements.txt                 # Khai báo các thư viện phụ thuộc
├── README.md                        # Hướng dẫn tổng quan dự án
├── UPDATE.md                        # Chi tiết các bản cập nhật & vá lỗi so với bản cũ
├── SYS_MAP.md                       # Sơ đồ biểu diễn luồng MVC của hệ thống
│
├── data/finance.db                  # [MODEL] Cơ sở dữ liệu SQLite cục bộ
├── models/database.py               # [MODEL] Định nghĩa cấu trúc các bảng và khởi tạo DB
│
├── services/finance_service.py      # [SERVICE] Tầng nghiệp vụ: Tương tác SQL, xử lý Pandas, tính toán biểu đồ
│
├── controllers/main_controller.py   # [CONTROLLER] Điều phối viên xử lý tín hiệu và Multi-threading
│
└── views/                           # [VIEW] Tầng giao diện người dùng (Được chia nhỏ thành Module)
    ├── core/                        # Window gốc, Thanh điều hướng (Header), Theme Styles
    ├── dashboard/                   # Cửa sổ hiển thị biểu đồ Matplotlib, Ngân sách, Cảnh báo
    ├── transactions/                # Bảng lưới (Table), Form thêm/sửa, Dropdown lọc theo thời gian
    ├── categories/                  # Quản lý danh sách các hạng mục thu/chi
    └── common/                      # Thẻ thống kê (Cards), Thanh tải (Loading), Thông báo Toast
```

---

## 📚 TÀI LIỆU MỞ RỘNG
Vui lòng tham khảo các tệp tin đính kèm để hiểu rõ hơn về hệ thống:
1. **[UPDATE.md](UPDATE.md):** Đọc để biết ứng dụng đã cải tiến Engine xử lý Pandas và thay đổi góc nhìn (Default View) như thế nào.
2. **[SYS_MAP.md](SYS_MAP.md):** Đọc để xem Sơ đồ Kiến trúc Hệ thống chuẩn MVC của dự án này hoạt động ra sao.
3. **huong_dan_su_dung.pdf:** Cẩm nang cho người dùng cuối.

---

## 💻 HƯỚNG DẪN CÀI ĐẶT & CHẠY ỨNG DỤNG

### 1. Yêu cầu hệ thống:
Đảm bảo bạn đã cài đặt Python 3.9 trở lên.

### 2. Cài đặt môi trường ảo và thư viện:
Bật Terminal / Command Prompt và gõ lệnh:
```bash
python -m venv venv
.\venv\Scripts\activate      # Dành cho Windows
pip install -r requirements.txt
```

### 3. Tạo dữ liệu mẫu và Chạy App:
Bạn có thể tự sinh ra 1 file dữ liệu mẫu gồm 1000 dòng cực kỳ chân thực thông qua tệp đính kèm:
```bash
python generate_data.py
```
*(File sinh ra có tên `transactions_1000.csv`. Sau khi mở App, bạn có thể dùng nút "Nhập CSV" để nạp file này vào Data).*

Khởi chạy ứng dụng chính:
```bash
python main.py
```

### 💡 Mẹo sử dụng:
- Sử dụng phím tắt `Ctrl + N` để mở nhanh bảng thêm giao dịch.
- Quét chọn nhiều dòng trên lưới (hoặc ô Checkbox chọn tất cả) và bấm `<Delete>` để xoá nhanh.
- Nút "Xem theo" mặc định hiển thị "Tất cả" dữ liệu, bạn có thể click vào để chọn lọc theo từng tuần/tháng cụ thể.

---
**Tác giả:** Nguyễn Trung Hiếu
**Đề tài:** Quản Lý Chi Tiêu Cá Nhân Bằng Python & Tkinter

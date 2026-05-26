# 📊 TÀI LIỆU CẬP NHẬT PHIÊN BẢN (UPDATE.md)

---

## 🚀 1. CẢI TIẾN TRẢI NGHIỆM NGƯỜI DÙNG (UX/UI) CỐT LÕI

- **Thay đổi mặc định góc nhìn (Default View):** 
  - Trước đây, khi vừa khởi động ứng dụng, chế độ lọc thời gian tự động khóa ở "Hôm nay". Điều này dẫn đến sự bỡ ngỡ cho người dùng khi import dữ liệu cũ nhưng màn hình vẫn trống rỗng (do không có giao dịch nào phát sinh đúng vào hôm nay).
  - **Cập nhật:** Đã đổi mặc định hiển thị của cả Bảng giao dịch chính và Bảng Thống Kê (Dashboard) sang **"Tất cả"**. Người dùng có thể nhìn thấy toàn bộ dữ liệu ngay lập tức.
- **Nút "Đặt lại" linh hoạt:** Chức năng reset bộ lọc cũng tự động đưa mốc thời gian về "Tất cả" thay vì gò bó vào "Hôm nay".

## 🛠️ 2. NÂNG CẤP ENGINE XỬ LÝ FILE CSV (Bằng Pandas)

Xử lý triệt để lỗi "Import báo thành công nhưng không có dữ liệu" xảy ra khi làm việc với file CSV có định dạng phức tạp:
- **Tự động gỡ lỗi BOM (Byte Order Mark):** Hỗ trợ chuẩn mã hóa `utf-8-sig` giúp xử lý gọn gàng các file CSV xuất ra từ Microsoft Excel mà không bị dính ký tự lạ ẩn ở tiêu đề cột.
- **Dọn dẹp khoảng trắng & dòng trống:** Tự động loại bỏ các dòng trống (`dropna(how='all')`) và các khoảng trắng thừa ở tên cột.
- **Phân tích ngày tháng siêu thông minh (`format='mixed'`):** Xóa bỏ ràng buộc `dayfirst=True` gây sai lệch việc parse ngày tháng. Thay vào đó, áp dụng cơ chế tự nhận diện thông minh của Pandas 2.0+ giúp ứng dụng đọc trơn tru cả dữ liệu chuẩn quốc tế (`YYYY-MM-DD`) lẫn dữ liệu chuẩn VN (`DD/MM/YYYY`) mà không sinh ra lỗi `NaT`.
- **Tẩy rửa chuỗi số học:** Xóa bỏ nhanh chóng dấu phẩy phân cách hàng nghìn (ví dụ `1,000,000` -> `1000000`) bằng Regex trước khi ghi vào Database.

## 🛡️ 3. TĂNG CƯỜNG TÍNH ỔN ĐỊNH VÀ BÁO LỖI (ERROR HANDLING)

- **Bắt lỗi dữ liệu rỗng:** Tránh tình trạng import một file CSV toàn chuỗi khoảng trắng hoặc rỗng ruột nhưng vẫn báo "Thành công". Giờ đây, ứng dụng sẽ `raise ValueError("File CSV không chứa dữ liệu hợp lệ")` và thông báo Toast Error lên màn hình thay vì im lặng.
- **Bảo vệ luồng (Thread-Safety):** Đảm bảo các callbacks bắt lỗi từ tiến trình nền (background threads) trả về giao diện đồ họa (main UI thread) một cách an toàn thông qua hàm `.after()` của Tkinter.
- **Tái cấu trúc thư mục:** Dọn dẹp sạch sẽ các tệp lệnh thử nghiệm dư thừa (scripts test) để mã nguồn phiên bản Final giữ được sự gọn gàng và nguyên bản.

---
*Phiên bản Final Version tự hào mang lại một hệ thống quản lý chi tiêu ổn định, chống chịu mọi rủi ro nhập liệu và vận hành cực kỳ trơn tru!*

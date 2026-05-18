# Software Requirements Specification (SRS) - SmartAttend

## 1. Giới thiệu
### 1.1 Mục đích
Tài liệu này đặc tả các yêu cầu chức năng và phi chức năng cho hệ thống **SmartAttend** - phần mềm hỗ trợ giảng viên trong việc quản lý sinh viên và theo dõi điểm danh chuyên cần tự động.

### 1.2 Phạm vi hệ thống
Hệ thống nhắm tới việc thay thế sổ điểm danh giấy/Excel truyền thống, cung cấp giao diện trực quan và tính toán tự động các thông số như tổng vắng, điểm chuyên cần, cảnh báo cấm thi.

---

## 2. Mô tả Tổng quan
### 2.1 Đặc điểm Người dùng (Actors)
* **Giảng viên / Người dùng**: Người trực tiếp sử dụng phần mềm để quản lý các lớp học của mình. Có toàn quyền (Thêm, sửa, xoá, điểm danh, xuất báo cáo).

### 2.2 Môi trường Hoạt động
* Chạy trên hệ điều hành Windows 10/11 (Có cung cấp sẵn file `.exe`).
* Không yêu cầu kết nối Internet (Ứng dụng Desktop chạy Offline hoàn toàn).

---

## 3. Yêu cầu Chức năng (Functional Requirements)

### FR1: Quản lý Sinh viên & Giao diện (GUI)
* **FR1.1 Cấu trúc Giao diện (Ít nhất 3 Windows)**:
  * **01 Main window**: Chứa các button chức năng (Thêm, sửa, xóa thông tin; import csv, export csv; about - hiển thị phiên bản, tác giả, ngày phát hành). Cửa sổ này hiển thị 01 bảng dữ liệu, có chức năng tìm kiếm dữ liệu, và các label text thống kê (sĩ số, giới tính, giá trị trung bình điểm, các ghi chú,...).
  * **02 Sub windows**: Gồm 01 window popup chuyên dụng để thêm thông tin, và 01 window popup chuyên dụng để sửa thông tin.
* **FR1.2 Thêm, Sửa sinh viên**: Thao tác cập nhật thông tin thông qua các Sub windows. Mã SV phải là duy nhất.
* **FR1.3 Xóa sinh viên**: Cho phép xóa một hoặc nhiều sinh viên cùng lúc khỏi danh sách trên Main window.
* **FR1.4 Tìm kiếm & Lọc**: Có thể tìm kiếm theo nhiều tiêu chí thông qua thanh công cụ trên Main window.

### FR2: Tính năng Điểm danh & Chuyên cần
* **FR2.1 Điểm danh theo tuần**: Hệ thống hỗ trợ tối đa 15 tuần học. Trạng thái gồm `M` (Có mặt), `P` (Vắng có phép), `K` (Vắng không phép).
* **FR2.2 Tự động tính chuyên cần**:
  * Điểm chuyên cần mặc định là 10.
  * Mỗi buổi vắng không phép (K) trừ 2 điểm.
  * Cộng điểm khi hoàn thành bài tập (0.5 điểm / lần).
  * Trừ điểm khi vi phạm (-1 điểm / lần).
* **FR2.3 Cảnh báo cấm thi tự động**:
  * Nếu tổng số buổi vắng (Cả có phép và không phép) > 3 buổi: Sinh viên bị **Cấm thi** và điểm chuyên cần bị đưa về 0.
  * Nếu tổng số buổi vắng = 3 buổi: Cảnh báo **Cẩn thận cấm thi**.

### FR3: Import / Export Dữ liệu
* **FR3.1 Nhập file CSV**: Nhập danh sách sinh viên hàng loạt từ file Excel (CSV) theo template cung cấp sẵn.
* **FR3.2 Xuất file CSV**: Xuất dữ liệu đã tính toán ra file CSV để báo cáo.

### FR4: Bảng điều khiển (Dashboard)
* **FR4.1 Thống kê**: Hiển thị tổng số sinh viên, tỷ lệ Nam/Nữ, số sinh viên bị cấm thi, và điểm chuyên cần trung bình.

---

## 4. Yêu cầu Phi chức năng (Non-Functional Requirements)

### NFR1: Kiến trúc & Công nghệ (Architecture)
* Áp dụng kiến trúc **MVC**:
  * **Model**: Lưu trữ dữ liệu dạng file **CSV**. **Bắt buộc** sử dụng thư viện `numpy` và `pandas` để tính toán và truy vấn dữ liệu.
  * **View**: Giao diện thiết kế bằng **Tkinter** với các widget cơ bản (button, Edit text, label text, Table). Yêu cầu có thay đổi màu sắc và thêm icon cho button để tăng tính thẩm mỹ.
  * **Controller**: Python cơ bản dùng để điều phối luồng xử lý giữa View và Model.

### NFR2: Trải nghiệm Người dùng (UI/UX)
* Sắp xếp các Widget (button, table) với vị trí hài hoà, hợp lý, tiện sử dụng.
* Các phần đồ họa của Windows (bảng, frame) có thể **auto resize/align** khi tăng/giảm kích thước cửa sổ.

### NFR3: Kiểm tra tính hợp lệ của Dữ liệu (Input Validation)
* Bắt buộc kiểm tra dữ liệu người dùng nhập vào và hiển thị các **messagebox** cảnh báo/thông báo hợp lý nhằm tránh lỗi ứng dụng.
* Các trường hợp điển hình cần xử lý:
  * Các trường dữ liệu bị trống -> Đưa ra thông báo: "Mời bạn nhập dữ liệu...".
  * Sai kiểu dữ liệu (ví dụ: tuổi nhập bằng chữ) -> Đưa ra thông báo: "Mời bạn nhập lại số tuổi...".
  * Nếu chọn nhiều hơn 1 dòng dữ liệu trên bảng để thực hiện chức năng "Sửa" -> Thông báo cho người dùng là chỉ được chọn 1 dòng.

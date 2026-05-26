import os
import logging
from logging.handlers import RotatingFileHandler
import sys

# ==========================================
# Tên file: logger.py (nằm trong thư mục utils)
# Danh sách lớp và chức năng OOP:
# Lớp: LineRotatingFileHandler
# - Chức năng: Bộ xử lý ghi log tùy chỉnh tự động dọn dẹp hoặc xoay vòng file log dựa trên số lượng dòng ghi nhận (line count) thay vì kích thước file (byte size).
# Khái niệm OOP sử dụng:
# - Tính kế thừa (Inheritance): Lớp LineRotatingFileHandler kế thừa trực tiếp từ RotatingFileHandler của thư viện chuẩn logging, tận dụng toàn bộ cơ sở hạ tầng ghi log mạnh mẽ có sẵn.
# - Tính đa hình và ghi đè phương thức (Polymorphism & Method Overriding): Ghi đè các phương thức shouldRollover, doRollover, và emit để tùy biến hành vi kiểm tra và thực thi xoay vòng log theo số lượng dòng thay vì dung lượng byte.
# - Ủy nhiệm phương thức lớp cha (Super class delegation): Sử dụng super().__init__() để gọi và thiết lập các tham số cơ sở cho lớp cha một cách nhất quán.
# ==========================================


class LineRotatingFileHandler(RotatingFileHandler):
    """
    Trình xử lý nhật ký tùy chỉnh (Handler) giúp luân chuyển (rotate) hoặc xóa tệp log
    khi tệp đạt đến một số lượng dòng ghi nhận nhất định.
    Nếu backupCount = 0, tệp log hiện tại sẽ bị xóa hoàn toàn để bắt đầu ghi lại từ đầu.
    """
    def __init__(self, filename, max_lines=1000, *args, **kwargs):
        self.max_lines = max_lines
        self.line_count = 0
        # Thiết lập maxBytes = 0 để vô hiệu hóa cơ chế luân chuyển theo dung lượng file mặc định của lớp cha
        super().__init__(filename, maxBytes=0, *args, **kwargs)
        self._init_line_count()

    def _init_line_count(self):
        """
        Đếm số dòng thực tế trong tệp tin log để khôi phục số lượng dòng hiện tại khi khởi động ứng dụng.
        """
        try:
            if os.path.exists(self.baseFilename):
                with open(self.baseFilename, 'r', encoding='utf-8', errors='replace') as f:
                    self.line_count = sum(1 for _ in f)
            else:
                self.line_count = 0
        except Exception:
            self.line_count = 0

    def doRollover(self):
        """
        Thực hiện luân chuyển (hoặc xóa/làm trống) tệp tin log cũ khi đạt giới hạn dòng.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        
        # Nếu muốn giữ lại các file log cũ đã luân chuyển (backupCount > 0)
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = self.rotation_filename("%s.%d" % (self.baseFilename, i))
                dfn = self.rotation_filename("%s.%d" % (self.baseFilename, i + 1))
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.rotation_filename(self.baseFilename + ".1")
            if os.path.exists(dfn):
                os.remove(dfn)
            self.rotate(self.baseFilename, dfn)
        else:
            # Xóa hoặc làm rỗng tệp log hiện tại nếu backupCount bằng 0 (chỉ giữ lại tệp log mới)
            try:
                if os.path.exists(self.baseFilename):
                    os.remove(self.baseFilename)
            except Exception:
                try:
                    with open(self.baseFilename, 'w', encoding='utf-8') as f:
                        f.truncate(0)
                except Exception:
                    pass
        
        if not self.delay:
            self.stream = self._open()
        # Đặt lại số dòng đã ghi trong bộ nhớ về 0 sau khi hoàn thành luân chuyển/xóa
        self.line_count = 0

    def shouldRollover(self, record):
        """
        Kiểm tra xem bản ghi log chuẩn bị ghi có làm số dòng vượt quá mức tối đa (max_lines) hay không.
        """
        if self.stream is None:
            self.stream = self._open()
            self._init_line_count()
        
        # Lấy định dạng hoàn chỉnh của dòng log chuẩn bị ghi
        msg = self.format(record)
        # Đếm số dòng mà thông điệp log mới sẽ chiếm dụng (thường là 1 dòng, ngoại trừ lỗi traceback)
        msg_lines = msg.count('\n') + 1
        
        # Kích hoạt luân chuyển nếu tổng số dòng hiện tại và dòng mới vượt quá max_lines
        if self.line_count + msg_lines > self.max_lines:
            return 1
        return 0

    def emit(self, record):
        """
        Thực hiện ghi bản ghi log vào tệp tin và tự động xử lý luân chuyển/xóa nếu cần thiết.
        """
        try:
            if self.shouldRollover(record):
                self.doRollover()
            msg = self.format(record)
            msg_lines = msg.count('\n') + 1
            # Cộng thêm số dòng mới ghi nhận vào bộ đếm dòng
            self.line_count += msg_lines
            logging.FileHandler.emit(self, record)
        except Exception:
            self.handleError(record)

def setup_logger():
    # Cấu hình encoding cho terminal để hiển thị tiếng Việt và tránh lỗi UnicodeEncodeError trên Windows
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        try:
            sys.stdout.reconfigure(errors='replace')
            sys.stderr.reconfigure(errors='replace')
        except Exception:
            pass

    # Thư mục logs nằm trong thư mục gốc của project
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    error_log_path = os.path.join(log_dir, 'error.log')
    app_log_path = os.path.join(log_dir, 'app.log')
    
    logger = logging.getLogger('FinanceManager')
    logger.setLevel(logging.DEBUG)
    
    # Tránh nhân đôi handler nếu gọi hàm nhiều lần
    if logger.hasHandlers():
        logger.handlers.clear()
        
    # Console Formatter chỉ chứa prefix loại log để dễ đọc
    console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
    
    # File Formatter chi tiết chứa mốc thời gian, file, function, line để phục vụ debug sâu
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s'
    )
    
    # 1. Console Handler (In các thông báo từ mức INFO trở lên ra console)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 2. Error File Handler (Ghi nhận toàn bộ lỗi mức ERROR và CRITICAL vào logs/error.log)
    error_handler = RotatingFileHandler(error_log_path, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)
    
    # 3. App File Handler (Ghi lại toàn bộ hoạt động từ mức DEBUG trở lên vào logs/app.log, tự động xóa sau mỗi 1000 dòng)
    app_handler = LineRotatingFileHandler(app_log_path, max_lines=1000, backupCount=0, encoding='utf-8')
    app_handler.setLevel(logging.DEBUG)
    app_handler.setFormatter(file_formatter)
    logger.addHandler(app_handler)
    
    return logger

# Tạo một instance logger dùng chung cho toàn hệ thống
logger = setup_logger()


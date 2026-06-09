# Nhập các thư viện cần thiết
import functools
from utils.logger import logger

# ==========================================
# Tên file: ui_decorators.py (nằm trong thư mục views/core)
# Chức năng: Cung cấp bộ trang trí (decorator) safe_execution hỗ trợ xử lý ngoại lệ tập trung và an toàn cho các phương thức View, và các helper tiện ích cho UI.
# Khái niệm OOP sử dụng:
# - Lập trình hướng khía cạnh & Decorator (Aspect-Oriented Programming & Method Decorators): Tách biệt khía cạnh phụ trợ (ghi log lỗi, bắt ngoại lệ hệ thống) ra khỏi logic giao diện chính, giúp mã nguồn sạch sẽ và tuân thủ DRY.
# - Tính phản xạ đối tượng (Object Reflection): Sử dụng getattr() và kiểm tra thuộc tính động trên đối tượng gọi (args[0] - chính là đối tượng self của phương thức được bọc) như getattr(self, 'show_error') để tự động tìm kiếm và kích hoạt phương thức thông báo lỗi tương thích trên View mà không cần liên kết cứng (decoupled).
# ==========================================


# Bộ trang trí (decorator) giúp thực thi hàm một cách an toàn và tránh sập ứng dụng
def safe_execution(error_message_prefix="Đã xảy ra lỗi", show_toast=True):
    """
    Decorator bọc các hàm callback của view, tự động bắt mọi ngoại lệ,
    ghi lại nhật ký kèm chi tiết traceback và hiển thị thông báo Toast lỗi
    mà không làm sập luồng xử lý của ứng dụng chính.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Trích xuất thông tin tên module và tên hàm
                func_name = f"{func.__module__}.{func.__name__}"
                
                # Ghi chi tiết stack trace lỗi vào tệp log
                logger.error(f"Lỗi xảy ra tại {func_name}: {str(e)}", exc_info=True)
                
                # Hiển thị thông báo lỗi Toast một cách an toàn nếu tìm thấy hàm show_error
                if show_toast and args:
                    caller_self = args[0]
                    show_error_func = getattr(caller_self, 'show_error', None)
                    if not show_error_func and hasattr(caller_self, 'master'):
                        show_error_func = getattr(caller_self.master, 'show_error', None)
                    if not show_error_func and hasattr(caller_self, 'view'):
                        show_error_func = getattr(caller_self.view, 'show_error', None)
                        
                    if show_error_func:
                        try:
                            show_error_func("Lỗi hệ thống", f"{error_message_prefix}: {str(e)}")
                        except Exception:
                            pass
                    else:
                        # In lỗi ra console nếu không tìm thấy hàm hiển thị giao diện toast
                        print(f"[ERROR] {error_message_prefix}: {str(e)}")
            return None
        return wrapper
    return decorator


def format_entry_amount(entry, event=None):
    """
    Tự động định dạng số tiền trong CTkEntry (thêm dấu phẩy phân tách hàng nghìn).
    Hỗ trợ cả phần thập phân, số âm và duy trì vị trí con trỏ chuột chính xác.
    """
    if event and event.keysym in ('Left', 'Right', 'Up', 'Down', 'Home', 'End'):
        return
        
    val = entry.get()
    # Loại bỏ các dấu phẩy cũ để chuẩn bị định dạng lại
    content = val.replace(',', '')
    if not content:
        return
        
    try:
        if '.' in content:
            parts = content.split('.')
            clean_int = "".join([c for c in parts[0] if c.isdigit()])
            if clean_int:
                int_part = f"{int(clean_int):,}"
            else:
                int_part = ""
            
            # Chỉ lấy các số cho phần thập phân
            clean_dec = "".join([c for c in parts[1] if c.isdigit()])
            formatted = int_part + '.' + clean_dec
        else:
            clean_int = "".join([c for c in content if c.isdigit()])
            if clean_int:
                formatted = f"{int(clean_int):,}"
            else:
                formatted = ""
                
        idx = entry.index("insert")
        old_len = len(val)
        
        entry.delete(0, 'end')
        entry.insert(0, formatted)
        
        new_len = len(formatted)
        new_idx = idx + (new_len - old_len)
        entry.icursor(new_idx)
    except ValueError:
        pass


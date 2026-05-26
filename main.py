import sys
import os
from utils.logger import logger

# Add parent directory to path so that we can import modules properly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ==========================================
# Tên file: main.py
# Chức năng: Điểm khởi chạy ứng dụng (Entry Point).
# Khái niệm OOP sử dụng:
# - Giao tiếp giữa các đối tượng (Object Collaboration): Đóng vai trò là Client Code khởi tạo và liên kết các đối tượng như database, MainWindow (View) và MainController (Controller) hoạt động cùng nhau theo mô hình MVC.
# ==========================================


try:
    from models.database import initialize_db
    from views.core.main_window import MainWindow
    from controllers.main_controller import MainController
except Exception as e:
    logger.error("Lỗi import các module hệ thống!", exc_info=True)
    sys.exit(1)

def main():
    logger.info("=========================================")
    logger.info("Khởi chạy ứng dụng Quản Lý Chi Tiêu Cá Nhân...")
    logger.info("=========================================")
    
    try:
        # Khởi tạo DB
        logger.info("Đang khởi tạo cơ sở dữ liệu...")
        initialize_db()
        logger.info("Khởi tạo cơ sở dữ liệu thành công.")
    except Exception as e:
        logger.error(f"Khởi tạo cơ sở dữ liệu thất bại: {str(e)}", exc_info=True)
        print(f"[FATAL] Khởi tạo cơ sở dữ liệu thất bại: {str(e)}")
        sys.exit(1)
        
    try:
        # Khởi tạo MVC
        logger.info("Đang khởi tạo các thành phần giao diện MVC...")
        view = MainWindow()
        controller = MainController(view)
        view.set_controller(controller)
        logger.info("Khởi tạo MVC hoàn tất.")
    except Exception as e:
        logger.error(f"Khởi tạo giao diện MVC thất bại: {str(e)}", exc_info=True)
        print(f"[FATAL] Khởi tạo giao diện MVC thất bại: {str(e)}")
        sys.exit(1)
        
    # Chạy ứng dụng
    try:
        logger.info("Bắt đầu chạy mainloop của ứng dụng...")
        view.mainloop()
        logger.info("Ứng dụng kết thúc bình thường.")
    except Exception as e:
        logger.error(f"Ứng dụng gặp sự cố trong quá trình chạy mainloop: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()


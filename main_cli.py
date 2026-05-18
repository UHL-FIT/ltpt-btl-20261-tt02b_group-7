"""
main_cli.py
===========
Khởi chạy ứng dụng "SmartAttend" ở chế độ dòng lệnh (CLI).
Dùng cho việc đóng gói (build) thành file thực thi riêng biệt (SmartAttend_CLI.exe).
"""

from controllers import cli_controller
import sys
from utils.logger import setup_logger

__version__ = "1.0.0"
logger = setup_logger("main_cli")

# Ép console sử dụng UTF-8 khi chạy file .exe để tránh lỗi UnicodeEncodeError
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

if __name__ == "__main__":
    logger.info(f"=== Khởi chạy SmartAttend v{__version__} (Chế độ Console Độc lập) ===")
    cli_controller.chay_ung_dung()

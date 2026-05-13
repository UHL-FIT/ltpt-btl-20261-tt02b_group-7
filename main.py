import sys
import os

# Add parent directory to path so that we can import modules properly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import initialize_db
from views.main_window import MainWindow
from controllers.main_controller import MainController

def main():
    # Khởi tạo DB
    initialize_db()
    
    # Khởi tạo MVC
    view = MainWindow()
    controller = MainController(view)
    view.set_controller(controller)
    
    # Chạy ứng dụng
    view.mainloop()

if __name__ == "__main__":
    main()

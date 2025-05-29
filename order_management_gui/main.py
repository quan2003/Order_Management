import sys
from gui import OrderManagementApp
from database import create_default_admin
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    # Gọi create_default_admin() trước khi khởi chạy ứng dụng
    print("Bắt đầu tạo tài khoản admin mặc định...")
    create_default_admin()
    print("Kết thúc tạo tài khoản admin mặc định.")

    app = QApplication(sys.argv)
    window = OrderManagementApp()
    sys.exit(app.exec())

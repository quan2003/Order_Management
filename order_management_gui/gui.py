import sys
import datetime
import random
import string
import bcrypt
import unicodedata
import pandas as pd
import json
import os
from dotenv import load_dotenv
from models import ActivityLog
import time
from PyQt6.QtGui import (
    QPixmap,
    QFont,
    QIcon,
    QPalette,
    QColor,
    QIntValidator,
    QRegularExpressionValidator,  # Nhập QRegularExpressionValidator từ QtGui
)
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QLabel,
    QMessageBox,
    QTabWidget,
    QDialog,
    QFormLayout,
    QComboBox,
    QFrame,
    QSizePolicy,
    QHeaderView,
    QFileDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal, QRegularExpression, QLocale
from PyQt6.QtWebEngineWidgets import QWebEngineView
from database import get_session
from models import User, Product, Order, OrderItem, Role, OrderStatus
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from collections import defaultdict
from nominatim_autocomplete_dialog import NominatimAutocompleteDialog
import calendar

# Định nghĩa stylesheet cho giao diện
STYLESHEET = """
QMainWindow {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #f8f9fc, stop: 1 #e9ecef);
}

QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #2c3e50;
}

QLabel {
    font-size: 14px;
    color: #2c3e50;
    font-weight: 500;
}

QLabel#titleLabel {
    font-size: 28px;
    font-weight: bold;
    color: #1a73e8;
    padding: 20px;
    border-radius: 10px;
    margin: 10px;
}

QLabel#userInfoLabel {
    font-size: 14px;
    font-weight: bold;
    color: white;
    padding: 8px 15px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 15px;
    margin-right: 10px;
}

QLineEdit {
    padding: 12px 15px;
    border: 2px solid #e1e5e9;
    border-radius: 8px;
    background-color: #ffffff;
    font-size: 14px;
    color: #495057;
    selection-background-color: #007bff;
}

QLineEdit:focus {
    border: 2px solid #1a73e8;
    background-color: #f8f9ff;
    outline: none;
}

QLineEdit:hover {
    border: 2px solid #4285f4;
}

QLineEdit#user_search_input, QLineEdit#product_search_input, QLineEdit#order_search_input, QLineEdit#customer_order_search_input {
    padding: 8px 12px;
    border: 2px solid #e1e5e9;
    border-radius: 8px;
    background-color: #ffffff;
    font-size: 13px;
}

QPushButton {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #4285f4, stop: 1 #1a73e8);
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    min-width: 100px;
}

QPushButton:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #5a95f5, stop: 1 #2b7de9);
}

QPushButton:pressed {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #3367d6, stop: 1 #1557b0);
}

QPushButton#logoutButton {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #dc3545, stop: 1 #c82333);
}

QPushButton#logoutButton:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #e4606d, stop: 1 #d32535);
}

QPushButton#addButton {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #28a745, stop: 1 #1e7e34);
}

QPushButton#addButton:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #34ce57, stop: 1 #218838);
}

QPushButton#editButton {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #ffc107, stop: 1 #e0a800);
    color: #212529;
}

QPushButton#editButton:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #ffcd39, stop: 1 #d39e00);
}

QPushButton#deleteButton {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #dc3545, stop: 1 #c82333);
}

QPushButton#deleteButton:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #e4606d, stop: 1 #d32535);
}

QTableWidget {
    border: 1px solid #dee2e6;
    background-color: #ffffff;
    font-size: 13px;
    gridline-color: #e9ecef;
    selection-background-color: #e3f2fd;
    alternate-background-color: #f8f9fa;
    border-radius: 8px;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #e9ecef;
}

QTableWidget::item:selected {
    background-color: #1a73e8;
    color: white;
}

QTableWidget::item:hover {
    background-color: #f1f3f4;
}

QHeaderView::section {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #f8f9fa, stop: 1 #e9ecef);
    padding: 10px;
    border: 1px solid #dee2e6;
    font-weight: bold;
    color: #495057;
    font-size: 13px;
}

QTabWidget::pane {
    border: 1px solid #dee2e6;
    background: #ffffff;
    border-radius: 8px;
    margin-top: 5px;
}

QTabBar::tab {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #f8f9fa, stop: 1 #e9ecef);
    padding: 12px 24px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    color: #6c757d;
    font-weight: 500;
    min-width: 120px;
}

QTabBar::tab:selected {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #1a73e8, stop: 1 #1557b0);
    color: white;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #e2e6ea, stop: 1 #dae0e5);
}

QTabWidget#statsSubTabs::pane {
    border: 1px solid #dee2e6;
    background: #ffffff;
    border-radius: 8px;
    margin-top: 5px;
}

QTabWidget#statsSubTabs QTabBar::tab {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #f8f9fa, stop: 1 #e9ecef);
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    color: #6c757d;
    font-weight: 500;
    min-width: 100px;
}

QTabWidget#statsSubTabs QTabBar::tab:selected {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #1a73e8, stop: 1 #1557b0);
    color: white;
    font-weight: bold;
}

QTabWidget#statsSubTabs QTabBar::tab:hover:!selected {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #e2e6ea, stop: 1 #dae0e5);
}

QComboBox {
    padding: 10px 15px;
    border: 2px solid #e1e5e9;
    border-radius: 8px;
    background-color: #ffffff;
    font-size: 14px;
    min-width: 150px;
    color: #000000;
}

QComboBox:hover {
    border: 2px solid #4285f4;
}

QComboBox:focus {
    border: 2px solid #1a73e8;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #000000;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #000000;
    selection-background-color: #1a73e8;
    selection-color: #000000;
}

QComboBox#user_role_filter, QComboBox#user_status_filter, 
QComboBox#product_category_filter, QComboBox#product_status_filter, 
QComboBox#order_status_filter, QComboBox#customer_order_status_filter {
    padding: 8px 12px;
    border: 2px solid #e1e5e9;
    border-radius: 8px;
    background-color: #ffffff;
    font-size: 13px;
    min-width: 120px;
}

QDialog {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #ffffff, stop: 1 #f8f9fa);
    border-radius: 10px;
}

QFrame#buttonFrame {
    background: rgba(248, 249, 250, 0.8);
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 10px;
    margin: 5px;
}

QFrame#headerFrame {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #667eea, stop: 1 #764ba2);
    border-bottom: 3px solid #1a73e8;
}
"""
# Tải biến môi trường từ file .env
load_dotenv()


# Hàm gửi email thông báo qua SendGrid
def send_email_notification(to_email, subject, content):
    import sendgrid
    from sendgrid.helpers.mail import Mail

    # Thông tin SendGrid
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    FROM_EMAIL = os.getenv("FROM_EMAIL")

    if not to_email:
        print("Không có email để gửi thông báo.")
        return

    sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
    message = Mail(
        from_email=FROM_EMAIL, to_emails=to_email, subject=subject, html_content=content
    )

    try:
        response = sg.send(message)
        print(f"Đã gửi email đến {to_email}. Mã trạng thái: {response.status_code}")
    except Exception as e:
        print(f"Lỗi khi gửi email: {str(e)}")
        QMessageBox.warning(None, "Lỗi", f"Lỗi khi gửi email: {str(e)}")


# Hàm định dạng giá dùng chung
def format_price(price):
    """Định dạng giá: Thêm dấu phân cách và VNĐ."""
    try:
        price_float = float(price)
        locale = QLocale("vi_VN")
        formatted_price = locale.toString(price_float, "f", 0)
        return f"{formatted_price} VNĐ"
    except ValueError:
        return "0 VNĐ"


# Hàm lấy dữ liệu thống kê doanh thu theo danh mục
def get_revenue_by_category(session, staff_id=None):
    # Lấy tất cả danh mục từ bảng Product
    all_categories = session.query(Product.category).distinct().all()
    all_categories = [
        cat[0] for cat in all_categories if cat[0]
    ]  # Lấy danh sách danh mục

    # Truy vấn doanh thu theo danh mục
    query = (
        session.query(
            Product.category, func.sum(OrderItem.quantity * OrderItem.unit_price)
        )
        .join(OrderItem, Product.id == OrderItem.product_id)
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.status == OrderStatus.completed)
    )
    if staff_id is not None:
        query = query.filter(Order.staff_id == staff_id)
    results = query.group_by(Product.category).all()

    # Tạo từ điển doanh thu theo danh mục
    revenue_dict = {r[0]: float(r[1]) / 1000 for r in results if r[0]}

    # Đảm bảo tất cả danh mục đều có mặt, gán 0 nếu không có doanh thu
    categories = all_categories
    revenues = [revenue_dict.get(cat, 0.0) for cat in categories]

    return categories, revenues


def get_revenue_by_month(session, staff_id=None):
    query = session.query(
        func.to_char(Order.created_at, "YYYY-MM"), func.sum(Order.total_amount)
    ).filter(Order.status == OrderStatus.completed)
    if staff_id is not None:
        query = query.filter(Order.staff_id == staff_id)
    results = (
        query.group_by(func.to_char(Order.created_at, "YYYY-MM"))
        .order_by(func.to_char(Order.created_at, "YYYY-MM"))
        .all()
    )
    months = [r[0] for r in results]
    revenues = [float(r[1]) / 1000 for r in results]
    return months, revenues


def get_order_status_distribution(session, staff_id=None):
    query = session.query(Order.status, func.count(Order.id))
    if staff_id is not None:
        query = query.filter(Order.staff_id == staff_id)
    results = query.group_by(Order.status).all()
    statuses = [r[0].value for r in results]
    counts = [r[1] for r in results]
    return statuses, counts


# Hàm xuất dữ liệu ra file Excel
def export_to_excel(data, filename, sheet_name):
    df = pd.DataFrame(data)
    df.to_excel(filename, sheet_name=sheet_name, index=False)
    return filename


from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QHBoxLayout,
)
from PyQt6.QtCore import QRegularExpression, Qt
from PyQt6.QtGui import QRegularExpressionValidator
from nominatim_autocomplete_dialog import NominatimAutocompleteDialog


class RegisterDialog(QDialog):
    def __init__(self, parent=None, session=None):
        super().__init__(parent)
        self.session = session  # Lưu session để truy cập database
        self.setWindowTitle("📝 Đăng ký tài khoản")
        self.setFixedSize(450, 600)

        self.layout = QFormLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 25, 20, 25)

        title = QLabel("Tạo tài khoản mới")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #1a73e8; margin-bottom: 20px;"
        )
        self.layout.addRow(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập tên đăng nhập")
        username_validator = QRegularExpressionValidator(
            QRegularExpression(r"^[a-zA-Z0-9_-]{3,20}$")
        )
        self.username_input.setValidator(username_validator)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Nhập mật khẩu")
        password_validator = QRegularExpressionValidator(
            QRegularExpression(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$")
        )
        self.password_input.setValidator(password_validator)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("Nhập lại mật khẩu")
        self.confirm_password_input.setValidator(password_validator)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Nhập email")
        email_validator = QRegularExpressionValidator(
            QRegularExpression(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        )
        self.email_input.setValidator(email_validator)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nhập họ tên")
        # Bỏ validator phức tạp để tránh lỗi
        # Chỉ kiểm tra độ dài và ký tự hợp lệ trong accept()

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Nhập số điện thoại")
        phone_validator = QRegularExpressionValidator(
            QRegularExpression(r"^(0|\+84)\d{9,10}$")
        )
        self.phone_input.setValidator(phone_validator)

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Nhập địa chỉ")
        address_validator = QRegularExpressionValidator(
            QRegularExpression(r"^[a-zA-Z0-9\s,.-]+$")
        )
        self.address_input.setValidator(address_validator)

        self.address_button = QPushButton("🌍")
        self.address_button.setToolTip("Chọn địa chỉ từ danh sách gợi ý")
        self.address_button.setFixedSize(30, 30)
        self.address_button.clicked.connect(self.open_address_autocomplete)
        self.address_button.setStyleSheet(
            """
            QPushButton {
                background: #e0e7ff;
                border: 1px solid #93c5fd;
                border-radius: 4px;
                padding: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #c7d2fe;
            }
            QPushButton:pressed {
                background: #a5b4fc;
            }
            """
        )

        self.register_button = QPushButton("🎯 Đăng ký")
        self.register_button.setObjectName("addButton")
        self.register_button.clicked.connect(self.accept)

        self.login_button = QPushButton("🔙 Quay lại đăng nhập")
        self.login_button.clicked.connect(self.reject)

        self.layout.addRow("👤 Tên đăng nhập:", self.username_input)
        self.layout.addRow("🔒 Mật khẩu:", self.password_input)
        self.layout.addRow("🔑 Xác nhận mật khẩu:", self.confirm_password_input)
        self.layout.addRow("📧 Email:", self.email_input)
        self.layout.addRow("🏷️ Họ tên:", self.name_input)
        self.layout.addRow("📱 Số điện thoại:", self.phone_input)

        address_layout = QHBoxLayout()
        address_layout.addWidget(self.address_input)
        address_layout.addWidget(self.address_button)
        self.layout.addRow("🏠 Địa chỉ:", address_layout)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.login_button)
        self.layout.addRow(button_layout)

        self.setLayout(self.layout)

    def accept(self):
        import re

        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        email = self.email_input.text().strip()
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        address = self.address_input.text().strip()

        # Validation cho tên đăng nhập
        if not username:
            QMessageBox.warning(self, "Lỗi", "Tên đăng nhập không được để trống!")
            return
        if not re.match(r"^[a-zA-Z0-9_-]{3,20}$", username):
            QMessageBox.warning(
                self,
                "Lỗi",
                "Tên đăng nhập phải từ 3-20 ký tự, chỉ chứa chữ cái, số, gạch dưới hoặc gạch nối!",
            )
            return
        if self.session.query(User).filter_by(username=username).first():
            QMessageBox.warning(self, "Lỗi", "Tên đăng nhập đã tồn tại!")
            return

        # Validation cho mật khẩu
        if not password:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu không được để trống!")
            return
        if not re.match(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$", password
        ):
            QMessageBox.warning(
                self,
                "Lỗi",
                "Mật khẩu phải từ 8 ký tự, chứa ít nhất 1 chữ hoa, 1 chữ thường và 1 số!",
            )
            return
        if password != confirm_password:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp!")
            return

        # Validation cho email
        if not email:
            QMessageBox.warning(self, "Lỗi", "Email không được để trống!")
            return
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            QMessageBox.warning(self, "Lỗi", "Email không hợp lệ!")
            return
        if self.session.query(User).filter_by(email=email).first():
            QMessageBox.warning(self, "Lỗi", "Email đã được sử dụng!")
            return

        # Validation cho họ tên (kiểm tra thủ công)
        if not name:
            QMessageBox.warning(self, "Lỗi", "Họ tên không được để trống!")
            return
        # Kiểm tra độ dài
        if len(name) < 2 or len(name) > 50:
            QMessageBox.warning(
                self,
                "Lỗi",
                "Họ tên phải từ 2-50 ký tự!",
            )
            return
        # Kiểm tra ký tự hợp lệ (chỉ chứa chữ cái, khoảng trắng, dấu gạch ngang)
        if not all(char.isalpha() or char.isspace() or char == "-" for char in name):
            QMessageBox.warning(
                self,
                "Lỗi",
                "Họ tên chỉ được chứa chữ cái, khoảng trắng hoặc dấu gạch ngang!",
            )
            return

        # Validation cho số điện thoại (nếu có)
        if phone and not re.match(r"^(0|\+84)\d{9,10}$", phone):
            QMessageBox.warning(
                self,
                "Lỗi",
                "Số điện thoại không hợp lệ! Vui lòng nhập số Việt Nam hợp lệ (10-11 số).",
            )
            return

        # Validation cho địa chỉ (nếu có)
        if address and len(address) < 5:
            QMessageBox.warning(self, "Lỗi", "Địa chỉ phải có ít nhất 5 ký tự!")
            return

        # Nếu tất cả validation đều qua, gọi accept() của lớp cha để đóng form
        super().accept()

    def open_address_autocomplete(self):
        dialog = NominatimAutocompleteDialog(self)
        dialog.address_selected.connect(self.address_input.setText)
        dialog.exec()


class LoginDialog(QDialog):
    register_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔐 Đăng nhập hệ thống")
        self.setFixedSize(400, 300)

        self.layout = QFormLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(40, 25, 40, 25)

        title = QLabel("Đăng nhập")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #1a73e8; margin-bottom: 30px;"
        )
        self.layout.addRow(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập tên đăng nhập")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Nhập mật khẩu")

        self.login_button = QPushButton("🚀 Đăng nhập")
        self.login_button.clicked.connect(self.accept)

        self.register_button = QPushButton("📝 Đăng ký")
        self.register_button.setObjectName("addButton")
        self.register_button.clicked.connect(self.request_registration_and_close)

        self.layout.addRow("👤 Tên đăng nhập:", self.username_input)
        self.layout.addRow("🔒 Mật khẩu:", self.password_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        self.layout.addRow(button_layout)

        self.setLayout(self.layout)

    def request_registration_and_close(self):
        self.register_requested.emit()
        self.reject()


class OrderTrackingMapDialog(QDialog):
    def __init__(self, order, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🗺️ Theo dõi đơn hàng")
        self.setFixedSize(600, 500)
        self.order = order
        self.session = parent.session
        self.current_user = parent.current_user

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        self.map_view = QWebEngineView()
        self.map_view.setFixedHeight(450)
        layout.addWidget(self.map_view)

        close_button = QPushButton("Đóng")
        close_button.setObjectName("addButton")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)
        self.load_map()

    def load_map(self):
        try:
            with open("map_template.html", "r", encoding="utf-8") as f:
                html_content = f.read()
        except FileNotFoundError as e:
            QMessageBox.critical(
                self, "Lỗi", f"Không tìm thấy tệp map_template.html: {str(e)}"
            )
            return

        # Lấy staff_id từ đơn hàng
        staff_id = self.order.staff_id
        if not staff_id:
            QMessageBox.critical(
                self, "Lỗi", f"Đơn hàng {self.order.code} không có staff_id."
            )
            return

        staff = self.session.query(User).get(staff_id)
        if not staff or not staff.address:
            QMessageBox.critical(
                self, "Lỗi", f"Nhân viên (staff_id: {staff_id}) không có địa chỉ."
            )
            return

        # Gọi Nominatim API để lấy tọa độ từ địa chỉ của staff
        import requests
        import time

        nominatim_url = f"https://nominatim.openstreetmap.org/search?q={staff.address}&format=json&limit=1"
        headers = {"User-Agent": "OrderManagementApp/1.0 (luuquan232003@gmail.com)"}
        response = requests.get(nominatim_url, headers=headers).json()
        time.sleep(1)  # Tuân thủ giới hạn 1 yêu cầu/giây
        if not response or len(response) == 0:
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không thể lấy tọa độ cho địa chỉ của nhân viên: {staff.address}",
            )
            return

        warehouse_lat = float(response[0]["lat"])
        warehouse_lng = float(response[0]["lon"])

        # Tọa độ khách hàng
        if not self.order.latitude or not self.order.longitude:
            customer = self.session.query(User).get(self.order.customer_id)
            QMessageBox.critical(
                self,
                "Lỗi",
                f"Không có tọa độ giao hàng cho khách hàng {customer.name}.",
            )
            return

        customer_lat = self.order.latitude
        customer_lng = self.order.longitude
        status = self.order.status.value

        self.map_view.setHtml(html_content)

        def on_load_finished(ok):
            if ok:
                self.map_view.page().runJavaScript(
                    f"showRoute({warehouse_lat}, {warehouse_lng}, {customer_lat}, {customer_lng}, '{status}');",
                    lambda result: print("Kết quả showRoute:", result),
                )
                # Ghi log hành động xem bản đồ
                log = ActivityLog(
                    user_id=self.current_user.id,
                    action="view_order_map",
                    target=f"Order {self.order.code}",
                    details=f"Viewed map for order status {status}",
                )
                self.session.add(log)
                self.session.commit()
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể tải bản đồ.")

        self.map_view.loadFinished.connect(on_load_finished)


class UserDialog(QDialog):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.setWindowTitle("👥 Quản lý người dùng")
        self.setFixedSize(500, 600)
        self.layout = QFormLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 25, 20, 25)
        self.user = user

        title_text = "Thêm người dùng mới" if not user else "Chỉnh sửa thông tin"
        title = QLabel(title_text)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1a73e8; margin-bottom: 20px;"
        )
        self.layout.addRow(title)

        self.username_input = QLineEdit(user.username if user else "")
        self.username_input.setPlaceholderText("Nhập tên đăng nhập")
        self.password_input = QLineEdit("")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_placeholder = (
            "Để trống nếu không thay đổi" if user else "Nhập mật khẩu"
        )
        self.password_input.setPlaceholderText(password_placeholder)

        self.email_input = QLineEdit(user.email if user else "")
        self.email_input.setPlaceholderText("Nhập email")
        self.name_input = QLineEdit(user.name if user else "")
        self.name_input.setPlaceholderText("Nhập họ tên")
        self.phone_input = QLineEdit(user.phone if user else "")
        self.phone_input.setPlaceholderText("Nhập số điện thoại")
        self.address_input = QLineEdit(user.address if user else "")
        self.address_input.setPlaceholderText("Nhập địa chỉ")

        # Nút tự động hoàn thành địa chỉ
        self.address_button = QPushButton("🌍")
        self.address_button.setToolTip("Chọn địa chỉ từ danh sách gợi ý")
        self.address_button.setFixedSize(30, 30)
        self.address_button.clicked.connect(self.open_address_autocomplete)
        self.address_button.setStyleSheet(
            """
            QPushButton {
                background: #e0e7ff;
                border: 1px solid #93c5fd;
                border-radius: 4px;
                padding: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #c7d2fe;
            }
            QPushButton:pressed {
                background: #a5b4fc;
            }
        """
        )

        self.role_input = QComboBox()
        self.role_input.addItems([r.value for r in Role])
        if user and user.role:
            self.role_input.setCurrentText(user.role.value)

        self.status_input = QComboBox()
        self.status_input.addItems(["Hoạt động", "Không hoạt động"])
        if user:
            self.status_input.setCurrentText(
                "Hoạt động" if user.status == "active" else "Không hoạt động"
            )

        self.save_button = QPushButton("💾 Lưu thông tin")
        self.save_button.setObjectName("addButton")
        self.save_button.clicked.connect(self.accept)

        self.layout.addRow("👤 Tên đăng nhập:", self.username_input)
        self.layout.addRow("🔒 Mật khẩu:", self.password_input)
        self.layout.addRow("📧 Email:", self.email_input)
        self.layout.addRow("🏷️ Họ tên:", self.name_input)
        self.layout.addRow("📱 Số điện thoại:", self.phone_input)

        # Trường địa chỉ với nút tự động hoàn thành
        address_layout = QHBoxLayout()
        address_layout.addWidget(self.address_input)
        address_layout.addWidget(self.address_button)
        self.layout.addRow("🏠 Địa chỉ:", address_layout)

        self.layout.addRow("👔 Vai trò:", self.role_input)
        self.layout.addRow("📊 Trạng thái:", self.status_input)
        self.layout.addWidget(self.save_button)
        self.setLayout(self.layout)

    def open_address_autocomplete(self):
        dialog = NominatimAutocompleteDialog(self)
        dialog.address_selected.connect(self.address_input.setText)
        dialog.exec()


class ProductDialog(QDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.setWindowTitle("📦 Quản lý sản phẩm")
        self.setFixedSize(500, 600)
        self.layout = QFormLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 25, 20, 25)
        self.product = product

        title_text = "Thêm sản phẩm mới" if not product else "Chỉnh sửa sản phẩm"
        title = QLabel(title_text)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1a73e8; margin-bottom: 20px;"
        )
        self.layout.addRow(title)

        self.name_input = QLineEdit(product.name if product else "")
        self.name_input.setPlaceholderText("Nhập tên sản phẩm (VD: Áo thun)")
        self.name_input.textChanged.connect(self.generate_product_code)

        self.code_input = QLineEdit(product.code if product else "")
        self.code_input.setReadOnly(True)
        self.code_input.setPlaceholderText("Mã sẽ tự động tạo")

        self.category_input = QComboBox()
        self.category_input.addItems(["Áo", "Quần", "Giày", "Phụ kiện"])
        if product and product.category:
            self.category_input.setCurrentText(product.category)

        self.price_input = QLineEdit()
        if product and product.price is not None:
            self.price_input.setText(format_price(product.price))
        self.price_input.setPlaceholderText("Nhập giá (VD: 150000)")
        self.price_input.editingFinished.connect(self.format_price_input)

        self.stock_input = QLineEdit(str(product.stock) if product else "")
        self.stock_input.setPlaceholderText("Nhập số lượng tồn kho (VD: 50)")

        self.description_input = QLineEdit(product.description if product else "")
        self.description_input.setPlaceholderText(
            "Nhập mô tả sản phẩm (VD: Áo thun cotton)"
        )

        self.image_input = QLineEdit(product.image if product else "")
        self.image_input.setReadOnly(True)
        self.image_input.setPlaceholderText("Chọn hình ảnh sản phẩm")

        self.image_button = QPushButton()
        self.image_button.setText("⬆️")
        self.image_button.setToolTip("Tải lên hình ảnh sản phẩm")
        self.image_button.setFixedSize(30, 30)
        self.image_button.clicked.connect(self.upload_image)
        self.image_button.setStyleSheet(
            """
            QPushButton {
                background: #e0e7ff;
                border: 1px solid #93c5fd;
                border-radius: 4px;
                padding: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #c7d2fe;
            }
            QPushButton:pressed {
                background: #a5b4fc;
            }
        """
        )

        self.status_input = QComboBox()
        self.status_input.addItems(["Hoạt động", "Không hoạt động"])
        if product:
            self.status_input.setCurrentText(
                "Hoạt động" if product.status == "active" else "Không hoạt động"
            )

        self.save_button = QPushButton("💾 Lưu sản phẩm")
        self.save_button.setObjectName("addButton")
        self.save_button.clicked.connect(self.accept)

        self.layout.addRow("🏷️ Tên sản phẩm:", self.name_input)
        self.layout.addRow("🔖 Mã sản phẩm:", self.code_input)
        self.layout.addRow("📂 Danh mục:", self.category_input)
        self.layout.addRow("💰 Giá (VNĐ):", self.price_input)
        self.layout.addRow("📊 Tồn kho:", self.stock_input)
        self.layout.addRow("📝 Mô tả:", self.description_input)

        image_layout = QHBoxLayout()
        image_layout.addWidget(self.image_input)
        image_layout.addWidget(self.image_button)
        self.layout.addRow("🖼️ Hình ảnh:", image_layout)

        self.layout.addRow("📊 Trạng thái:", self.status_input)
        self.layout.addWidget(self.save_button)
        self.setLayout(self.layout)

    def format_price_input(self):
        text = self.price_input.text().strip()
        if text:
            try:
                price = self.get_raw_price()
                if price < 0:
                    QMessageBox.warning(self, "Lỗi", "Giá không được âm!")
                    self.price_input.setText("0 VNĐ")
                    return
                formatted = format_price(price)
                self.price_input.setText(formatted)
            except ValueError:
                QMessageBox.warning(
                    self, "Lỗi", "Vui lòng nhập giá hợp lệ (chỉ nhập số)!"
                )
                self.price_input.setText("0 VNĐ")
        else:
            self.price_input.setText("0 VNĐ")

    def get_raw_price(self):
        text = self.price_input.text().strip()
        if text:
            # Loại bỏ "VNĐ" và các ký tự không phải số ngoại trừ dấu chấm
            clean_text = text.replace(" VNĐ", "").replace(".", "")
            if clean_text:
                return float(clean_text)
            raise ValueError("Giá trị không hợp lệ")
        return 0.0

    def generate_product_code(self):
        name = self.name_input.text().strip()
        if name:
            name_without_diacritics = self.remove_diacritics(name)
            prefix = name_without_diacritics[:2].upper()
            random_suffix = "".join(random.choices(string.digits, k=4))
            generated_code = f"{prefix}-{random_suffix}"
            self.code_input.setText(generated_code)
        else:
            self.code_input.setText("")

    def remove_diacritics(self, text):
        normalized = unicodedata.normalize("NFD", text)
        without_diacritics = "".join(
            c for c in normalized if unicodedata.category(c) != "Mn"
        )
        return unicodedata.normalize("NFC", without_diacritics)

    def upload_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Chọn hình ảnh sản phẩm", "", "Hình ảnh (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_name:
            self.image_input.setText(file_name)


class UserProfileDialog(QDialog):
    def __init__(self, parent=None, user=None, session=None):
        super().__init__(parent)
        self.setWindowTitle("👤 Thông tin tài khoản")
        self.setFixedSize(500, 600)
        self.user = user
        self.session = session

        self.layout = QFormLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 25, 20, 25)

        title = QLabel("Thông tin tài khoản")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1a73e8; margin-bottom: 20px;"
        )
        self.layout.addRow(title)

        # Các trường thông tin người dùng
        self.username_input = QLineEdit(user.username if user else "")
        self.username_input.setReadOnly(True)
        self.email_input = QLineEdit(user.email if user else "")
        self.email_input.setPlaceholderText("Nhập email")
        self.name_input = QLineEdit(user.name if user else "")
        self.name_input.setPlaceholderText("Nhập họ tên")
        self.phone_input = QLineEdit(user.phone if user else "")
        self.phone_input.setPlaceholderText("Nhập số điện thoại")
        self.address_input = QLineEdit(user.address if user else "")
        self.address_input.setPlaceholderText("Nhập địa chỉ")

        # Nút tự động hoàn thành địa chỉ
        self.address_button = QPushButton("🌍")
        self.address_button.setToolTip("Chọn địa chỉ từ danh sách gợi ý")
        self.address_button.setFixedSize(30, 30)
        self.address_button.clicked.connect(self.open_address_autocomplete)
        self.address_button.setStyleSheet(
            """
            QPushButton {
                background: #e0e7ff;
                border: 1px solid #93c5fd;
                border-radius: 4px;
                padding: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #c7d2fe;
            }
            QPushButton:pressed {
                background: #a5b4fc;
            }
        """
        )

        # Các trường đổi mật khẩu
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setPlaceholderText("Nhập mật khẩu mới")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("Xác nhận mật khẩu mới")

        # Nút lưu thông tin
        self.save_button = QPushButton("💾 Lưu thông tin")
        self.save_button.setObjectName("addButton")
        self.save_button.clicked.connect(self.save_changes)

        self.layout.addRow("👤 Tên đăng nhập:", self.username_input)
        self.layout.addRow("📧 Email:", self.email_input)
        self.layout.addRow("🏷️ Họ tên:", self.name_input)
        self.layout.addRow("📱 Số điện thoại:", self.phone_input)

        # Trường địa chỉ với nút tự động hoàn thành
        address_layout = QHBoxLayout()
        address_layout.addWidget(self.address_input)
        address_layout.addWidget(self.address_button)
        self.layout.addRow("🏠 Địa chỉ:", address_layout)

        self.layout.addRow("🔒 Mật khẩu mới:", self.new_password_input)
        self.layout.addRow("🔑 Xác nhận mật khẩu:", self.confirm_password_input)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def save_changes(self):
        # Cập nhật thông tin người dùng
        self.user.email = self.email_input.text()
        self.user.name = self.name_input.text()
        self.user.phone = self.phone_input.text()
        self.user.address = self.address_input.text()

        # Kiểm tra và cập nhật mật khẩu nếu có
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if new_password or confirm_password:
            if new_password != confirm_password:
                QMessageBox.warning(self, "❌ Lỗi", "Mật khẩu xác nhận không khớp!")
                return
            if not new_password:
                QMessageBox.warning(self, "❌ Lỗi", "Mật khẩu mới không được để trống!")
                return
            hashed_password = bcrypt.hashpw(
                new_password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            self.user.password = hashed_password

        try:
            self.session.commit()
            QMessageBox.information(
                self, "✅ Thành công", "Cập nhật thông tin thành công!"
            )
            self.accept()
        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(self, "Lỗi cập nhật thông tin", str(e))

    def open_address_autocomplete(self):
        dialog = NominatimAutocompleteDialog(self)
        dialog.address_selected.connect(self.address_input.setText)
        dialog.exec()


class ImageViewerDialog(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🖼️ Xem hình ảnh")
        self.setFixedSize(400, 400)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Hiển thị hình ảnh lớn
        self.image_label = QLabel()
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(
                380, 380, Qt.AspectRatioMode.KeepAspectRatio
            )
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("Không tìm thấy hình ảnh")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.image_label)

        # Nút đóng
        close_button = QPushButton("Đóng")
        close_button.setObjectName("addButton")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)


class OrderCreationDialog(QDialog):
    def __init__(self, parent=None, session=None):
        super().__init__(parent)
        self.setWindowTitle("🛒 Tạo đơn hàng mới")
        self.setFixedSize(600, 650)  # Tăng chiều cao để giao diện thoáng hơn
        self.session = session
        self.current_user = (
            parent.current_user
        )  # Lấy current_user từ parent (OrderManagementApp)
        self.products = self.session.query(Product).filter_by(status="active").all()
        self.best_seller = self.get_best_seller()

        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 25, 20, 25)

        # Tiêu đề
        title = QLabel("Tạo đơn hàng mới")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1a73e8; margin-bottom: 20px;"
        )
        self.layout.addWidget(title)

        # Form layout cho các trường nhập liệu
        form_layout = QHBoxLayout()

        # Cột bên trái: Chọn danh mục và sản phẩm
        left_layout = QVBoxLayout()

        # Chọn danh mục
        self.category_input = QComboBox()
        self.category_input.addItem("Tất cả danh mục")
        categories = sorted(set(p.category for p in self.products if p.category))
        self.category_input.addItems(categories)
        self.category_input.currentIndexChanged.connect(
            self.filter_products_by_category
        )
        left_layout.addWidget(QLabel("📂 Danh mục:"))
        left_layout.addWidget(self.category_input)

        # Chọn sản phẩm
        self.product_input = QComboBox()
        self.product_input.addItem("Chọn sản phẩm...")
        self.update_product_list()
        self.product_input.currentIndexChanged.connect(self.update_price_info)
        self.product_input.currentIndexChanged.connect(self.update_image_display)
        left_layout.addWidget(QLabel("📦 Sản phẩm:"))
        left_layout.addWidget(self.product_input)

        # Số lượng
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Nhập số lượng (VD: 1)")
        self.quantity_input.setValidator(QIntValidator(1, 9999))
        self.quantity_input.textChanged.connect(self.update_price_info)
        left_layout.addWidget(QLabel("🔢 Số lượng:"))
        left_layout.addWidget(self.quantity_input)

        form_layout.addLayout(left_layout)

        # Cột bên phải: Hiển thị hình ảnh và thông tin giá
        right_layout = QVBoxLayout()

        # Hiển thị hình ảnh
        self.image_label = QLabel()
        self.image_label.setFixedSize(150, 150)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid #e1e5e9; border-radius: 8px;")
        self.image_label.setText("Chưa có hình ảnh")
        right_layout.addWidget(QLabel("🖼️ Hình ảnh:"))
        right_layout.addWidget(self.image_label)

        # Thêm khoảng cách để đẩy phần giá xuống dưới
        right_layout.addSpacing(30)

        # Giá và tổng tiền
        self.price_label = QLabel("Giá đơn vị: 0 VNĐ")
        self.price_label.setStyleSheet("font-size: 14px; color: #2c3e50;")
        right_layout.addWidget(QLabel("💰 Giá:"))
        right_layout.addWidget(self.price_label)

        self.total_label = QLabel("Tổng tiền: 0 VNĐ")
        self.total_label.setStyleSheet("font-size: 14px; color: #2c3e50;")
        right_layout.addWidget(QLabel("📊 Tổng tiền:"))
        right_layout.addWidget(self.total_label)

        form_layout.addLayout(right_layout)
        self.layout.addLayout(form_layout)

        # Gợi ý sản phẩm
        self.suggestion_label = QLabel("📈 Gợi ý sản phẩm:")
        self.suggestion_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #1a73e8;"
        )
        self.layout.addWidget(self.suggestion_label)

        self.suggestion_text = QLabel("Chưa có gợi ý")
        self.suggestion_text.setStyleSheet("font-size: 13px; color: #2c3e50;")
        self.update_suggestion()
        self.layout.addWidget(self.suggestion_text)

        # Thông tin nhân viên bán nhiều nhất
        top_seller_layout = QHBoxLayout()
        top_seller_label = QLabel("🏆 Nhân viên bán nhiều nhất:")
        top_seller_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #1a73e8;"
        )
        top_seller_layout.addWidget(top_seller_label)

        if self.best_seller:
            top_seller_info = QLabel(
                f"{self.best_seller.name} - {self.best_seller.order_count} đơn hàng, phục vụ {self.best_seller.customer_count} khách hàng"
            )
        else:
            top_seller_info = QLabel("Chưa có dữ liệu")
        top_seller_info.setStyleSheet("font-size: 13px; color: #2c3e50;")
        top_seller_layout.addWidget(top_seller_info)
        top_seller_layout.addStretch()
        self.layout.addLayout(top_seller_layout)

        # Nút điều khiển
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("💾 Tạo đơn hàng")
        self.save_button.setObjectName("addButton")
        self.save_button.clicked.connect(self.accept)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("🔙 Hủy")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

    def get_top_seller(self):
        # Lấy thông tin của staff hiện tại (self.current_user)
        if not self.current_user or self.current_user.role != Role.staff:
            return None

        result = (
            self.session.query(
                User,
                func.count(Order.id).label("order_count"),
                func.count(func.distinct(Order.customer_id)).label("customer_count"),
            )
            .join(
                Order, Order.staff_id == User.id, isouter=True
            )  # Dùng outer join để lấy cả staff chưa có đơn hàng
            .filter(User.id == self.current_user.id, User.role == Role.staff)
            .group_by(User.id)
            .first()
        )

        if result:
            user, order_count, customer_count = result
            return type(
                "Seller",
                (),
                {
                    "name": user.name,
                    "order_count": order_count or 0,  # Nếu không có đơn hàng, trả về 0
                    "customer_count": customer_count
                    or 0,  # Nếu không có khách hàng, trả về 0
                },
            )
        return None

    def get_best_seller(self):
        result = (
            self.session.query(
                User,
                func.count(Order.id).label("order_count"),
                func.count(func.distinct(Order.customer_id)).label("customer_count"),
            )
            .join(Order, Order.staff_id == User.id, isouter=True)
            .filter(User.role == Role.staff, Order.status == OrderStatus.completed)
            .group_by(User.id)
            .order_by(func.count(Order.id).desc())
            .first()
        )

        if result:
            user, order_count, customer_count = result
            return type(
                "Seller",
                (),
                {
                    "id": user.id,
                    "name": user.name,
                    "order_count": order_count or 0,
                    "customer_count": customer_count or 0,
                },
            )
        return None

    def filter_products_by_category(self):
        selected_category = self.category_input.currentText()
        self.update_product_list(selected_category)
        self.update_suggestion()

    def update_product_list(self, category_filter=None):
        self.product_input.clear()
        self.product_input.addItem("Chọn sản phẩm...")
        filtered_products = self.products
        if category_filter and category_filter != "Tất cả danh mục":
            filtered_products = [
                p for p in self.products if p.category == category_filter
            ]
        for product in filtered_products:
            self.product_input.addItem(
                f"{product.name} (Mã: {product.code}, Tồn kho: {product.stock})",
                product.id,
            )

    def update_suggestion(self):
        selected_category = self.category_input.currentText()
        if selected_category == "Tất cả danh mục":
            product_sales = {}
            for product in self.products:
                total_sold = (
                    self.session.query(func.sum(OrderItem.quantity))
                    .filter(OrderItem.product_id == product.id)
                    .filter(OrderItem.order_id == Order.id)
                    .filter(Order.status == "completed")
                    .scalar()
                    or 0
                )
                product_sales[product] = total_sold
            if product_sales:
                top_product = max(product_sales.items(), key=lambda x: x[1])[0]
                self.suggestion_text.setText(
                    f"Sản phẩm bán chạy: {top_product.name} (Đã bán: {product_sales[top_product]} sản phẩm)"
                )
            else:
                self.suggestion_text.setText("Chưa có dữ liệu bán hàng")
        else:
            filtered_products = [
                p for p in self.products if p.category == selected_category
            ]
            if not filtered_products:
                self.suggestion_text.setText("Không có sản phẩm trong danh mục này")
                return
            product_sales = {}
            for product in filtered_products:
                total_sold = (
                    self.session.query(func.sum(OrderItem.quantity))
                    .filter(OrderItem.product_id == product.id)
                    .filter(OrderItem.order_id == Order.id)
                    .filter(Order.status == "completed")
                    .scalar()
                    or 0
                )
                product_sales[product] = total_sold
            if product_sales:
                top_product = max(product_sales.items(), key=lambda x: x[1])[0]
                self.suggestion_text.setText(
                    f"Sản phẩm bán chạy trong danh mục {selected_category}: {top_product.name} (Đã bán: {product_sales[top_product]} sản phẩm)"
                )
            else:
                self.suggestion_text.setText(
                    f"Chưa có dữ liệu bán hàng trong danh mục {selected_category}"
                )

    def update_image_display(self):
        product_id = self.product_input.currentData()
        if not product_id:
            self.image_label.setText("Chưa có hình ảnh")
            return

        product = next((p for p in self.products if p.id == product_id), None)
        if product and product.image and os.path.exists(product.image):
            pixmap = QPixmap(product.image).scaled(
                150, 150, Qt.AspectRatioMode.KeepAspectRatio
            )
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("Không có hình ảnh")

    def update_price_info(self):
        product_id = self.product_input.currentData()
        quantity_text = self.quantity_input.text()

        if not product_id or not quantity_text:
            self.price_label.setText("Giá đơn vị: 0 VNĐ")
            self.total_label.setText("Tổng tiền: 0 VNĐ")
            return

        try:
            quantity = int(quantity_text)
            product = next((p for p in self.products if p.id == product_id), None)
            if product:
                if product.price is None:
                    self.price_label.setText("Giá đơn vị: Không xác định")
                    self.total_label.setText("Tổng tiền: Không xác định")
                    return
                price = product.price
                self.price_label.setText(f"Giá đơn vị: {format_price(price)}")
                total = price * quantity
                self.total_label.setText(f"Tổng tiền: {format_price(total)}")
        except ValueError:
            self.price_label.setText("Giá đơn vị: 0 VNĐ")
            self.total_label.setText("Tổng tiền: 0 VNĐ")

    def validate_input(self):
        product_id = self.product_input.currentData()
        quantity_text = self.quantity_input.text()

        print(
            f"Xác thực - ID sản phẩm: {product_id}, Số lượng nhập: {quantity_text}"
        )  # Log

        if not product_id:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một sản phẩm!")
            return False

        try:
            quantity = int(quantity_text)
            print(f"Xác thực - Số lượng: {quantity}")  # Log
            if quantity <= 0:
                QMessageBox.warning(self, "Lỗi", "Số lượng phải lớn hơn 0!")
                return False
        except ValueError as e:
            print(f"Xác thực - Lỗi số lượng: {str(e)}")  # Log
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập số lượng hợp lệ!")
            return False

        product = next((p for p in self.products if p.id == product_id), None)
        if not product:
            print(f"Xác thực - Không tìm thấy sản phẩm với ID: {product_id}")  # Log
            QMessageBox.warning(self, "Lỗi", "Sản phẩm không tồn tại!")
            return False

        print(
            f"Xác thực - Sản phẩm: {product.name}, Tồn kho: {product.stock}, Giá: {product.price}, Người tạo: {product.created_by}"
        )  # Log

        if product.stock < quantity:
            QMessageBox.warning(
                self,
                "Lỗi",
                f"Sản phẩm {product.name} chỉ còn {product.stock} trong kho!",
            )
            return False

        if product.price is None:
            QMessageBox.warning(self, "Lỗi", f"Sản phẩm {product.name} không có giá!")
            return False

        # Kiểm tra xem sản phẩm có nhân viên tạo không
        if not product.created_by:
            print(f"Xác thực - Sản phẩm {product.name} không có người tạo!")  # Log
            QMessageBox.warning(
                self, "Lỗi", f"Sản phẩm {product.name} không có nhân viên tạo!"
            )
            return False

        # Kiểm tra xem nhân viên có vai trò staff không
        staff = self.session.query(User).get(product.created_by)
        if not staff or staff.role != Role.staff:
            print(
                f"Xác thực - Nhân viên không hợp lệ cho sản phẩm {product.name}, ID Nhân viên: {product.created_by}, Vai trò: {staff.role if staff else 'Không có'}"
            )  # Log
            QMessageBox.warning(
                self, "Lỗi", f"Nhân viên tạo sản phẩm {product.name} không hợp lệ!"
            )
            return False

        return True

    def get_selected_product(self):
        product_id = self.product_input.currentData()
        return next((p for p in self.products if p.id == product_id), None)

    def get_quantity(self):
        try:
            return int(self.quantity_input.text())
        except ValueError:
            return 0


class SelectCustomerDialog(QDialog):
    def __init__(self, parent=None, session=None):
        super().__init__(parent)
        self.setWindowTitle("👤 Chọn khách hàng")
        self.setFixedSize(400, 300)
        self.session = session
        self.customers = self.session.query(User).filter_by(role=Role.customer).all()

        self.layout = QFormLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 25, 20, 25)

        title = QLabel("Chọn khách hàng để tạo đơn hàng")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1a73e8; margin-bottom: 20px;"
        )
        self.layout.addRow(title)

        self.customer_input = QComboBox()
        self.customer_input.addItem("Chọn khách hàng...")
        if not self.customers:
            self.customer_input.setEnabled(False)
            self.customer_input.addItem("Không có khách hàng")
        else:
            for customer in self.customers:
                status = (
                    " (Hoạt động)"
                    if customer.status == "active"
                    else " (Không hoạt động)"
                )
                self.customer_input.addItem(
                    f"{customer.name} ({customer.username}){status}", customer.id
                )
        self.layout.addRow("👤 Khách hàng:", self.customer_input)

        self.select_button = QPushButton("✅ Chọn")
        self.select_button.setObjectName("addButton")
        self.select_button.clicked.connect(self.accept)
        if not self.customers:
            self.select_button.setEnabled(False)

        self.cancel_button = QPushButton("🔙 Hủy")
        self.cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addRow(button_layout)

        self.setLayout(self.layout)

    def get_selected_customer_id(self):
        return self.customer_input.currentData()


class OrderManagementApp(QMainWindow):
    _instance_count = 0

    def __init__(self):
        super().__init__()
        OrderManagementApp._instance_count += 1
        self.setWindowTitle("🏪 Hệ thống Quản lý Đơn hàng")
        self.session = get_session()
        self.current_user = None
        self.setStyleSheet(STYLESHEET)

        self.login_dialog_instance = None
        self.register_dialog_instance = None
        self._navigating_to_register = False

        self.setup_login_screen()

    def clear_current_central_widget(self):
        current_cw = self.centralWidget()
        if current_cw:
            current_cw.deleteLater()

    def setup_login_screen(self):
        self.clear_current_central_widget()
        self.reset_ui_components()

        login_screen_widget = QWidget()
        login_screen_layout = QVBoxLayout(login_screen_widget)
        login_screen_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_screen_layout.setContentsMargins(20, 50, 20, 50)

        app_title_label = QLabel("🏪 HỆ THỐNG QUẢN LÝ ĐƠN HÀNG")
        app_title_label.setObjectName("titleLabel")
        app_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_title_label.setStyleSheet(
            "font-size: 32px; font-weight: bold; color: #1a73e8; padding: 20px; margin-bottom: 30px;"
        )
        login_screen_layout.addWidget(app_title_label)
        login_screen_layout.addStretch(1)

        self.setCentralWidget(login_screen_widget)
        self.setMinimumSize(600, 450)
        self.resize(700, 500)

        self.hide()
        self.attempt_login()

    def attempt_login(self):
        # Kiểm tra và đóng dialog hiện tại nếu đang hiển thị
        if self.login_dialog_instance and self.login_dialog_instance.isVisible():
            self.login_dialog_instance.close()
            self.login_dialog_instance.deleteLater()
            self.login_dialog_instance = None

        # Tạo dialog mới
        self.login_dialog_instance = LoginDialog(self)
        self.login_dialog_instance.setModal(True)
        self.login_dialog_instance.register_requested.connect(
            self.handle_registration_request
        )

        while True:  # Vòng lặp để hiển thị lại form nếu nhập sai
            if self.login_dialog_instance.exec():
                username = self.login_dialog_instance.username_input.text()
                password = self.login_dialog_instance.password_input.text()

                if not username or not password:
                    QMessageBox.warning(
                        self, "❌ Lỗi", "Vui lòng nhập đầy đủ thông tin!"
                    )
                    continue  # Hiển thị lại form thay vì thoát

                user = self.session.query(User).filter_by(username=username).first()
                if user:
                    try:
                        password_bytes = password.encode("utf-8")
                        hashed_db = user.password
                        if isinstance(hashed_db, str):
                            hashed_db = hashed_db.encode("utf-8")
                        if bcrypt.checkpw(password_bytes, hashed_db):
                            if user.status != "active":
                                QMessageBox.warning(
                                    self,
                                    "⚠️ Thông báo",
                                    "Tài khoản chưa được kích hoạt!",
                                )
                                continue  # Hiển thị lại form
                            self.current_user = user
                            if self.login_dialog_instance:
                                self.login_dialog_instance.deleteLater()
                                self.login_dialog_instance = None
                            self.show()
                            self.setup_main_interface()
                            break  # Thoát vòng lặp khi đăng nhập thành công
                        else:
                            QMessageBox.warning(self, "❌ Lỗi", "Mật khẩu không đúng!")
                            continue  # Hiển thị lại form
                    except Exception as e:
                        QMessageBox.warning(self, "❌ Lỗi", f"Lỗi xác thực: {str(e)}")
                        continue  # Hiển thị lại form
                else:
                    QMessageBox.warning(self, "❌ Lỗi", "Tên đăng nhập không tồn tại!")
                    continue  # Hiển thị lại form
            else:
                # Người dùng nhấn "Hủy" hoặc đóng form
                if self.login_dialog_instance:
                    self.login_dialog_instance.deleteLater()
                    self.login_dialog_instance = None
                if not self.current_user and not self._navigating_to_register:
                    QApplication.instance().quit()  # Thoát ứng dụng nếu chưa đăng nhập
                else:
                    self.show()
                self._navigating_to_register = False
                break  # Thoát vòng lặp

    def handle_registration_request(self):
        self._navigating_to_register = True
        if self.login_dialog_instance:
            self.login_dialog_instance.close()
            self.login_dialog_instance.deleteLater()
            self.login_dialog_instance = None

        if self.register_dialog_instance and self.register_dialog_instance.isVisible():
            self.register_dialog_instance.close()
            self.register_dialog_instance.deleteLater()
            self.register_dialog_instance = None

        self.register_dialog_instance = RegisterDialog(self, session=self.session)
        self.register_dialog_instance.setModal(True)

        if self.register_dialog_instance.exec():
            username = self.register_dialog_instance.username_input.text().strip()
            password = self.register_dialog_instance.password_input.text()
            email = self.register_dialog_instance.email_input.text().strip()
            name = self.register_dialog_instance.name_input.text().strip()
            phone = self.register_dialog_instance.phone_input.text().strip()
            address = self.register_dialog_instance.address_input.text().strip()

            hashed_password = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            new_user = User(
                username=username,
                password=hashed_password,
                email=email,
                name=name,
                phone=phone,
                address=address,
                role=Role.customer,
                status="inactive",
            )
            try:
                self.session.add(new_user)
                self.session.commit()
                if email:
                    subject = "Chào mừng bạn đến với Hệ thống Quản lý Đơn hàng"
                    content = f"""
                    <h3>Đăng ký thành công</h3>
                    <p>Xin chào {name},</p>
                    <p>Tài khoản của bạn với tên đăng nhập <strong>{username}</strong> đã được tạo thành công.</p>
                    <p>Vui lòng chờ quản trị viên kích hoạt tài khoản để bắt đầu sử dụng.</p>
                    <p>Cảm ơn bạn đã tham gia!</p>
                    """
                    send_email_notification(email, subject, content)
                QMessageBox.information(
                    self,
                    "Thành công",
                    "Đăng ký thành công! Vui lòng chờ Admin kích hoạt.",
                )
            except Exception as e:
                self.session.rollback()
                QMessageBox.warning(self, "Lỗi", f"Lỗi khi đăng ký: {str(e)}")
                return

        if self.register_dialog_instance:
            self.register_dialog_instance.deleteLater()
            self.register_dialog_instance = None
        self._navigating_to_register = False
        self.attempt_login()

    def logout(self):
        reply = QMessageBox.question(
            self,
            "🔄 Xác nhận",
            "Bạn có chắc chắn muốn đăng xuất?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.current_user = None
            if self.login_dialog_instance:
                self.login_dialog_instance.close()
                self.login_dialog_instance.deleteLater()
                self.login_dialog_instance = None
            if self.register_dialog_instance:
                self.register_dialog_instance.close()
                self.register_dialog_instance.deleteLater()
                self.register_dialog_instance = None
            self.hide()
            self.setup_login_screen()

    def create_header(self):
        self.header_frame = QFrame()
        self.header_frame.setObjectName("headerFrame")
        self.header_frame.setFixedHeight(70)

        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(20, 0, 20, 0)

        self.app_title_main = QLabel("HỆ THỐNG QUẢN LÝ")
        self.app_title_main.setStyleSheet(
            "color: white; font-size: 22px; font-weight: bold;"
        )
        header_layout.addWidget(self.app_title_main)
        header_layout.addStretch()

        self.user_info_label = QLabel("")
        self.user_info_label.setObjectName("userInfoLabel")
        self.user_info_label.setVisible(False)
        self.user_info_label.setCursor(
            Qt.CursorShape.PointingHandCursor
        )  # Đặt con trỏ thành hình bàn tay
        self.user_info_label.mousePressEvent = (
            self.show_user_profile
        )  # Gắn sự kiện nhấp chuột
        header_layout.addWidget(self.user_info_label)

        self.logout_button = QPushButton("🚪 Đăng xuất")
        self.logout_button.setObjectName("logoutButton")
        self.logout_button.setFixedWidth(150)
        self.logout_button.clicked.connect(self.logout)
        self.logout_button.setVisible(False)
        header_layout.addWidget(self.logout_button)

    def setup_main_interface(self):
        self.clear_current_central_widget()

        main_interface_widget = QWidget()
        self.main_layout = QVBoxLayout(main_interface_widget)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.create_header()
        self.main_layout.addWidget(self.header_frame)

        if self.current_user:
            self.user_info_label.setText(
                f"👤 {self.current_user.name} ({self.current_user.role.value})"
            )
            self.user_info_label.setVisible(True)
            self.logout_button.setVisible(True)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.addWidget(self.content_widget)

        self.tabs = QTabWidget()
        self.content_layout.addWidget(self.tabs)

        # Kết nối tín hiệu currentChanged với phương thức xử lý
        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.setup_role_based_ui(self.current_user.role)

        self.setCentralWidget(main_interface_widget)
        self.setGeometry(100, 100, 1400, 800)

    def on_tab_changed(self, index):
        """Xử lý khi chuyển tab, tải lại dữ liệu mới nhất."""
        tab_name = self.tabs.tabText(index)  # Lấy tên của tab hiện tại
        try:
            if tab_name == "👥 Người dùng" and self.current_user.role == Role.admin:
                self.filter_users()
            elif tab_name == "📦 Sản phẩm":
                self.filter_products()
            elif tab_name == "📋 Đơn hàng":
                self.filter_orders()
            elif (
                tab_name == "🛒 Đơn hàng của tôi"
                and self.current_user.role == Role.customer
            ):
                self.filter_customer_orders()
            elif tab_name == "📊 Thống kê":
                # Tải lại dữ liệu thống kê (nếu cần)
                self.refresh_statistics()
        except Exception as e:
            QMessageBox.critical(
                self, "Lỗi tải dữ liệu", f"Lỗi khi tải dữ liệu: {str(e)}"
            )

    def refresh_statistics(self):
        """Làm mới dữ liệu trong tab Thống kê."""
        if not hasattr(self, "stats_sub_tabs") or not self.stats_sub_tabs:
            return

        # Xóa các biểu đồ cũ
        for i in range(self.stats_sub_tabs.count()):
            widget = self.stats_sub_tabs.widget(i)
            layout = widget.layout()
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        # Tải lại dữ liệu thống kê
        staff_id = (
            self.current_user.id if self.current_user.role == Role.staff else None
        )

        # Sub-Tab: Doanh thu theo danh mục
        categories, revenues = get_revenue_by_category(self.session, staff_id)
        print("Danh mục:", categories, "Doanh thu:", revenues)  # Debug dữ liệu
        if categories and revenues:
            self.revenue_by_category_chart = self.create_revenue_by_category_chart(
                categories, revenues
            )
            self.revenue_by_category_layout.addWidget(
                QLabel("Doanh thu theo danh mục (nghìn VNĐ):")
            )
            self.revenue_by_category_layout.addWidget(self.revenue_by_category_chart)
        else:
            self.revenue_by_category_layout.addWidget(
                QLabel("Không có dữ liệu doanh thu theo danh mục.")
            )
        self.revenue_by_category_layout.addStretch()

        # Sub-Tab: Doanh thu theo tháng
        months, monthly_revenues = get_revenue_by_month(self.session, staff_id)
        print("Tháng:", months, "Doanh thu:", monthly_revenues)  # Debug dữ liệu
        if months and monthly_revenues:
            self.revenue_by_month_chart = self.create_revenue_by_month_chart(
                months, monthly_revenues
            )
            self.revenue_by_month_layout.addWidget(
                QLabel("Doanh thu theo tháng (nghìn VNĐ):")
            )
            self.revenue_by_month_layout.addWidget(self.revenue_by_month_chart)
        else:
            self.revenue_by_month_layout.addWidget(
                QLabel("Không có dữ liệu doanh thu theo tháng.")
            )
        self.revenue_by_month_layout.addStretch()

        # Sub-Tab: Phân bố trạng thái đơn hàng
        statuses, counts = get_order_status_distribution(self.session, staff_id)
        print("Trạng thái:", statuses, "Số lượng:", counts)  # Debug dữ liệu
        if statuses and counts:
            self.order_status_chart = self.create_order_status_chart(statuses, counts)
            self.order_status_layout.addWidget(QLabel("Phân bố trạng thái đơn hàng:"))
            self.order_status_layout.addWidget(self.order_status_chart)
        else:
            self.order_status_layout.addWidget(
                QLabel("Không có dữ liệu trạng thái đơn hàng.")
            )
        self.order_status_layout.addStretch()

    def reset_ui_components(self):
        for table_attr in [
            "user_table",
            "product_table",
            "order_table",
            "customer_order_table",
            "stats_table",
        ]:
            if hasattr(self, table_attr):
                setattr(self, table_attr, None)
        if hasattr(self, "tabs"):
            self.tabs = None
        if hasattr(self, "header_frame"):
            self.header_frame = None
        if hasattr(self, "user_info_label"):
            self.user_info_label = None
        if hasattr(self, "logout_button"):
            self.logout_button = None
        if hasattr(self, "app_title_main"):
            self.app_title_main = None
        if hasattr(self, "content_widget"):
            self.content_widget = None

    def create_button_frame(self, buttons):
        button_frame = QFrame()
        button_frame.setObjectName("buttonFrame")
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(10, 5, 10, 5)

        for button in buttons:
            button_layout.addWidget(button)
        button_layout.addStretch()
        return button_frame

    def setup_role_based_ui(self, role):
        if hasattr(self, "tabs") and self.tabs:
            self.tabs.clear()

        if role == Role.admin:
            self.setup_admin_ui()
        elif role == Role.staff:
            self.setup_staff_ui()
        elif role == Role.customer:
            self.setup_customer_ui()
        else:
            QMessageBox.information(
                self,
                "Thông báo",
                f"Vai trò '{str(role)}' không có giao diện được định nghĩa, hiển thị giao diện khách hàng.",
            )
            self.setup_customer_ui()

    def setup_admin_ui(self):
        # Tab Người dùng
        self.user_tab = QWidget()
        self.user_layout = QVBoxLayout(self.user_tab)
        self.user_layout.setSpacing(10)
        self.user_layout.setContentsMargins(15, 15, 15, 15)

        user_title = QLabel("👥 Quản lý người dùng")
        user_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1a73e8; margin-bottom: 10px;"
        )
        self.user_layout.addWidget(user_title)

        user_search_frame = QFrame()
        user_search_frame.setObjectName("buttonFrame")
        user_search_layout = QHBoxLayout(user_search_frame)
        user_search_layout.setSpacing(10)
        user_search_layout.setContentsMargins(10, 5, 10, 5)

        self.user_search_input = QLineEdit()
        self.user_search_input.setPlaceholderText("Tìm kiếm theo tên, email...")
        self.user_search_input.setFixedWidth(200)
        self.user_search_input.textChanged.connect(self.filter_users)
        user_search_layout.addWidget(QLabel("🔍 Tìm kiếm:"))
        user_search_layout.addWidget(self.user_search_input)

        self.user_role_filter = QComboBox()
        self.user_role_filter.addItems(["Tất cả vai trò"] + [r.value for r in Role])
        self.user_role_filter.currentIndexChanged.connect(self.filter_users)
        user_search_layout.addWidget(QLabel("👔 Vai trò:"))
        user_search_layout.addWidget(self.user_role_filter)

        self.user_status_filter = QComboBox()
        self.user_status_filter.addItems(
            ["Tất cả trạng thái", "Hoạt động", "Không hoạt động"]
        )
        self.user_status_filter.currentIndexChanged.connect(self.filter_users)
        user_search_layout.addWidget(QLabel("📊 Trạng thái:"))
        user_search_layout.addWidget(self.user_status_filter)

        user_search_layout.addStretch()
        self.user_layout.addWidget(user_search_frame)

        self.user_table = QTableWidget()
        self.user_table.setColumnCount(6)
        self.user_table.setHorizontalHeaderLabels(
            ["ID", "Tên đăng nhập", "Tên", "Email", "Vai trò", "Trạng thái"]
        )
        self.user_table.setAlternatingRowColors(True)
        self.user_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.user_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.user_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.filter_users()

        self.add_user_button = QPushButton("➕ Thêm người dùng")
        self.add_user_button.setObjectName("addButton")
        self.add_user_button.clicked.connect(self.add_user)
        self.edit_user_button = QPushButton("✏️ Sửa người dùng")
        self.edit_user_button.setObjectName("editButton")
        self.edit_user_button.clicked.connect(self.edit_user)
        self.delete_user_button = QPushButton("🗑️ Xóa người dùng")
        self.delete_user_button.setObjectName("deleteButton")
        self.delete_user_button.clicked.connect(self.delete_user)
        self.export_users_button = QPushButton("📤 Xuất Excel")
        self.export_users_button.setObjectName("addButton")
        self.export_users_button.clicked.connect(self.export_users)

        user_button_frame = self.create_button_frame(
            [
                self.add_user_button,
                self.edit_user_button,
                self.delete_user_button,
                self.export_users_button,
            ]
        )
        self.user_layout.addWidget(self.user_table)
        self.user_layout.addWidget(user_button_frame)
        self.tabs.addTab(self.user_tab, "👥 Người dùng")

        # Tab Sản phẩm
        self.product_tab = QWidget()
        self.product_layout = QVBoxLayout(self.product_tab)
        product_title = QLabel("📦 Quản lý sản phẩm")
        product_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1a73e8; margin-bottom: 10px;"
        )
        self.product_layout.addWidget(product_title)

        product_search_frame = QFrame()
        product_search_frame.setObjectName("buttonFrame")
        product_search_layout = QHBoxLayout(product_search_frame)
        product_search_layout.setSpacing(10)
        product_search_layout.setContentsMargins(10, 5, 10, 5)

        self.product_search_input = QLineEdit()
        self.product_search_input.setPlaceholderText("Tìm kiếm theo tên, mã...")
        self.product_search_input.setFixedWidth(200)
        self.product_search_input.textChanged.connect(self.filter_products)
        product_search_layout.addWidget(QLabel("🔍 Tìm kiếm:"))
        product_search_layout.addWidget(self.product_search_input)

        self.product_category_filter = QComboBox()
        self.product_category_filter.addItems(
            ["Tất cả danh mục", "Áo", "Quần", "Giày", "Phụ kiện"]
        )
        self.product_category_filter.currentIndexChanged.connect(self.filter_products)
        product_search_layout.addWidget(QLabel("📂 Danh mục:"))
        product_search_layout.addWidget(self.product_category_filter)

        self.product_status_filter = QComboBox()
        self.product_status_filter.addItems(
            ["Tất cả trạng thái", "Hoạt động", "Không hoạt động"]
        )
        self.product_status_filter.currentIndexChanged.connect(self.filter_products)
        product_search_layout.addWidget(QLabel("📊 Trạng thái:"))
        product_search_layout.addWidget(self.product_status_filter)

        product_search_layout.addStretch()
        self.product_layout.addWidget(product_search_frame)

        self.product_table = QTableWidget()
        self.product_table.setColumnCount(6)
        self.product_table.setHorizontalHeaderLabels(
            ["ID", "Tên", "Mã", "Giá", "Tồn kho", "Trạng thái"]
        )
        self.product_table.setAlternatingRowColors(True)
        self.product_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.product_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.product_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.filter_products()

        self.add_product_button = QPushButton("➕ Thêm sản phẩm")
        self.add_product_button.setObjectName("addButton")
        self.add_product_button.clicked.connect(self.add_product)
        self.edit_product_button = QPushButton("✏️ Sửa sản phẩm")
        self.edit_product_button.setObjectName("editButton")
        self.edit_product_button.clicked.connect(self.edit_product)
        self.delete_product_button = QPushButton("🗑️ Xóa sản phẩm")
        self.delete_product_button.setObjectName("deleteButton")
        self.delete_product_button.clicked.connect(self.delete_product)
        self.export_products_button = QPushButton("📤 Xuất Excel")
        self.export_products_button.setObjectName("addButton")
        self.export_products_button.clicked.connect(self.export_products)

        product_button_frame = self.create_button_frame(
            [
                self.add_product_button,
                self.edit_product_button,
                self.delete_product_button,
                self.export_products_button,
            ]
        )
        self.product_layout.addWidget(self.product_table)
        self.product_layout.addWidget(product_button_frame)
        self.tabs.addTab(self.product_tab, "📦 Sản phẩm")

        # Tab Đơn hàng
        self.order_tab = QWidget()
        self.order_layout = QVBoxLayout(self.order_tab)
        order_title = QLabel("📋 Quản lý đơn hàng")
        order_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1a73e8; margin-bottom: 10px;"
        )
        self.order_layout.addWidget(order_title)

        order_search_frame = QFrame()
        order_search_frame.setObjectName("buttonFrame")
        order_search_layout = QHBoxLayout(order_search_frame)
        order_search_layout.setSpacing(10)
        order_search_layout.setContentsMargins(10, 5, 10, 5)

        self.order_search_input = QLineEdit()
        self.order_search_input.setPlaceholderText(
            "Tìm kiếm theo mã, tên khách hàng..."
        )
        self.order_search_input.setFixedWidth(200)
        self.order_search_input.textChanged.connect(self.filter_orders)
        order_search_layout.addWidget(QLabel("🔍 Tìm kiếm:"))
        order_search_layout.addWidget(self.order_search_input)

        self.order_status_filter = QComboBox()
        self.order_status_filter.addItems(
            ["Tất cả trạng thái"] + [s.value for s in OrderStatus]
        )
        self.order_status_filter.currentIndexChanged.connect(self.filter_orders)
        order_search_layout.addWidget(QLabel("📋 Trạng thái:"))
        order_search_layout.addWidget(self.order_status_filter)

        order_search_layout.addStretch()
        self.order_layout.addWidget(order_search_frame)

        self.order_table = QTableWidget()
        self.order_table.setColumnCount(7)  # Tăng từ 5 lên 7 cột
        self.order_table.setHorizontalHeaderLabels(
            [
                "ID",
                "Mã",
                "Khách hàng",
                "Tên sản phẩm",
                "Hình ảnh",
                "Trạng thái",
                "Tổng tiền",
            ]
        )
        self.order_table.setAlternatingRowColors(True)
        self.order_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.order_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.order_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.order_table.setColumnWidth(4, 50)  # Cột Hình ảnh có chiều rộng cố định
        self.filter_orders()

        self.edit_order_button = QPushButton("✏️ Cập nhật trạng thái")
        self.edit_order_button.setObjectName("editButton")
        self.edit_order_button.clicked.connect(self.edit_order)
        self.export_orders_button = QPushButton("📤 Xuất Excel")
        self.export_orders_button.setObjectName("addButton")
        self.export_orders_button.clicked.connect(self.export_orders)

        order_button_frame = self.create_button_frame(
            [self.edit_order_button, self.export_orders_button]
        )
        self.order_layout.addWidget(self.order_table)
        self.order_layout.addWidget(order_button_frame)
        self.tabs.addTab(self.order_tab, "📋 Đơn hàng")

        # Tab Thống kê với Sub-Tabs
        self.stats_tab = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_tab)
        self.stats_layout.setSpacing(10)
        self.stats_layout.setContentsMargins(15, 15, 15, 15)

        stats_title = QLabel("📊 Thống kê")
        stats_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1a73e8; margin-bottom: 10px;"
        )
        self.stats_layout.addWidget(stats_title)

        # Tạo sub-tabs cho các biểu đồ
        self.stats_sub_tabs = QTabWidget()
        self.stats_sub_tabs.setObjectName("statsSubTabs")
        self.stats_layout.addWidget(self.stats_sub_tabs)

        # Sub-Tab: Doanh thu theo danh mục
        self.revenue_by_category_tab = QWidget()
        self.revenue_by_category_layout = QVBoxLayout(self.revenue_by_category_tab)
        categories, revenues = get_revenue_by_category(self.session)
        print("Danh mục:", categories, "Doanh thu:", revenues)  # Debug dữ liệu
        if categories and revenues:
            self.revenue_by_category_chart = self.create_revenue_by_category_chart(
                categories, revenues
            )
            self.revenue_by_category_layout.addWidget(
                QLabel("Doanh thu theo danh mục (nghìn VNĐ):")
            )
            self.revenue_by_category_layout.addWidget(self.revenue_by_category_chart)
        else:
            self.revenue_by_category_layout.addWidget(
                QLabel("Không có dữ liệu doanh thu theo danh mục.")
            )
        self.revenue_by_category_layout.addStretch()
        self.stats_sub_tabs.addTab(
            self.revenue_by_category_tab, "📊 Doanh thu theo danh mục"
        )

        # Sub-Tab: Doanh thu theo tháng
        self.revenue_by_month_tab = QWidget()
        self.revenue_by_month_layout = QVBoxLayout(self.revenue_by_month_tab)
        months, monthly_revenues = get_revenue_by_month(self.session)
        print("Tháng:", months, "Doanh thu:", monthly_revenues)  # Debug dữ liệu
        if months and monthly_revenues:
            self.revenue_by_month_chart = self.create_revenue_by_month_chart(
                months, monthly_revenues
            )
            self.revenue_by_month_layout.addWidget(
                QLabel("Doanh thu theo tháng (nghìn VNĐ):")
            )
            self.revenue_by_month_layout.addWidget(self.revenue_by_month_chart)
        else:
            self.revenue_by_month_layout.addWidget(
                QLabel("Không có dữ liệu doanh thu theo tháng.")
            )
        self.revenue_by_month_layout.addStretch()
        self.stats_sub_tabs.addTab(self.revenue_by_month_tab, "📈 Doanh thu theo tháng")

        # Sub-Tab: Phân bố trạng thái đơn hàng
        self.order_status_tab = QWidget()
        self.order_status_layout = QVBoxLayout(self.order_status_tab)
        statuses, counts = get_order_status_distribution(self.session)
        print("Trạng thái:", statuses, "Số lượng:", counts)  # Debug dữ liệu
        if statuses and counts:
            self.order_status_chart = self.create_order_status_chart(statuses, counts)
            self.order_status_layout.addWidget(QLabel("Phân bố trạng thái đơn hàng:"))
            self.order_status_layout.addWidget(self.order_status_chart)
        else:
            self.order_status_layout.addWidget(
                QLabel("Không có dữ liệu trạng thái đơn hàng.")
            )
        self.order_status_layout.addStretch()
        self.stats_sub_tabs.addTab(self.order_status_tab, "🥧 Trạng thái đơn hàng")

        # Nút xuất thống kê
        self.export_stats_button = QPushButton("📤 Xuất thống kê Excel")
        self.export_stats_button.setObjectName("addButton")
        self.export_stats_button.clicked.connect(self.export_statistics)
        stats_button_frame = self.create_button_frame([self.export_stats_button])
        self.stats_layout.addWidget(stats_button_frame)
        self.stats_layout.addStretch()
        self.tabs.addTab(self.stats_tab, "📊 Thống kê")

    def setup_staff_ui(self):
        # Tab Sản phẩm
        self.product_tab = QWidget()
        self.product_layout = QVBoxLayout(self.product_tab)
        product_title = QLabel("📦 Quản lý sản phẩm")
        product_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1a73e8; margin-bottom: 10px;"
        )
        self.product_layout.addWidget(product_title)

        product_search_frame = QFrame()
        product_search_frame.setObjectName("buttonFrame")
        product_search_layout = QHBoxLayout(product_search_frame)
        product_search_layout.setSpacing(10)
        product_search_layout.setContentsMargins(10, 5, 10, 5)

        self.product_search_input = QLineEdit()
        self.product_search_input.setPlaceholderText("Tìm kiếm theo tên, mã...")
        self.product_search_input.setFixedWidth(200)
        self.product_search_input.textChanged.connect(self.filter_products)
        product_search_layout.addWidget(QLabel("🔍 Tìm kiếm:"))
        product_search_layout.addWidget(self.product_search_input)

        self.product_category_filter = QComboBox()
        self.product_category_filter.addItems(
            ["Tất cả danh mục", "Áo", "Quần", "Giày", "Phụ kiện"]
        )
        self.product_category_filter.currentIndexChanged.connect(self.filter_products)
        product_search_layout.addWidget(QLabel("📂 Danh mục:"))
        product_search_layout.addWidget(self.product_category_filter)

        self.product_status_filter = QComboBox()
        self.product_status_filter.addItems(
            ["Tất cả trạng thái", "Hoạt động", "Không hoạt động"]
        )
        self.product_status_filter.currentIndexChanged.connect(self.filter_products)
        product_search_layout.addWidget(QLabel("📊 Trạng thái:"))
        product_search_layout.addWidget(self.product_status_filter)

        product_search_layout.addStretch()
        self.product_layout.addWidget(product_search_frame)

        self.product_table = QTableWidget()
        self.product_table.setColumnCount(6)
        self.product_table.setHorizontalHeaderLabels(
            ["ID", "Tên", "Mã", "Giá", "Tồn kho", "Trạng thái"]
        )
        self.product_table.setAlternatingRowColors(True)
        self.product_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.product_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.product_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.filter_products()

        self.add_product_button = QPushButton("➕ Thêm sản phẩm")
        self.add_product_button.setObjectName("addButton")
        self.add_product_button.clicked.connect(self.add_product)
        self.edit_product_button = QPushButton("✏️ Sửa sản phẩm")
        self.edit_product_button.setObjectName("editButton")
        self.edit_product_button.clicked.connect(self.edit_product)
        self.export_products_button = QPushButton("📤 Xuất Excel")
        self.export_products_button.setObjectName("addButton")
        self.export_products_button.clicked.connect(self.export_products)

        product_button_frame = self.create_button_frame(
            [
                self.add_product_button,
                self.edit_product_button,
                self.export_products_button,
            ]
        )
        self.product_layout.addWidget(self.product_table)
        self.product_layout.addWidget(product_button_frame)
        self.tabs.addTab(self.product_tab, "📦 Sản phẩm")

        # Tab Đơn hàng
        self.order_tab = QWidget()
        self.order_layout = QVBoxLayout(self.order_tab)
        order_title = QLabel("📋 Quản lý đơn hàng")
        order_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1a73e8; margin-bottom: 10px;"
        )
        self.order_layout.addWidget(order_title)

        order_search_frame = QFrame()
        order_search_frame.setObjectName("buttonFrame")
        order_search_layout = QHBoxLayout(order_search_frame)
        order_search_layout.setSpacing(10)
        order_search_layout.setContentsMargins(10, 5, 10, 5)

        self.order_search_input = QLineEdit()
        self.order_search_input.setPlaceholderText(
            "Tìm kiếm theo mã, tên khách hàng..."
        )
        self.order_search_input.setFixedWidth(200)
        self.order_search_input.textChanged.connect(self.filter_orders)
        order_search_layout.addWidget(QLabel("🔍 Tìm kiếm:"))
        order_search_layout.addWidget(self.order_search_input)

        self.order_status_filter = QComboBox()
        self.order_status_filter.addItems(
            ["Tất cả trạng thái"] + [s.value for s in OrderStatus]
        )
        self.order_status_filter.currentIndexChanged.connect(self.filter_orders)
        order_search_layout.addWidget(QLabel("📋 Trạng thái:"))
        order_search_layout.addWidget(self.order_status_filter)

        order_search_layout.addStretch()
        self.order_layout.addWidget(order_search_frame)

        self.order_table = QTableWidget()
        self.order_table.setColumnCount(7)  # Tăng từ 5 lên 7 cột
        self.order_table.setHorizontalHeaderLabels(
            [
                "ID",
                "Mã",
                "Khách hàng",
                "Tên sản phẩm",
                "Hình ảnh",
                "Trạng thái",
                "Tổng tiền",
            ]
        )
        self.order_table.setAlternatingRowColors(True)
        self.order_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.order_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.order_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.order_table.setColumnWidth(4, 100)  # Cột Hình ảnh có chiều rộng cố định
        self.filter_orders()

        self.add_order_button = QPushButton("➕ Thêm đơn hàng")
        self.add_order_button.setObjectName("addButton")
        self.add_order_button.clicked.connect(self.add_order_for_customer_by_staff)
        self.edit_order_button = QPushButton("✏️ Cập nhật trạng thái")
        self.edit_order_button.setObjectName("editButton")
        self.edit_order_button.clicked.connect(self.edit_order)
        self.export_orders_button = QPushButton("📤 Xuất Excel")
        self.export_orders_button.setObjectName("addButton")
        self.export_orders_button.clicked.connect(self.export_orders)

        order_button_frame = self.create_button_frame(
            [self.add_order_button, self.edit_order_button, self.export_orders_button]
        )
        self.order_layout.addWidget(self.order_table)
        self.order_layout.addWidget(order_button_frame)
        self.tabs.addTab(self.order_tab, "📋 Đơn hàng")

        # Tab Thống kê với Sub-Tabs
        self.stats_tab = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_tab)
        self.stats_layout.setSpacing(10)
        self.stats_layout.setContentsMargins(15, 15, 15, 15)

        stats_title = QLabel("📊 Thống kê")
        stats_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1a73e8; margin-bottom: 10px;"
        )
        self.stats_layout.addWidget(stats_title)

        # Tạo sub-tabs cho các biểu đồ
        self.stats_sub_tabs = QTabWidget()
        self.stats_sub_tabs.setObjectName("statsSubTabs")
        self.stats_layout.addWidget(self.stats_sub_tabs)

        # Sub-Tab: Doanh thu theo danh mục
        self.revenue_by_category_tab = QWidget()
        self.revenue_by_category_layout = QVBoxLayout(self.revenue_by_category_tab)
        categories, revenues = get_revenue_by_category(
            self.session, self.current_user.id
        )
        print("Danh mục:", categories, "Doanh thu:", revenues)  # Debug dữ liệu
        if categories and revenues:
            self.revenue_by_category_chart = self.create_revenue_by_category_chart(
                categories, revenues
            )
            self.revenue_by_category_layout.addWidget(
                QLabel("Doanh thu theo danh mục (nghìn VNĐ):")
            )
            self.revenue_by_category_layout.addWidget(self.revenue_by_category_chart)
        else:
            self.revenue_by_category_layout.addWidget(
                QLabel("Không có dữ liệu doanh thu theo danh mục.")
            )
        self.revenue_by_category_layout.addStretch()
        self.stats_sub_tabs.addTab(
            self.revenue_by_category_tab, "📊 Doanh thu theo danh mục"
        )

        # Sub-Tab: Doanh thu theo tháng
        self.revenue_by_month_tab = QWidget()
        self.revenue_by_month_layout = QVBoxLayout(self.revenue_by_month_tab)
        months, monthly_revenues = get_revenue_by_month(
            self.session, self.current_user.id
        )
        print("Tháng:", months, "Doanh thu:", monthly_revenues)  # Debug dữ liệu
        if months and monthly_revenues:
            self.revenue_by_month_chart = self.create_revenue_by_month_chart(
                months, monthly_revenues
            )
            self.revenue_by_month_layout.addWidget(
                QLabel("Doanh thu theo tháng (nghìn VNĐ):")
            )
            self.revenue_by_month_layout.addWidget(self.revenue_by_month_chart)
        else:
            self.revenue_by_month_layout.addWidget(
                QLabel("Không có dữ liệu doanh thu theo tháng.")
            )
        self.revenue_by_month_layout.addStretch()
        self.stats_sub_tabs.addTab(self.revenue_by_month_tab, "📈 Doanh thu theo tháng")

        # Sub-Tab: Phân bố trạng thái đơn hàng
        self.order_status_tab = QWidget()
        self.order_status_layout = QVBoxLayout(self.order_status_tab)
        statuses, counts = get_order_status_distribution(
            self.session, self.current_user.id
        )
        print("Trạng thái:", statuses, "Số lượng:", counts)  # Debug dữ liệu
        if statuses and counts:
            self.order_status_chart = self.create_order_status_chart(statuses, counts)
            self.order_status_layout.addWidget(QLabel("Phân bố trạng thái đơn hàng:"))
            self.order_status_layout.addWidget(self.order_status_chart)
        else:
            self.order_status_layout.addWidget(
                QLabel("Không có dữ liệu trạng thái đơn hàng.")
            )
        self.order_status_layout.addStretch()
        self.stats_sub_tabs.addTab(self.order_status_tab, "🥧 Trạng thái đơn hàng")

        # Nút xuất thống kê
        self.export_stats_button = QPushButton("📤 Xuất thống kê Excel")
        self.export_stats_button.setObjectName("addButton")
        self.export_stats_button.clicked.connect(self.export_statistics)
        stats_button_frame = self.create_button_frame([self.export_stats_button])
        self.stats_layout.addWidget(stats_button_frame)
        self.stats_layout.addStretch()
        self.tabs.addTab(self.stats_tab, "📊 Thống kê")

    def setup_customer_ui(self):
        self.customer_order_tab = QWidget()
        self.customer_order_layout = QVBoxLayout(self.customer_order_tab)
        self.customer_order_layout.setSpacing(10)
        self.customer_order_layout.setContentsMargins(15, 15, 15, 15)

        customer_title = QLabel("🛒 Đơn hàng của tôi")
        customer_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1a73e8; margin-bottom: 10px;"
        )
        self.customer_order_layout.addWidget(customer_title)

        customer_search_frame = QFrame()
        customer_search_frame.setObjectName("buttonFrame")
        customer_search_layout = QHBoxLayout(customer_search_frame)
        customer_search_layout.setSpacing(10)
        customer_search_layout.setContentsMargins(10, 5, 10, 5)

        self.customer_order_search_input = QLineEdit()
        self.customer_order_search_input.setPlaceholderText("Tìm kiếm theo mã...")
        self.customer_order_search_input.setFixedWidth(200)
        self.customer_order_search_input.textChanged.connect(
            self.filter_customer_orders
        )
        customer_search_layout.addWidget(QLabel("🔍 Tìm kiếm:"))
        customer_search_layout.addWidget(self.customer_order_search_input)

        self.customer_order_status_filter = QComboBox()
        self.customer_order_status_filter.addItems(
            ["Tất cả trạng thái"] + [s.value for s in OrderStatus]
        )
        self.customer_order_status_filter.currentIndexChanged.connect(
            self.filter_customer_orders
        )
        customer_search_layout.addWidget(QLabel("📋 Trạng thái:"))
        customer_search_layout.addWidget(self.customer_order_status_filter)

        customer_search_layout.addStretch()
        self.customer_order_layout.addWidget(customer_search_frame)

        self.customer_order_table = QTableWidget()
        self.customer_order_table.setColumnCount(6)  # Tăng từ 4 lên 6 cột
        self.customer_order_table.setHorizontalHeaderLabels(
            ["ID", "Mã", "Tên sản phẩm", "Hình ảnh", "Trạng thái", "Tổng tiền"]
        )
        self.customer_order_table.setAlternatingRowColors(True)
        self.customer_order_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.customer_order_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.customer_order_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.customer_order_table.setColumnWidth(
            3, 50
        )  # Cột Hình ảnh có chiều rộng cố định
        self.filter_customer_orders()

        self.create_new_order_button = QPushButton("➕ Tạo đơn hàng mới")
        self.create_new_order_button.setObjectName("addButton")
        self.create_new_order_button.clicked.connect(self.add_order)
        self.cancel_order_button = QPushButton("❌ Hủy đơn hàng")
        self.cancel_order_button.setObjectName("deleteButton")
        self.cancel_order_button.clicked.connect(self.cancel_order)
        self.export_customer_orders_button = QPushButton("📤 Xuất Excel")
        self.export_customer_orders_button.setObjectName("addButton")
        self.export_customer_orders_button.clicked.connect(self.export_customer_orders)

        customer_button_frame = self.create_button_frame(
            [
                self.create_new_order_button,
                self.cancel_order_button,
                self.export_customer_orders_button,
            ]
        )
        self.customer_order_layout.addWidget(self.customer_order_table)
        self.customer_order_layout.addWidget(customer_button_frame)
        self.tabs.addTab(self.customer_order_tab, "🛒 Đơn hàng của tôi")

    def filter_users(self):
        if not hasattr(self, "user_table") or not self.user_table:
            return
        try:
            search_text = self.user_search_input.text().lower().strip()
            role_filter = self.user_role_filter.currentText()
            status_filter = self.user_status_filter.currentText()

            query = self.session.query(User)

            if role_filter != "Tất cả vai trò":
                query = query.filter_by(role=Role[role_filter])

            if status_filter != "Tất cả trạng thái":
                status_value = "active" if status_filter == "Hoạt động" else "inactive"
                query = query.filter_by(status=status_value)

            if search_text:
                query = query.filter(
                    (User.username.ilike(f"%{search_text}%"))
                    | (User.name.ilike(f"%{search_text}%"))
                    | (User.email.ilike(f"%{search_text}%"))
                )

            users = query.all()
            self.user_table.setRowCount(len(users))
            for row, user in enumerate(users):
                self.user_table.setItem(row, 0, QTableWidgetItem(str(user.id)))
                self.user_table.setItem(row, 1, QTableWidgetItem(user.username or ""))
                self.user_table.setItem(row, 2, QTableWidgetItem(user.name or ""))
                self.user_table.setItem(row, 3, QTableWidgetItem(user.email or ""))
                self.user_table.setItem(row, 4, QTableWidgetItem(user.role.value))
                self.user_table.setItem(
                    row,
                    5,
                    QTableWidgetItem(
                        "Hoạt động" if user.status == "active" else "Không hoạt động"
                    ),
                )
        except Exception as e:
            QMessageBox.critical(self, "Lỗi lọc người dùng", str(e))

    def load_users(self):
        self.filter_users()

    def add_user(self):
        dialog = UserDialog(self)
        if dialog.exec():
            password = dialog.password_input.text()
            if not password:
                QMessageBox.warning(self, "❌ Lỗi", "Mật khẩu không được để trống!")
                return
            username = dialog.username_input.text()
            if not username:
                QMessageBox.warning(
                    self, "❌ Lỗi", "Tên đăng nhập không được để trống!"
                )
                return

            hashed_password = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            try:
                role_value = dialog.role_input.currentText()
                user_role = Role[role_value]
            except KeyError:
                QMessageBox.warning(
                    self, "❌ Lỗi", f"Vai trò không hợp lệ: {role_value}"
                )
                return

            user = User(
                username=username,
                password=hashed_password,
                email=dialog.email_input.text(),
                name=dialog.name_input.text(),
                phone=dialog.phone_input.text(),
                address=dialog.address_input.text(),
                role=user_role,
                status=(
                    "active"
                    if dialog.status_input.currentText() == "Hoạt động"
                    else "inactive"
                ),
            )
            try:
                self.session.add(user)
                self.session.commit()
                self.filter_users()

                # Gửi email thông báo khi thêm người dùng mới (cho admin)
                if user.email:
                    subject = "Người dùng mới đã được thêm"
                    content = f"""
                    <h3>Thông báo người dùng mới</h3>
                    <p>Xin chào Quản trị viên,</p>
                    <p>Một người dùng mới đã được thêm vào hệ thống:</p>
                    <p><strong>Tên đăng nhập:</strong> {user.username}<br>
                    <strong>Họ tên:</strong> {user.name}<br>
                    <strong>Email:</strong> {user.email}<br>
                    <strong>Vai trò:</strong> {user.role.value}<br>
                    <strong>Trạng thái:</strong> {user.status}</p>
                    <p>Vui lòng kiểm tra và kích hoạt tài khoản nếu cần.</p>
                    """
                    send_email_notification(user.email, subject, content)

                QMessageBox.information(
                    self, "✅ Thành công", "Thêm người dùng thành công!"
                )

                # Tùy chọn đăng nhập ngay vào tài khoản vừa tạo
                if user.status == "active":
                    reply = QMessageBox.question(
                        self,
                        "Đăng nhập",
                        f"Bạn có muốn đăng nhập ngay vào tài khoản '{user.username}' không?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        self.current_user = user
                        self.setup_main_interface()
            except IntegrityError:
                self.session.rollback()
                QMessageBox.warning(self, "❌ Lỗi", "Tên đăng nhập đã tồn tại!")
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Lỗi thêm người dùng", str(e))

    def edit_user(self):
        if not hasattr(self, "user_table") or not self.user_table:
            return
        selected = self.user_table.currentRow()
        if selected >= 0:
            user_id = int(self.user_table.item(selected, 0).text())
            user = self.session.query(User).get(user_id)
            if not user:
                QMessageBox.warning(self, "❌ Lỗi", "Không tìm thấy người dùng!")
                return

            dialog = UserDialog(self, user)
            if dialog.exec():
                user.username = dialog.username_input.text()
                new_password = dialog.password_input.text()
                if new_password:
                    user.password = bcrypt.hashpw(
                        new_password.encode("utf-8"), bcrypt.gensalt()
                    ).decode("utf-8")
                user.email = dialog.email_input.text()
                user.name = dialog.name_input.text()
                user.phone = dialog.phone_input.text()
                user.address = dialog.address_input.text()
                try:
                    role_value = dialog.role_input.currentText()
                    user.role = Role[role_value]
                except KeyError:
                    QMessageBox.warning(
                        self, "❌ Lỗi", f"Vai trò không hợp lệ: {role_value}"
                    )
                    return
                user.status = (
                    "active"
                    if dialog.status_input.currentText() == "Hoạt động"
                    else "inactive"
                )
                try:
                    self.session.commit()
                    self.filter_users()
                    QMessageBox.information(
                        self, "✅ Thành công", "Cập nhật người dùng thành công!"
                    )
                except IntegrityError:
                    self.session.rollback()
                    QMessageBox.warning(
                        self,
                        "❌ Lỗi",
                        "Tên đăng nhập có thể đã tồn tại cho người dùng khác.",
                    )
                except Exception as e:
                    self.session.rollback()
                    QMessageBox.critical(self, "Lỗi cập nhật người dùng", str(e))
        else:
            QMessageBox.warning(self, "❌ Lỗi", "Vui lòng chọn người dùng để sửa!")

    def delete_user(self):
        if not hasattr(self, "user_table") or not self.user_table:
            return
        selected = self.user_table.currentRow()
        if selected >= 0:
            user_id = int(self.user_table.item(selected, 0).text())
            user = self.session.query(User).get(user_id)
            if not user:
                QMessageBox.warning(self, "❌ Lỗi", "Không tìm thấy người dùng!")
                return

            reply = QMessageBox.question(
                self,
                "⚠️ Xác nhận",
                f"Bạn có chắc muốn xóa người dùng '{user.username}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    self.session.delete(user)
                    self.session.commit()
                    self.filter_users()
                    QMessageBox.information(
                        self, "✅ Thành công", "Xóa người dùng thành công!"
                    )
                except Exception as e:
                    self.session.rollback()
                    QMessageBox.critical(self, "Lỗi xóa người dùng", str(e))
        else:
            QMessageBox.warning(self, "❌ Lỗi", "Vui lòng chọn người dùng để xóa!")

    def filter_products(self):
        if not hasattr(self, "product_table") or not self.product_table:
            return
        try:
            search_text = self.product_search_input.text().lower().strip()
            category_filter = self.product_category_filter.currentText()
            status_filter = self.product_status_filter.currentText()

            query = self.session.query(Product)

            if category_filter != "Tất cả danh mục":
                query = query.filter_by(category=category_filter)

            if status_filter != "Tất cả trạng thái":
                status_value = "active" if status_filter == "Hoạt động" else "inactive"
                query = query.filter_by(status=status_value)

            if search_text:
                query = query.filter(
                    (Product.name.ilike(f"%{search_text}%"))
                    | (Product.code.ilike(f"%{search_text}%"))
                    | (Product.description.ilike(f"%{search_text}%"))
                )

            products = query.all()
            self.product_table.setColumnCount(7)  # Thêm cột "Người tạo"
            self.product_table.setHorizontalHeaderLabels(
                ["ID", "Tên", "Mã", "Giá", "Tồn kho", "Trạng thái", "Người tạo"]
            )
            self.product_table.setRowCount(len(products))
            for row, product in enumerate(products):
                self.product_table.setItem(row, 0, QTableWidgetItem(str(product.id)))
                self.product_table.setItem(row, 1, QTableWidgetItem(product.name or ""))
                self.product_table.setItem(row, 2, QTableWidgetItem(product.code or ""))
                self.product_table.setItem(
                    row, 3, QTableWidgetItem(format_price(product.price or 0))
                )
                self.product_table.setItem(
                    row, 4, QTableWidgetItem(str(product.stock or 0))
                )
                self.product_table.setItem(
                    row,
                    5,
                    QTableWidgetItem(
                        "Hoạt động" if product.status == "active" else "Không hoạt động"
                    ),
                )
                creator_name = product.creator.name if product.creator else "N/A"
                self.product_table.setItem(row, 6, QTableWidgetItem(creator_name))
        except Exception as e:
            QMessageBox.critical(self, "Lỗi lọc sản phẩm", str(e))

    def load_products(self):
        self.filter_products()

    def add_product(self):
        dialog = ProductDialog(self)
        if dialog.exec():
            try:
                price = dialog.get_raw_price()
                stock = int(dialog.stock_input.text() or 0)
            except ValueError:
                QMessageBox.warning(self, "❌ Lỗi", "Giá và tồn kho phải là số.")
                return

            if not self.current_user or self.current_user.role not in [
                Role.admin,
                Role.staff,
            ]:
                QMessageBox.warning(
                    self, "❌ Lỗi", "Chỉ admin hoặc staff mới có thể tạo sản phẩm!"
                )
                return

            product = Product(
                name=dialog.name_input.text(),
                code=dialog.code_input.text(),
                category=dialog.category_input.currentText(),
                price=price,
                stock=stock,
                description=dialog.description_input.text(),
                image=dialog.image_input.text(),
                status=(
                    "active"
                    if dialog.status_input.currentText() == "Hoạt động"
                    else "inactive"
                ),
                created_by=self.current_user.id,  # Gán created_by
            )
            try:
                self.session.add(product)
                self.session.commit()
                self.filter_products()
                QMessageBox.information(
                    self, "✅ Thành công", "Thêm sản phẩm thành công!"
                )
            except IntegrityError:
                self.session.rollback()
                QMessageBox.warning(self, "❌ Lỗi", "Mã sản phẩm đã tồn tại!")
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Lỗi thêm sản phẩm", str(e))

    def edit_product(self):
        if not hasattr(self, "product_table") or not self.product_table:
            return
        selected = self.product_table.currentRow()
        if selected >= 0:
            product_id = int(self.product_table.item(selected, 0).text())
            product = self.session.query(Product).get(product_id)
            if not product:
                QMessageBox.warning(self, "❌ Lỗi", "Không tìm thấy sản phẩm!")
                return

            if (
                self.current_user.role == Role.staff
                and product.created_by != self.current_user.id
            ):
                QMessageBox.warning(
                    self, "❌ Lỗi", "Bạn chỉ có thể chỉnh sửa sản phẩm do bạn tạo!"
                )
                return

            dialog = ProductDialog(self, product)
            if dialog.exec():
                try:
                    product.price = dialog.get_raw_price()
                    product.stock = int(dialog.stock_input.text() or 0)
                except ValueError:
                    QMessageBox.warning(self, "❌ Lỗi", "Giá và tồn kho phải là số.")
                    return

                product.name = dialog.name_input.text()
                product.code = dialog.code_input.text()
                product.category = dialog.category_input.currentText()
                product.description = dialog.description_input.text()
                product.image = dialog.image_input.text()
                product.status = (
                    "active"
                    if dialog.status_input.currentText() == "Hoạt động"
                    else "inactive"
                )
                # Không thay đổi created_by khi chỉnh sửa
                try:
                    self.session.commit()
                    self.filter_products()
                    QMessageBox.information(
                        self, "✅ Thành công", "Cập nhật sản phẩm thành công!"
                    )
                except IntegrityError:
                    self.session.rollback()
                    QMessageBox.warning(
                        self,
                        "❌ Lỗi",
                        "Mã sản phẩm có thể đã tồn tại cho sản phẩm khác.",
                    )
                except Exception as e:
                    self.session.rollback()
                    QMessageBox.critical(self, "Lỗi cập nhật sản phẩm", str(e))
        else:
            QMessageBox.warning(self, "❌ Lỗi", "Vui lòng chọn sản phẩm để sửa!")

    def delete_product(self):
        if not hasattr(self, "product_table") or not self.product_table:
            return
        selected = self.product_table.currentRow()
        if selected >= 0:
            product_id = int(self.product_table.item(selected, 0).text())
            product = self.session.query(Product).get(product_id)
            if not product:
                QMessageBox.warning(self, "❌ Lỗi", "Không tìm thấy sản phẩm!")
                return

            reply = QMessageBox.question(
                self,
                "⚠️ Xác nhận",
                f"Bạn có chắc muốn xóa sản phẩm '{product.name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    self.session.delete(product)
                    self.session.commit()
                    self.filter_products()
                    QMessageBox.information(
                        self, "✅ Thành công", "Xóa sản phẩm thành công!"
                    )
                except Exception as e:
                    self.session.rollback()
                    QMessageBox.critical(self, "Lỗi xóa sản phẩm", str(e))
        else:
            QMessageBox.warning(self, "❌ Lỗi", "Vui lòng chọn sản phẩm để xóa!")

    def filter_orders(self):
        if not hasattr(self, "order_table") or not self.order_table:
            return
        try:
            search_text = self.order_search_input.text().lower().strip()
            status_filter = self.order_status_filter.currentText()

            # Truy vấn cơ bản
            query = self.session.query(Order)

            # Nếu người dùng là nhân viên (Staff), chỉ hiển thị đơn hàng của họ
            if self.current_user.role == Role.staff:
                query = query.filter(Order.staff_id == self.current_user.id)

            if status_filter != "Tất cả trạng thái":
                query = query.filter_by(status=OrderStatus[status_filter])

            # Lấy tất cả đơn hàng trước
            orders = query.all()

            # Lọc đơn hàng theo search_text
            filtered_orders = []
            for order in orders:
                # Kiểm tra mã đơn hàng
                if search_text and order.code and search_text in order.code.lower():
                    filtered_orders.append(order)
                    continue

                # Kiểm tra tên khách hàng
                customer_name = (
                    order.customer.name
                    if order.customer and order.customer.name
                    else ""
                )
                if (
                    search_text
                    and customer_name
                    and search_text in customer_name.lower()
                ):
                    filtered_orders.append(order)
                    continue

                # Kiểm tra tên sản phẩm
                order_items = order.items
                product_names = []
                product_images = []
                for item in order_items:
                    product = self.session.query(Product).get(item.product_id)
                    if product:
                        product_names.append(product.name.lower())
                        product_images.append(product.image or "Không có hình ảnh")
                if search_text and any(search_text in name for name in product_names):
                    filtered_orders.append(order)
                    continue

                # Kiểm tra giá tổng (total_amount / 1000)
                total_amount_str = str(int((order.total_amount or 0) / 1000))
                if search_text and search_text in total_amount_str:
                    filtered_orders.append(order)
                    continue

                # Nếu không có search_text, hiển thị tất cả đơn hàng (đã lọc theo staff_id nếu là Staff)
                if not search_text:
                    filtered_orders.append(order)

            # Hiển thị kết quả lên bảng
            self.order_table.setRowCount(len(filtered_orders))
            for row, order in enumerate(filtered_orders):
                self.order_table.setItem(row, 0, QTableWidgetItem(str(order.id)))
                self.order_table.setItem(row, 1, QTableWidgetItem(order.code or ""))
                customer_name = (
                    order.customer.name
                    if order.customer and order.customer.name
                    else "N/A"
                )
                self.order_table.setItem(row, 2, QTableWidgetItem(customer_name))

                # Lấy danh sách sản phẩm từ OrderItem
                order_items = order.items
                product_names = []
                product_images = []
                for item in order_items:
                    product = self.session.query(Product).get(item.product_id)
                    if product:
                        product_names.append(product.name)
                        product_images.append(product.image or "Không có hình ảnh")

                # Hiển thị tên sản phẩm
                product_names_str = ", ".join(product_names) if product_names else "N/A"
                self.order_table.setItem(row, 3, QTableWidgetItem(product_names_str))

                # Hiển thị hình ảnh (thu nhỏ xuống 25x25)
                image_path = (
                    product_images[0] if product_images else "Không có hình ảnh"
                )
                image_label = QLabel()
                image_label.setCursor(Qt.CursorShape.PointingHandCursor)
                if image_path != "Không có hình ảnh" and os.path.exists(image_path):
                    pixmap = QPixmap(image_path).scaled(
                        25, 25, Qt.AspectRatioMode.KeepAspectRatio
                    )
                    image_label.setPixmap(pixmap)
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                    def create_image_click_handler(path):
                        return lambda event: self.show_large_image(path)

                    image_label.mousePressEvent = create_image_click_handler(image_path)
                else:
                    image_label.setText("N/A")
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.order_table.setCellWidget(row, 4, image_label)

                self.order_table.setItem(row, 5, QTableWidgetItem(order.status.value))
                self.order_table.setItem(
                    row, 6, QTableWidgetItem(format_price(order.total_amount or 0))
                )
        except Exception as e:
            QMessageBox.critical(self, "Lỗi lọc đơn hàng", str(e))

    def load_orders(self):
        self.filter_orders()

    def filter_customer_orders(self):
        if not hasattr(self, "customer_order_table") or not self.customer_order_table:
            return
        if not self.current_user:
            return
        try:
            search_text = self.customer_order_search_input.text().lower().strip()
            status_filter = self.customer_order_status_filter.currentText()

            query = self.session.query(Order).filter_by(
                customer_id=self.current_user.id
            )
            if status_filter != "Tất cả trạng thái":
                query = query.filter_by(status=OrderStatus[status_filter])

            orders = query.all()
            filtered_orders = []
            for order in orders:
                if search_text and order.code and search_text in order.code.lower():
                    filtered_orders.append(order)
                    continue
                order_items = order.items
                product_names = []
                product_images = []
                for item in order_items:
                    product = self.session.query(Product).get(item.product_id)
                    if product:
                        product_names.append(product.name.lower())
                        product_images.append(product.image or "Không có hình ảnh")
                if search_text and any(search_text in name for name in product_names):
                    filtered_orders.append(order)
                    continue
                total_amount_str = str(int((order.total_amount or 0) / 1000))
                if search_text and search_text in total_amount_str:
                    filtered_orders.append(order)
                    continue
                if not search_text:
                    filtered_orders = orders

            self.customer_order_table.setColumnCount(7)
            self.customer_order_table.setHorizontalHeaderLabels(
                [
                    "ID",
                    "Mã",
                    "Tên sản phẩm",
                    "Hình ảnh",
                    "Trạng thái",
                    "Tổng tiền",
                    "Bản đồ",
                ]
            )
            self.customer_order_table.setRowCount(len(filtered_orders))
            for row, order in enumerate(filtered_orders):
                self.customer_order_table.setItem(
                    row, 0, QTableWidgetItem(str(order.id))
                )
                self.customer_order_table.setItem(
                    row, 1, QTableWidgetItem(order.code or "")
                )
                product_names_str = (
                    ", ".join([item.product.name for item in order.items])
                    if order.items
                    else "N/A"
                )
                self.customer_order_table.setItem(
                    row, 2, QTableWidgetItem(product_names_str)
                )

                image_path = (
                    order.items[0].product.image
                    if order.items and order.items[0].product.image
                    else "Không có hình ảnh"
                )
                image_label = QLabel()
                image_label.setCursor(Qt.CursorShape.PointingHandCursor)
                if image_path != "Không có hình ảnh" and os.path.exists(image_path):
                    pixmap = QPixmap(image_path).scaled(
                        25, 25, Qt.AspectRatioMode.KeepAspectRatio
                    )
                    image_label.setPixmap(pixmap)
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    image_label.mousePressEvent = (
                        lambda event, path=image_path: self.show_large_image(path)
                    )
                else:
                    image_label.setText("N/A")
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.customer_order_table.setCellWidget(row, 3, image_label)

                self.customer_order_table.setItem(
                    row, 4, QTableWidgetItem(order.status.value)
                )
                self.customer_order_table.setItem(
                    row, 5, QTableWidgetItem(format_price(order.total_amount or 0))
                )

                # Chỉ hiển thị nút "Xem bản đồ" khi trạng thái là completed và có tọa độ
                if (
                    order.status == OrderStatus.completed
                    and order.latitude
                    and order.longitude
                ):
                    map_button = QPushButton("🗺️")
                    map_button.setFixedSize(30, 30)
                    map_button.setStyleSheet(
                        """
                        QPushButton {
                            background: #e0e7ff;
                            border: 1px solid #93c5fd;
                            border-radius: 4px;
                        }
                        QPushButton:hover {
                            background: #c7d2fe;
                        }
                        """
                    )
                    map_button.clicked.connect(
                        lambda checked, o=order: self.show_order_map(o)
                    )
                    self.customer_order_table.setCellWidget(row, 6, map_button)
                else:
                    self.customer_order_table.setItem(row, 6, QTableWidgetItem("N/A"))

            self.customer_order_table.setColumnWidth(3, 50)
            self.customer_order_table.setColumnWidth(6, 50)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi lọc đơn hàng của bạn", str(e))

    def show_order_map(self, order):
        dialog = OrderTrackingMapDialog(order, self)
        dialog.exec()

    def show_large_image(self, image_path):
        if image_path != "Không có hình ảnh" and os.path.exists(image_path):
            dialog = ImageViewerDialog(image_path, self)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy hình ảnh để hiển thị!")

    def load_customer_orders(self):
        self.filter_customer_orders()

    def create_revenue_by_category_chart(self, categories, revenues):
        web_view = QWebEngineView()
        web_view.setFixedHeight(400)

        try:
            with open("chart_template.html", "r", encoding="utf-8") as f:
                html_content = f.read()
        except FileNotFoundError as e:
            QMessageBox.critical(
                self, "Lỗi", f"Không tìm thấy tệp chart_template.html: {str(e)}"
            )
            return web_view

        web_view.setHtml(html_content)

        def on_load_finished(ok):
            if ok:
                print(
                    "HTML tải thành công, gọi renderChart cho doanh thu theo danh mục"
                )
                web_view.page().runJavaScript(
                    f"renderChart('bar', {json.dumps(categories)}, {json.dumps(revenues)}, 'Doanh thu (nghìn VNĐ)');",
                    lambda result: print("Kết quả renderChart:", result),
                )
            else:
                print("Lỗi khi tải HTML cho biểu đồ doanh thu theo danh mục")
                QMessageBox.critical(
                    self, "Lỗi", "Không thể tải biểu đồ doanh thu theo danh mục."
                )

        def console_message(level, message, line_number, source_id):
            print(f"JavaScript Console (Line {line_number}): {message}")

        web_view.page().javaScriptConsoleMessage = console_message
        web_view.loadFinished.connect(on_load_finished)
        return web_view

    def create_revenue_by_month_chart(self, months, revenues):
        web_view = QWebEngineView()
        web_view.setFixedHeight(400)

        try:
            with open("chart_template.html", "r", encoding="utf-8") as f:
                html_content = f.read()
        except FileNotFoundError as e:
            QMessageBox.critical(
                self, "Lỗi", f"Không tìm thấy tệp chart_template.html: {str(e)}"
            )
            return web_view

        web_view.setHtml(html_content)

        def on_load_finished(ok):
            if ok:
                print("HTML tải thành công, gọi renderChart cho doanh thu theo tháng")
                web_view.page().runJavaScript(
                    f"renderChart('line', {json.dumps(months)}, {json.dumps(revenues)}, 'Doanh thu (nghìn VNĐ)');",
                    lambda result: print("Kết quả renderChart:", result),
                )
            else:
                print("Lỗi khi tải HTML cho biểu đồ doanh thu theo tháng")
                QMessageBox.critical(
                    self, "Lỗi", "Không thể tải biểu đồ doanh thu theo tháng."
                )

        def console_message(level, message, line_number, source_id):
            print(f"JavaScript Console (Line {line_number}): {message}")

        web_view.page().javaScriptConsoleMessage = console_message
        web_view.loadFinished.connect(on_load_finished)
        return web_view

    def create_order_status_chart(self, statuses, counts):
        web_view = QWebEngineView()
        web_view.setFixedHeight(400)

        try:
            with open("chart_template.html", "r", encoding="utf-8") as f:
                html_content = f.read()
        except FileNotFoundError as e:
            QMessageBox.critical(
                self, "Lỗi", f"Không tìm thấy tệp chart_template.html: {str(e)}"
            )
            return web_view

        web_view.setHtml(html_content)

        def on_load_finished(ok):
            if ok:
                print("HTML tải thành công, gọi renderChart cho trạng thái đơn hàng")
                web_view.page().runJavaScript(
                    f"renderChart('pie', {json.dumps(statuses)}, {json.dumps(counts)}, 'Số đơn hàng');",
                    lambda result: print("Kết quả renderChart:", result),
                )
            else:
                print("Lỗi khi tải HTML cho biểu đồ trạng thái đơn hàng")
                QMessageBox.critical(
                    self, "Lỗi", "Không thể tải biểu đồ trạng thái đơn hàng."
                )

        def console_message(level, message, line_number, source_id):
            print(f"JavaScript Console (Line {line_number}): {message}")

        web_view.page().javaScriptConsoleMessage = console_message
        web_view.loadFinished.connect(on_load_finished)
        return web_view

    def export_users(self):
        users = self.session.query(User).all()
        data = [
            {
                "ID": u.id,
                "Tên đăng nhập": u.username,
                "Tên": u.name or "",
                "Email": u.email or "",
                "Vai trò": u.role.value,
                "Trạng thái": (
                    "Hoạt động" if u.status == "active" else "Không hoạt động"
                ),
                "Số điện thoại": u.phone or "",
                "Địa chỉ": u.address or "",
            }
            for u in users
        ]
        filename, _ = QFileDialog.getSaveFileName(
            self, "Lưu file Excel", "users_export.xlsx", "Excel Files (*.xlsx)"
        )
        if filename:
            try:
                export_to_excel(data, filename, "Users")
                QMessageBox.information(
                    self, "Thành công", f"Đã xuất danh sách người dùng ra {filename}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi khi xuất file: {str(e)}")

    def export_products(self):
        try:
            # Truy vấn cơ bản
            query = self.session.query(Product)

            # Nếu người dùng là nhân viên (Staff), chỉ lấy sản phẩm của họ
            if self.current_user.role == Role.staff:
                query = query.filter(Product.created_by == self.current_user.id)

            products = query.all()
            data = [
                {
                    "ID": p.id,
                    "Tên": p.name,
                    "Mã": p.code,
                    "Danh mục": p.category or "",
                    "Giá (VNĐ)": format_price(p.price or 0),
                    "Tồn kho": p.stock or 0,
                    "Mô tả": p.description or "",
                    "Trạng thái": (
                        "Hoạt động" if p.status == "active" else "Không hoạt động"
                    ),
                }
                for p in products
            ]
            filename, _ = QFileDialog.getSaveFileName(
                self, "Lưu file Excel", "products_export.xlsx", "Excel Files (*.xlsx)"
            )
            if filename:
                export_to_excel(data, filename, "Products")
                QMessageBox.information(
                    self, "Thành công", f"Đã xuất danh sách sản phẩm ra {filename}"
                )
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi xuất file: {str(e)}")

    def export_orders(self):
        try:
            # Truy vấn cơ bản
            query = self.session.query(Order)

            # Nếu người dùng là nhân viên (Staff), chỉ lấy đơn hàng của họ
            if self.current_user.role == Role.staff:
                query = query.filter(Order.staff_id == self.current_user.id)

            orders = query.all()
            data = [
                {
                    "ID": o.id,
                    "Mã": o.code,
                    "Khách hàng": (
                        o.customer.name if o.customer and o.customer.name else "N/A"
                    ),
                    "Nhân viên": o.staff.name if o.staff and o.staff.name else "N/A",
                    "Ngày tạo": (
                        o.created_at.strftime("%Y-%m-%d %H:%M:%S")
                        if o.created_at
                        else ""
                    ),
                    "Tổng tiền (VNĐ)": format_price(o.total_amount or 0),
                    "Trạng thái": o.status.value,
                    "Phương thức thanh toán": o.payment_method or "",
                    "Phương thức vận chuyển": o.shipping_method or "",
                }
                for o in orders
            ]
            filename, _ = QFileDialog.getSaveFileName(
                self, "Lưu file Excel", "orders_export.xlsx", "Excel Files (*.xlsx)"
            )
            if filename:
                export_to_excel(data, filename, "Orders")
                QMessageBox.information(
                    self, "Thành công", f"Đã xuất danh sách đơn hàng ra {filename}"
                )
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi xuất file: {str(e)}")

    def export_customer_orders(self):
        if not self.current_user:
            return
        orders = (
            self.session.query(Order).filter_by(customer_id=self.current_user.id).all()
        )
        data = [
            {
                "ID": o.id,
                "Mã": o.code,
                "Ngày tạo": (
                    o.created_at.strftime("%Y-%m-%d %H:%M:%S") if o.created_at else ""
                ),
                "Tổng tiền (VNĐ)": format_price(o.total_amount or 0),
                "Trạng thái": o.status.value,
                "Phương thức thanh toán": o.payment_method or "",
                "Phương thức vận chuyển": o.shipping_method or "",
            }
            for o in orders
        ]
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu file Excel",
            "customer_orders_export.xlsx",
            "Excel Files (*.xlsx)",
        )
        if filename:
            try:
                export_to_excel(data, filename, "Customer_Orders")
                QMessageBox.information(
                    self, "Thành công", f"Đã xuất danh sách đơn hàng ra {filename}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi khi xuất file: {str(e)}")

    def export_statistics(self):
        try:
            # Nếu là nhân viên (Staff), truyền staff_id để lọc dữ liệu; nếu là Admin, không lọc
            staff_id = (
                self.current_user.id if self.current_user.role == Role.staff else None
            )

            # Thống kê doanh thu theo danh mục
            categories, revenues = get_revenue_by_category(self.session, staff_id)
            category_data = [
                {"Danh mục": cat, "Doanh thu (nghìn VNĐ)": rev}
                for cat, rev in zip(categories, revenues)
            ]

            # Thống kê doanh thu theo tháng
            months, monthly_revenues = get_revenue_by_month(self.session, staff_id)
            monthly_data = [
                {"Tháng": month, "Doanh thu (nghìn VNĐ)": rev}
                for month, rev in zip(months, monthly_revenues)
            ]

            # Thống kê trạng thái đơn hàng
            statuses, counts = get_order_status_distribution(self.session, staff_id)
            status_data = [
                {"Trạng thái": status, "Số lượng": count}
                for status, count in zip(statuses, counts)
            ]

            filename, _ = QFileDialog.getSaveFileName(
                self, "Lưu file Excel", "statistics_export.xlsx", "Excel Files (*.xlsx)"
            )
            if filename:
                with pd.ExcelWriter(filename, engine="openpyxl") as writer:
                    if category_data:
                        pd.DataFrame(category_data).to_excel(
                            writer, sheet_name="Revenue_by_Category", index=False
                        )
                    if monthly_data:
                        pd.DataFrame(monthly_data).to_excel(
                            writer, sheet_name="Revenue_by_Month", index=False
                        )
                    if status_data:
                        pd.DataFrame(status_data).to_excel(
                            writer, sheet_name="Order_Status", index=False
                        )
                QMessageBox.information(
                    self, "Thành công", f"Đã xuất thống kê ra {filename}"
                )
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi xuất file: {str(e)}")

    def add_order_for_customer_by_staff(self):
        # Kiểm tra nếu người dùng hiện tại không phải nhân viên
        if self.current_user.role != Role.staff:
            QMessageBox.warning(
                self, "Lỗi", "Chỉ nhân viên mới có thể tạo đơn hàng cho khách hàng!"
            )
            return

        # Kiểm tra xem có khách hàng nào trong cơ sở dữ liệu không
        customers = self.session.query(User).filter_by(role=Role.customer).all()
        if not customers:
            QMessageBox.warning(
                self, "Lỗi", "Không có khách hàng nào trong hệ thống để tạo đơn hàng!"
            )
            return

        # Mở dialog chọn khách hàng
        customer_dialog = SelectCustomerDialog(self, self.session)
        if customer_dialog.exec():
            customer_id = customer_dialog.get_selected_customer_id()
            if not customer_id:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một khách hàng!")
                return

            # Kiểm tra trạng thái khách hàng
            customer = self.session.query(User).get(customer_id)
            if customer.status != "active":
                QMessageBox.warning(self, "Lỗi", "Khách hàng này hiện không hoạt động!")
                return

            # Gọi phương thức add_order với customer_id
            self.add_order(created_by_staff=True, customer_id_for_staff=customer_id)

    def add_order(self, created_by_staff=False, customer_id_for_staff=None):
        if not self.current_user:
            print("Lỗi - Người dùng hiện tại là None")  # Log
            QMessageBox.warning(self, "Lỗi", "Không xác định được người dùng hiện tại.")
            return

        products = self.session.query(Product).filter_by(status="active").all()
        if not products:
            print("Lỗi - Không tìm thấy sản phẩm đang hoạt động")  # Log
            QMessageBox.warning(
                self, "Thông báo", "Hiện không có sản phẩm nào để tạo đơn hàng."
            )
            return

        dialog = OrderCreationDialog(self, self.session)
        if dialog.exec():
            if not dialog.validate_input():
                print("Xác thực thất bại trong dialog")  # Log
                return

            product = dialog.get_selected_product()
            quantity = dialog.get_quantity()

            print(
                f"Tạo đơn hàng - Sản phẩm: {product.name}, Số lượng: {quantity}, Người tạo: {product.created_by}"
            )  # Log

            # Lấy staff_id từ created_by của sản phẩm
            order_staff_id = product.created_by
            print(f"ID Nhân viên của đơn hàng: {order_staff_id}")  # Log

            order_code = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )
            order_customer_id = self.current_user.id

            if created_by_staff:
                if customer_id_for_staff:
                    order_customer_id = customer_id_for_staff
                else:
                    print(
                        "Lỗi - Không chọn khách hàng cho đơn hàng do nhân viên tạo"
                    )  # Log
                    QMessageBox.warning(
                        self, "Thông báo", "Vui lòng chọn khách hàng khi tạo đơn."
                    )
                    return

            print(
                f"Chi tiết đơn hàng - ID Khách hàng: {order_customer_id}, Tổng tiền: {product.price * quantity}"
            )  # Log

            total_amount = product.price * quantity
            order = Order(
                code=order_code,
                customer_id=order_customer_id,
                staff_id=order_staff_id,  # Sử dụng staff_id từ created_by của sản phẩm
                total_amount=total_amount,
                status=OrderStatus.new,
                payment_method="cash",
                shipping_method="standard",
            )
            try:
                self.session.add(order)
                self.session.flush()
                print(
                    f"Đơn hàng đã được tạo - ID Đơn hàng: {order.id}, Mã: {order.code}"
                )  # Log

                import requests
                import time

                customer = self.session.query(User).get(order_customer_id)
                customer_address = customer.address if customer else None

                if customer_address:
                    print(f"Đang lấy tọa độ cho địa chỉ: {customer_address}")  # Log
                    nominatim_url = f"https://nominatim.openstreetmap.org/search?q={customer_address}&format=json&limit=1"
                    headers = {
                        "User-Agent": "OrderManagementApp/1.0 (luuquan232003@gmail.com)"
                    }
                    try:
                        response = requests.get(nominatim_url, headers=headers).json()
                        time.sleep(1)
                        if response and len(response) > 0:
                            order.latitude = float(response[0]["lat"])
                            order.longitude = float(response[0]["lon"])
                            print(
                                f"Tọa độ đã lấy - Vĩ độ: {order.latitude}, Kinh độ: {order.longitude}"
                            )  # Log
                        else:
                            print("Cảnh báo - Không thể lấy tọa độ")  # Log
                            QMessageBox.warning(
                                self,
                                "Cảnh báo",
                                f"Không thể lấy tọa độ cho địa chỉ: {customer_address}",
                            )
                            order.latitude = None
                            order.longitude = None
                    except Exception as e:
                        print(f"Lỗi khi lấy tọa độ: {str(e)}")  # Log
                        QMessageBox.warning(
                            self, "Lỗi", f"Lỗi khi gọi Nominatim API: {str(e)}"
                        )
                        order.latitude = None
                        order.longitude = None
                else:
                    print(
                        f"Cảnh báo - Khách hàng {order_customer_id} không có địa chỉ"
                    )  # Log
                    QMessageBox.warning(
                        self,
                        "Cảnh báo",
                        f"Khách hàng {order_customer_id} không có địa chỉ.",
                    )
                    order.latitude = None
                    order.longitude = None

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.price,
                )
                self.session.add(order_item)
                product.stock -= quantity
                print(
                    f"Mục đơn hàng đã tạo - ID Đơn hàng: {order.id}, ID Sản phẩm: {product.id}, Tồn kho cập nhật: {product.stock}"
                )  # Log

                log = ActivityLog(
                    user_id=self.current_user.id,
                    action="create_order",
                    target=f"Order {order.code}",
                    details=f"Created new order with status {order.status.value} by staff_id {order_staff_id}",
                )
                self.session.add(log)
                print(f"Nhật ký hoạt động đã tạo cho Đơn hàng {order.code}")  # Log

                self.session.commit()
                print("Đơn hàng đã được lưu thành công")  # Log

                customer_email = order.customer.email if order.customer else None
                if customer_email:
                    subject = f"Thông báo: Đơn hàng {order.code} đã được tạo"
                    content = f"""
                    <h3>Thông báo tạo đơn hàng</h3>
                    <p>Xin chào {order.customer.name},</p>
                    <p>Đơn hàng của bạn với mã <strong>{order.code}</strong> đã được tạo thành công.</p>
                    <p><strong>Trạng thái:</strong> {order.status.value}<br>
                    <strong>Tổng tiền:</strong> {format_price(order.total_amount)}</p>
                    <p>Cảm ơn bạn đã mua sắm tại cửa hàng của chúng tôi!</p>
                    """
                    send_email_notification(customer_email, subject, content)
                    print(f"Email thông báo đã gửi tới {customer_email}")  # Log

                if self.current_user.role == Role.customer:
                    self.filter_customer_orders()
                else:
                    self.filter_orders()
                QMessageBox.information(
                    self, "✅ Thành công", f"Tạo đơn hàng '{order_code}' thành công!"
                )
            except Exception as e:
                self.session.rollback()
                print(f"Lỗi khi tạo đơn hàng: {str(e)}")  # Log
                QMessageBox.critical(self, "Lỗi tạo đơn hàng", str(e))

    def edit_order(self):
        if not hasattr(self, "order_table") or not self.order_table:
            return
        selected = self.order_table.currentRow()
        if selected >= 0:
            order_id = int(self.order_table.item(selected, 0).text())
            order = self.session.query(Order).get(order_id)
            if not order:
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy đơn hàng!")
                return

            # Kiểm tra quyền chỉnh sửa
            if (
                self.current_user.role == Role.staff
                and order.staff_id != self.current_user.id
            ):
                QMessageBox.warning(
                    self, "Lỗi", "Bạn không có quyền chỉnh sửa đơn hàng này!"
                )
                return

            dialog = QDialog(self)
            dialog.setWindowTitle("📝 Cập nhật trạng thái đơn hàng")
            dialog.setFixedSize(350, 200)

            layout = QFormLayout(dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)

            status_label = QLabel("Trạng thái mới:")
            status_input = QComboBox()
            status_input.addItems([s.value for s in OrderStatus])
            status_input.setCurrentText(order.status.value)

            layout.addRow(status_label, status_input)

            save_button = QPushButton("💾 Lưu")
            save_button.setObjectName("addButton")
            save_button.clicked.connect(dialog.accept)
            layout.addWidget(save_button)

            if dialog.exec():
                try:
                    old_status = order.status.value
                    new_status_value = status_input.currentText()
                    order.status = OrderStatus[new_status_value]
                    if self.current_user.role != Role.customer:
                        order.staff_id = self.current_user.id

                    # Lưu tọa độ khi trạng thái là "shipping" hoặc "completed"
                    if new_status_value in [
                        OrderStatus.shipping.value,
                        OrderStatus.completed.value,
                    ]:
                        import requests

                        customer = self.session.query(User).get(order.customer_id)
                        customer_address = customer.address if customer else None

                        if customer_address:
                            # Gọi Nominatim API để lấy tọa độ
                            nominatim_url = f"https://nominatim.openstreetmap.org/search?q={customer_address}&format=json&limit=1"
                            headers = {
                                "User-Agent": "OrderManagementApp/1.0 (your_email@example.com)"  # Thay bằng email của bạn
                            }
                            response = requests.get(
                                nominatim_url, headers=headers
                            ).json()
                            time.sleep(1)  # Tuân thủ giới hạn 1 yêu cầu/giây
                            if response and len(response) > 0:
                                order.latitude = float(response[0]["lat"])
                                order.longitude = float(response[0]["lon"])
                            else:
                                QMessageBox.warning(
                                    self,
                                    "Lỗi",
                                    "Không thể lấy tọa độ từ địa chỉ khách hàng!",
                                )
                                order.latitude = None
                                order.longitude = None
                        else:
                            QMessageBox.warning(
                                self, "Lỗi", "Khách hàng không có địa chỉ!"
                            )
                            order.latitude = None
                            order.longitude = None

                    # Ghi log hành động
                    log = ActivityLog(
                        user_id=self.current_user.id,
                        action="update_order_status",
                        target=f"Order {order.code}",
                        details=f"Changed status from {old_status} to {new_status_value}",
                    )
                    self.session.add(log)

                    self.session.commit()

                    # Gửi email thông báo
                    should_send_email = False
                    customer_email = order.customer.email if order.customer else None
                    if (
                        self.current_user.role == Role.customer
                        and order.customer_id == self.current_user.id
                    ):
                        should_send_email = True
                    elif (
                        self.current_user.role == Role.staff
                        and order.staff_id == self.current_user.id
                    ):
                        should_send_email = True

                    if should_send_email and customer_email:
                        subject = (
                            f"Thông báo: Trạng thái đơn hàng {order.code} đã thay đổi"
                        )
                        content = f"""
                        <h3>Thông báo thay đổi trạng thái đơn hàng</h3>
                        <p>Xin chào {order.customer.name},</p>
                        <p>Đơn hàng của bạn với mã <strong>{order.code}</strong> đã được cập nhật trạng thái:</p>
                        <p><strong>Từ:</strong> {old_status}<br>
                        <strong>Đến:</strong> {new_status_value}</p>
                        <p>Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi!</p>
                        """
                        send_email_notification(customer_email, subject, content)

                    if (
                        new_status_value == OrderStatus.completed.value
                        and should_send_email
                        and customer_email
                    ):
                        subject = f"Đơn hàng {order.code} đã hoàn thành"
                        content = f"""
                        <h3>Đơn hàng hoàn thành</h3>
                        <p>Xin chào {order.customer.name},</p>
                        <p>Đơn hàng của bạn với mã <strong>{order.code}</strong> đã hoàn thành.</p>
                        <p>Tổng tiền: {format_price(order.total_amount)}</p>
                        <p>Cảm ơn bạn đã mua sắm tại cửa hàng của chúng tôi!</p>
                        """
                        send_email_notification(customer_email, subject, content)

                    self.filter_orders()
                    QMessageBox.information(
                        self, "✅ Thành công", "Cập nhật trạng thái thành công!"
                    )
                except KeyError:
                    QMessageBox.warning(
                        self, "Lỗi", f"Trạng thái không hợp lệ: {new_status_value}"
                    )
                except Exception as e:
                    self.session.rollback()
                    QMessageBox.critical(self, "Lỗi cập nhật", str(e))
        else:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn đơn hàng để cập nhật!")

    def cancel_order(self):
        if not hasattr(self, "customer_order_table") or not self.customer_order_table:
            return
        selected = self.customer_order_table.currentRow()
        if selected >= 0:
            order_id = int(self.customer_order_table.item(selected, 0).text())
            order = self.session.query(Order).get(order_id)
            if not order:
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy đơn hàng!")
                return

            if order.status == OrderStatus.new:
                reply = QMessageBox.question(
                    self,
                    "⚠️ Xác nhận",
                    f"Bạn có chắc muốn hủy đơn hàng '{order.code}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    try:
                        old_status = order.status.value  # Lưu trạng thái cũ
                        order.status = OrderStatus.canceled
                        for item in order.items:
                            product = self.session.query(Product).get(item.product_id)
                            if product:
                                product.stock += item.quantity
                        self.session.commit()

                        # Gửi email thông báo khi hủy đơn hàng
                        customer_email = (
                            order.customer.email if order.customer else None
                        )
                        if customer_email:
                            subject = f"Thông báo: Đơn hàng {order.code} đã bị hủy"
                            content = f"""
                            <h3>Thông báo hủy đơn hàng</h3>
                            <p>Xin chào {order.customer.name},</p>
                            <p>Đơn hàng của bạn với mã <strong>{order.code}</strong> đã bị hủy.</p>
                            <p><strong>Trạng thái cũ:</strong> {old_status}<br>
                               <strong>Trạng thái mới:</strong> {OrderStatus.canceled.value}</p>
                            <p>Nếu bạn có thắc mắc, vui lòng liên hệ với chúng tôi.</p>
                            """
                            send_email_notification(customer_email, subject, content)

                        self.filter_customer_orders()
                        QMessageBox.information(
                            self, "✅ Thành công", "Hủy đơn hàng thành công."
                        )
                    except Exception as e:
                        self.session.rollback()
                        QMessageBox.critical(self, "Lỗi hủy đơn hàng", str(e))
            else:
                QMessageBox.warning(
                    self,
                    "Thông báo",
                    f"Không thể hủy đơn hàng ở trạng thái '{order.status.value}'.",
                )
        else:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn đơn hàng để hủy!")

    def show_user_profile(self, event):
        if not self.current_user:
            QMessageBox.warning(self, "Lỗi", "Không xác định được người dùng hiện tại.")
            return

        dialog = UserProfileDialog(self, self.current_user, self.session)
        if dialog.exec():
            # Cập nhật lại nhãn thông tin người dùng sau khi chỉnh sửa
            self.user_info_label.setText(
                f"👤 {self.current_user.name} ({self.current_user.role.value})"
            )

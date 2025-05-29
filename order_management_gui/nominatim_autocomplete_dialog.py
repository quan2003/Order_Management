from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QMessageBox,
    QListWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal
import requests
import json


class NominatimAutocompleteDialog(QDialog):
    address_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🌍 Chọn địa chỉ")
        self.setFixedSize(400, 300)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Nhãn hướng dẫn
        self.label = QLabel("Nhập địa chỉ và nhấn Tìm kiếm:")
        self.layout.addWidget(self.label)

        # Trường nhập địa chỉ
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Nhập địa chỉ (VD: Hà Nội, Việt Nam)...")
        self.layout.addWidget(self.address_input)

        # Nút tìm kiếm
        self.search_button = QPushButton("🔍 Tìm kiếm")
        self.search_button.setObjectName("addButton")
        self.search_button.clicked.connect(self.search_addresses)
        self.layout.addWidget(self.search_button)

        # Danh sách kết quả
        self.result_list = QListWidget()
        self.result_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.result_list.itemClicked.connect(self.on_item_clicked)
        # Áp dụng stylesheet cho danh sách kết quả: chữ trắng, background tối
        self.result_list.setStyleSheet(
            """
            QListWidget {
                background-color: #2c3e50;  /* Màu nền tối */
                color: white;  /* Chữ trắng */
                border: 1px solid #e1e5e9;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #1a73e8;  /* Màu nền khi chọn */
                color: white;
            }
            QListWidget::item:hover {
                background-color: #34495e;  /* Màu nền khi di chuột qua */
            }
        """
        )
        self.layout.addWidget(self.result_list)

        # Nút chọn và đóng
        self.select_button = QPushButton("✅ Chọn")
        self.select_button.setObjectName("addButton")
        self.select_button.clicked.connect(self.accept)
        self.close_button = QPushButton("🔙 Đóng")
        self.close_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.close_button)
        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)

    def search_addresses(self):
        text = self.address_input.text().strip()
        if not text or len(text) < 3:
            QMessageBox.warning(
                self, "Thông báo", "Vui lòng nhập ít nhất 3 ký tự để tìm kiếm!"
            )
            return

        try:
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": text,
                    "format": "json",
                    "addressdetails": 1,
                    "countrycodes": "vn",  # Giới hạn ở Việt Nam
                    "limit": 10,  # Lấy tối đa 10 kết quả
                },
                headers={"User-Agent": "MyQtOrderManagementApp/1.0"},
                timeout=2,
            )
            response.raise_for_status()
            data = response.json()
            self.result_list.clear()
            if data:
                for item in data:
                    self.result_list.addItem(item["display_name"])
            else:
                self.result_list.addItem("Không tìm thấy địa chỉ phù hợp.")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tìm kiếm địa chỉ: {str(e)}")

    def on_item_clicked(self, item):
        self.address_input.setText(item.text())

    def accept(self):
        address = self.address_input.text().strip()
        if address:
            self.address_selected.emit(address)
            super().accept()
        else:
            QMessageBox.information(
                self, "Thông báo", "Vui lòng nhập hoặc chọn một địa chỉ!"
            )

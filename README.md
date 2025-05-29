# Hệ thống Quản lý Đơn hàng

Đây là ứng dụng quản lý đơn hàng được xây dựng bằng Python và PyQt6, hỗ trợ quản lý người dùng, sản phẩm, đơn hàng và thống kê doanh thu. Ứng dụng sử dụng PostgreSQL làm cơ sở dữ liệu và tích hợp các dịch vụ như SendGrid (gửi email) và Nominatim API (theo dõi bản đồ).

## Tính năng
- **Quản lý người dùng**: Thêm, sửa, xóa người dùng (admin, nhân viên, khách hàng).
- **Quản lý sản phẩm**: Tạo, cập nhật, xóa sản phẩm với hình ảnh và thông tin chi tiết.
- **Quản lý đơn hàng**: Tạo đơn hàng, cập nhật trạng thái, hủy đơn, theo dõi đơn hàng trên bản đồ.
- **Thống kê**: Biểu đồ doanh thu theo danh mục, tháng và phân bố trạng thái đơn hàng.
- **Thông báo email**: Gửi email thông báo khi tạo, cập nhật hoặc hủy đơn hàng.
- **Giao diện thân thiện**: Sử dụng PyQt6 với thiết kế hiện đại.

## Yêu cầu hệ thống
- Hệ điều hành: Windows, macOS, hoặc Linux.
- Python 3.8 trở lên.
- PostgreSQL 12 trở lên.
- Tài khoản SendGrid để gửi email (tùy chọn).
- Kết nối internet (để sử dụng Nominatim API và SendGrid).

## Hướng dẫn cài đặt và chạy ứng dụng

### 1. Tải mã nguồn
1. Cài đặt Git:
   - Windows: Tải Git từ [git-scm.com](https://git-scm.com/downloads) và cài đặt.
   - macOS: Chạy `brew install git` (nếu có Homebrew) hoặc cài từ [git-scm.com](https://git-scm.com/downloads).
   - Linux: Chạy `sudo apt install git` (Ubuntu/Debian) hoặc `sudo yum install git` (CentOS).

2. Clone repository từ GitHub:
   ```bash
   git clone https://github.com/quan2003/Order_Management.git
   ```

3. Di chuyển vào thư mục dự án:
   ```bash
   cd Order_Management
   ```

### 2. Cài đặt môi trường Python
1. Cài đặt Python 3.8+:
   - Tải Python từ [python.org](https://www.python.org/downloads/).
   - Khi cài đặt trên Windows, chọn **Add Python to PATH**.
   - Kiểm tra Python đã cài đặt:
     ```bash
     python --version
     ```

2. Tạo môi trường ảo:
   ```bash
   python -m venv venv
   ```

3. Kích hoạt môi trường ảo:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

   Khi kích hoạt thành công, bạn sẽ thấy `(venv)` trước dấu nhắc lệnh.

### 3. Cài đặt các thư viện cần thiết
1. Cài đặt các thư viện được liệt kê trong `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

   Nếu file `requirements.txt` chưa có, bạn có thể cài đặt các thư viện thủ công:
   ```bash
   pip install PyQt6 SQLAlchemy psycopg2-binary bcrypt python-dotenv pandas openpyxl sendgrid requests
   ```

### 4. Cài đặt và cấu hình PostgreSQL
1. Cài đặt PostgreSQL:
   - Windows: Tải từ [postgresql.org](https://www.postgresql.org/download/windows/) và cài đặt.
   - macOS: Chạy `brew install postgresql` (nếu có Homebrew).
   - Linux: Chạy `sudo apt install postgresql postgresql-contrib` (Ubuntu/Debian).

2. Khởi động PostgreSQL:
   - Windows: PostgreSQL tự động chạy sau khi cài đặt (hoặc mở pgAdmin).
   - macOS/Linux: Chạy:
     ```bash
     sudo service postgresql start
     ```

3. Tạo cơ sở dữ liệu:
   - Mở terminal hoặc pgAdmin và đăng nhập vào PostgreSQL (mặc định user là `postgres`):
     ```bash
     psql -U postgres
     ```
   - Tạo database:
     ```sql
     CREATE DATABASE order_management;
     ```
   - Thoát:
     ```sql
     \q
     ```

4. Cấu hình kết nối cơ sở dữ liệu:
   - Mở file `database.py` trong thư mục dự án.
   - Cập nhật `DATABASE_URL` để khớp với thông tin PostgreSQL của bạn:
     ```python
     DATABASE_URL = "postgresql://postgres:your_password@localhost:5432/order_management"
     ```
     Thay `your_password` bằng mật khẩu PostgreSQL của bạn.

### 5. Cấu hình SendGrid (tùy chọn)
Nếu muốn sử dụng tính năng gửi email, bạn cần tài khoản SendGrid:

1. Đăng ký tài khoản tại [sendgrid.com](https://sendgrid.com/).
2. Tạo API Key:
   - Vào **Settings** > **API Keys** > **Create API Key**.
   - Chọn quyền **Full Access** hoặc **Restricted Access** (bao gồm quyền gửi mail).
   - Sao chép API Key.

3. Tạo file `.env` trong thư mục gốc của dự án:
   ```bash
   touch .env
   ```

4. Thêm các thông tin sau vào file `.env`:
   ```
   SENDGRID_API_KEY=your_sendgrid_api_key
   FROM_EMAIL=your_email@example.com
   ```
   - Thay `your_sendgrid_api_key` bằng API Key từ SendGrid.
   - Thay `your_email@example.com` bằng email của bạn.

### 6. Tạo tài khoản admin mặc định
1. Chạy lệnh để tạo tài khoản admin:
   ```bash
   python -c "from database import create_default_admin; create_default_admin()"
   ```

2. Tài khoản admin mặc định:
   - Tên đăng nhập: `admin`
   - Mật khẩu: `admin`
   - Bạn có thể đăng nhập và thay đổi mật khẩu sau khi chạy ứng dụng.

### 7. Chạy ứng dụng
1. Đảm bảo môi trường ảo đang được kích hoạt:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

2. Chạy file chính:
   ```bash
   python main.py
   ```

3. Đăng nhập:
   - Sử dụng tài khoản admin (`admin`/`admin`) hoặc tạo tài khoản mới qua giao diện đăng ký.

### 8. Sử dụng ứng dụng
- **Admin**: Quản lý người dùng, sản phẩm, đơn hàng và xem thống kê.
- **Nhân viên (Staff)**: Quản lý sản phẩm, tạo đơn hàng cho khách hàng, xem thống kê cá nhân.
- **Khách hàng (Customer)**: Tạo đơn hàng, xem đơn hàng của mình, theo dõi bản đồ (khi đơn hoàn thành).

### Khắc phục sự cố
- **Lỗi kết nối PostgreSQL**:
  - Kiểm tra PostgreSQL đang chạy: `sudo service postgresql status`.
  - Đảm bảo `DATABASE_URL` trong `database.py` đúng.
- **Lỗi thư viện**:
  - Cài lại thư viện: `pip install -r requirements.txt`.
- **Lỗi gửi email**:
  - Kiểm tra API Key và email trong file `.env`.
  - Đảm bảo kết nối internet.
- **Lỗi Nominatim API**:
  - Kiểm tra kết nối internet.
  - Đảm bảo tuân thủ giới hạn 1 yêu cầu/giây của Nominatim.

### Góp ý
- Nếu gặp vấn đề, hãy tạo **Issue** trên GitHub.
- Đóng góp mã nguồn bằng cách gửi **Pull Request**.

### Tác giả
- **Quan Luu** ([quan2003](https://github.com/quan2003))
- Liên hệ: 0336440523

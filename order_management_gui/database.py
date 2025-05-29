from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Role
import bcrypt

# Kết nối đến cơ sở dữ liệu PostgreSQL
DATABASE_URL = "postgresql://postgres:quan2003@localhost:5432/order_management"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Tạo tất cả các bảng nếu chưa tồn tại
Base.metadata.create_all(engine)


def get_session():
    return Session()


def create_default_admin():
    session = get_session()
    try:
        admin_exists = session.query(User).filter_by(username="admin").first()
        if not admin_exists:
            hashed_password = bcrypt.hashpw(
                "admin".encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            admin = User(
                username="admin",
                password=hashed_password,
                email="admin@example.com",
                role=Role.admin,
                name="Admin User",
                status="active",
            )
            session.add(admin)
            session.commit()
            print("Tài khoản admin mặc định đã được tạo.")
        else:
            print("Tài khoản admin đã tồn tại.")
    except Exception as e:
        session.rollback()
        print(f"Lỗi khi tạo tài khoản admin mặc định: {str(e)}")
    finally:
        session.close()

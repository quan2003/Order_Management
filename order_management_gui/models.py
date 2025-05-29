from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Enum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime
import enum

Base = declarative_base()


class Role(enum.Enum):
    admin = "admin"
    staff = "staff"
    customer = "customer"


class OrderStatus(enum.Enum):
    new = "new"
    confirmed = "confirmed"
    shipping = "shipping"
    completed = "completed"
    canceled = "canceled"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String)
    role = Column(Enum(Role), default=Role.customer)
    name = Column(String)
    phone = Column(String)
    address = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="active")
    orders = relationship(
        "Order", foreign_keys="Order.customer_id", back_populates="customer"
    )
    handled_orders = relationship(
        "Order", foreign_keys="Order.staff_id", back_populates="staff"
    )
    created_products = relationship("Product", back_populates="creator")


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    category = Column(String)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    description = Column(String)
    image = Column(String)
    status = Column(String, default="active")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User", back_populates="created_products")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"))
    staff_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    delivery_date = Column(DateTime)
    total_amount = Column(Float, default=0.0)
    status = Column(Enum(OrderStatus), default=OrderStatus.new)
    payment_method = Column(String)
    shipping_method = Column(String)
    note = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    customer = relationship("User", foreign_keys=[customer_id], back_populates="orders")
    staff = relationship(
        "User", foreign_keys=[staff_id], back_populates="handled_orders"
    )
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    unit_price = Column(Float)
    order = relationship("Order", back_populates="items")
    product = relationship("Product")


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    target = Column(String)
    details = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User")

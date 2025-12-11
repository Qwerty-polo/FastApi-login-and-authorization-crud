from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class CategoryModel(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    dishes = relationship("DishModel", back_populates="cat", cascade="all, delete")

class DishModel(Base):
    __tablename__ = 'dish'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    category_id = Column(Integer,ForeignKey('category.id'))

    image_url = Column(String,nullable=True) #nulable means not nesesary column
    is_active = Column(Boolean, default=True)
    cat = relationship("CategoryModel", back_populates="dishes")


class UserModel(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)

    hashed_password = Column(String)
    orders = relationship("OrderModel", back_populates="user")

class OrderModel(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default='pending')
    total_price = Column(Float, default=0.0)

    user = relationship("UserModel", back_populates="orders")
    items = relationship("OrderItemModel", back_populates="order")



class OrderItemModel(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    dish_id = Column(Integer, ForeignKey('dish.id'))
    quantity = Column(Integer)
    price = Column(Float)

    order = relationship("OrderModel", back_populates="items")
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
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


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)

    hashed_password = Column(String)
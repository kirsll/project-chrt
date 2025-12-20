from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    password = Column(String(128), nullable=False)

    favorites = relationship("FavoriteCourse", back_populates="user", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    long_description = Column(Text, nullable=True)
    category = Column(String(64), nullable=False)
    duration = Column(String(64), nullable=False)
    level = Column(String(64), nullable=False)
    image_path = Column(String(255), nullable=False)
    materials_path = Column(String(255), nullable=True)
    is_popular = Column(Boolean, default=False)

    favorites = relationship("FavoriteCourse", back_populates="course", cascade="all, delete-orphan")


class FavoriteCourse(Base):
    __tablename__ = "favorite_courses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    user = relationship("User", back_populates="favorites")
    course = relationship("Course", back_populates="favorites")

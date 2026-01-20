from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

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


class CourseModule(Base):
    __tablename__ = "course_modules"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(200), nullable=False)
    order_index = Column(Integer, nullable=False, default=0)

    course = relationship("Course", backref="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey("course_modules.id"), nullable=False)
    title = Column(String(200), nullable=False)
    order_index = Column(Integer, nullable=False, default=0)
    content = Column(Text, nullable=True)

    module = relationship("CourseModule", back_populates="lessons")
    progresses = relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="lesson", cascade="all, delete-orphan")


class LessonProgress(Base):
    __tablename__ = "lesson_progresses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", backref="lesson_progresses")
    lesson = relationship("Lesson", back_populates="progresses")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    starter_code = Column(Text, nullable=True)
    checker_code = Column(Text, nullable=True)

    lesson = relationship("Lesson", back_populates="tasks")
    attempts = relationship("TaskAttempt", back_populates="task", cascade="all, delete-orphan")


class TaskAttempt(Base):
    __tablename__ = "task_attempts"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(Text, nullable=False)
    is_passed = Column(Boolean, default=False, nullable=False)
    output = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    task = relationship("Task", back_populates="attempts")
    user = relationship("User", backref="task_attempts")

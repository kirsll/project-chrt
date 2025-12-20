import eel
from pathlib import Path
import sys

from db import get_session, engine
from models import Base, User, Course, FavoriteCourse

CURRENT_USER_ID = None
if getattr(sys, "frozen", False):
    BASE_DIR = Path(getattr(sys, "_MEIPASS"))
else:
    BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR


def init_db():
    Base.metadata.create_all(bind=engine)
    session = get_session()
    try:
        if not session.query(Course).first():
            seed_courses(session)
            session.commit()
    finally:
        session.close()


def seed_courses(session):
    courses = [
        Course(
            id=1,
            title="Frontend‑разработчик с нуля",
            description="HTML, CSS, JavaScript и адаптивная вёрстка.",
            long_description="Подробная программа по основам веб‑разработки: семантическая вёрстка, адаптивный дизайн, работа с макетами, базовый JavaScript и подготовка портфолио‑проекта.",
            category="Программирование",
            duration="4,5 месяца",
            level="Начинающий",
            image_path="./static/photo1.jpg",
            materials_path="./static/materials/Course1.zip",
            is_popular=True,
        ),
        Course(
            id=2,
            title="UX/UI‑дизайн цифровых продуктов",
            description="Исследование пользователей, прототипирование и Figma.",
            long_description="Курс по созданию удобных интерфейсов: исследование аудитории, CJM, прототипы, дизайн‑системы и подготовка кейса в портфолио в Figma.",
            category="Дизайн",
            duration="3 месяца",
            level="Продолжающий",
            image_path="./static/photo3.jpg",
            materials_path="./static/materials/Course1.zip",
            is_popular=True,
        ),
        Course(
            id=3,
            title="Аналитик данных",
            description="SQL, BI‑инструменты и построение дашбордов для бизнеса.",
            long_description="Практический курс по аналитике данных: SQL, основы статистики, построение отчётов и дашбордов в BI‑инструментах и аналитический проект.",
            category="Аналитика",
            duration="4 месяца",
            level="Начинающий",
            image_path="./static/photo4.jpg",
            materials_path="./static/materials/Course1.zip",
            is_popular=True,
        ),
        Course(
            id=4,
            title="Backend на Python",
            description="Django, REST API и базы данных.",
            long_description="Практический курс по серверной разработке: Django, DRF, ORM, аутентификация, деплой и работа с БД.",
            category="Программирование",
            duration="5 месяцев",
            level="Продолжающий",
            image_path="./static/photo2.jpg",
            materials_path="./static/materials/Course1.zip",
            is_popular=False,
        ),
        Course(
            id=5,
            title="Digital‑маркетолог",
            description="Стратегия продвижения и аналитика кампаний.",
            long_description="Онлайн‑маркетинг от стратегии до аналитики: работа с каналами трафика, креативами, воронками и метриками эффективности.",
            category="Маркетинг",
            duration="3,5 месяца",
            level="Продолжающий",
            image_path="./static/photo5.jpg",
            materials_path="./static/materials/Course1.zip",
            is_popular=False,
        ),
        Course(
            id=6,
            title="Fullstack‑разработчик",
            description="Frontend + backend для комплексных веб‑приложений.",
            long_description="Комплексная программа: современный frontend и backend, работа с API, БД и деплоем боевого приложения.",
            category="Программирование",
            duration="6 месяцев",
            level="Интенсив",
            image_path="./static/photo6.jpg",
            materials_path="./static/materials/Course1.zip",
            is_popular=False,
        ),
    ]
    session.add_all(courses)


@eel.expose
def api_login(username: str, password: str):
    global CURRENT_USER_ID
    session = get_session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user is None:
            user = User(username=username, password=password)
            session.add(user)
            session.commit()
        elif user.password != password:
            return {"ok": False, "error": "Неверный пароль"}
        CURRENT_USER_ID = user.id
        return {"ok": True, "user": {"id": user.id, "username": user.username}}
    finally:
        session.close()


@eel.expose
def api_get_current_user():
    if CURRENT_USER_ID is None:
        return None
    session = get_session()
    try:
        user = session.get(User, CURRENT_USER_ID)
        if not user:
            return None
        fav_ids = {f.course_id for f in user.favorites}
        return {
            "id": user.id,
            "username": user.username,
            "password": user.password,
            "favorite_course_ids": list(fav_ids),
        }
    finally:
        session.close()


@eel.expose
def api_get_courses():
    session = get_session()
    try:
        courses = session.query(Course).all()
        result = []
        fav_ids = set()
        if CURRENT_USER_ID is not None:
            user = session.get(User, CURRENT_USER_ID)
            fav_ids = {f.course_id for f in user.favorites}
        for c in courses:
            result.append(
                {
                    "id": c.id,
                    "title": c.title,
                    "description": c.description,
                    "category": c.category,
                    "duration": c.duration,
                    "level": c.level,
                    "image_path": c.image_path,
                    "is_popular": c.is_popular,
                    "is_favorite": c.id in fav_ids,
                }
            )
        return result
    finally:
        session.close()


@eel.expose
def api_toggle_favorite(course_id: int):
    if CURRENT_USER_ID is None:
        return {"ok": False, "error": "Необходима авторизация"}
    session = get_session()
    try:
        fav = (
            session.query(FavoriteCourse)
            .filter_by(user_id=CURRENT_USER_ID, course_id=course_id)
            .first()
        )
        if fav:
            session.delete(fav)
            session.commit()
            return {"ok": True, "is_favorite": False}
        else:
            session.add(FavoriteCourse(user_id=CURRENT_USER_ID, course_id=course_id))
            session.commit()
            return {"ok": True, "is_favorite": True}
    finally:
        session.close()


@eel.expose
def api_get_course(course_id: int):
    session = get_session()
    try:
        course = session.get(Course, course_id)
        if not course:
            return None
        return {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "long_description": course.long_description,
            "category": course.category,
            "duration": course.duration,
            "level": course.level,
            "image_path": course.image_path,
            "materials_path": course.materials_path,
        }
    finally:
        session.close()


def main():
    init_db()
    eel.init(str(WEB_DIR))
    eel.start("index.html", size=(1200, 800), icon="static/logo.ico")


main()

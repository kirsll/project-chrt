import eel
from pathlib import Path
import sys
import subprocess
import textwrap
from tempfile import NamedTemporaryFile
from datetime import datetime

from db import get_session, engine
from models import (
    Base,
    User,
    Course,
    FavoriteCourse,
    CourseModule,
    Lesson,
    LessonProgress,
    Task,
    TaskAttempt,
)

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

    # Модули для всех курсов
    modules = [
        # Frontend‑разработчик с нуля (course_id=1)
        CourseModule(id=1, course_id=1, title="Основы HTML и верстки", order_index=1),
        CourseModule(id=2, course_id=1, title="Современный CSS", order_index=2),
        CourseModule(id=3, course_id=1, title="Введение в JavaScript", order_index=3),

        # UX/UI‑дизайн цифровых продуктов (course_id=2)
        CourseModule(id=4, course_id=2, title="Исследование пользователей", order_index=1),
        CourseModule(id=5, course_id=2, title="Прототипирование и интерфейсы", order_index=2),

        # Аналитик данных (course_id=3)
        CourseModule(id=6, course_id=3, title="Основы SQL", order_index=1),
        CourseModule(id=7, course_id=3, title="Отчеты и дашборды", order_index=2),

        # Backend на Python (course_id=4)
        CourseModule(id=8, course_id=4, title="Введение в Python backend", order_index=1),
        CourseModule(id=9, course_id=4, title="Работа с веб‑фреймворком", order_index=2),

        # Digital‑маркетолог (course_id=5)
        CourseModule(id=10, course_id=5, title="Основы digital‑стратегии", order_index=1),
        CourseModule(id=11, course_id=5, title="Реклама и аналитика", order_index=2),

        # Fullstack‑разработчик (course_id=6)
        CourseModule(id=12, course_id=6, title="Frontend для fullstack", order_index=1),
        CourseModule(id=13, course_id=6, title="Backend и API", order_index=2),
    ]
    session.add_all(modules)

    # Уроки для всех модулей (минимальная теория по каждому направлению)
    lessons = [
        # Frontend: HTML
        Lesson(
            id=1,
            module_id=1,
            title="Структура HTML‑страницы",
            order_index=1,
            content=(
                "<p>Разберём базовую структуру HTML‑документа: теги <code>&lt;html&gt;</code>, <code>&lt;head&gt;</code>, <code>&lt;body&gt;</code>.</p>"
                "<p>Поймём, что такое семантическая верстка и зачем нужны теги <code>&lt;header&gt;</code>, <code>&lt;main&gt;</code>, <code>&lt;footer&gt;</code>.</p>"
            ),
        ),
        Lesson(
            id=2,
            module_id=1,
            title="Текст, списки и ссылки",
            order_index=2,
            content=(
                "<p>Добавляем контент на страницу: параграфы, заголовки, списки и ссылки.</p>"
                "<pre><code>&lt;h1&gt;Bravelearn&lt;/h1&gt;\n&lt;p&gt;Онлайн‑курсы для развития карьеры&lt;/p&gt;</code></pre>"
            ),
        ),

        # Frontend: CSS
        Lesson(
            id=3,
            module_id=2,
            title="Подключение CSS и каскад",
            order_index=1,
            content=(
                "<p>Подключаем стили к странице: встроенные, внутренние и внешние CSS‑файлы.</p>"
                "<p>Разбираем базовую терминологию: селекторы, свойства, каскад и специфичность.</p>"
            ),
        ),
        Lesson(
            id=4,
            module_id=2,
            title="Flexbox и сетка", 
            order_index=2,
            content=(
                "<p>Изучаем современный способ раскладки интерфейса через Flexbox.</p>"
                "<pre><code>.container { display: flex; gap: 16px; }</code></pre>"
            ),
        ),

        # Frontend: JavaScript
        Lesson(
            id=5,
            module_id=3,
            title="Введение в JavaScript", 
            order_index=1,
            content=(
                "<p>Подключаем JavaScript на страницу и пишем первый скрипт.</p>"
                "<pre><code>console.log('Привет из Bravelearn!');</code></pre>"
            ),
        ),

        # UX/UI: исследования
        Lesson(
            id=6,
            module_id=4,
            title="Целевая аудитория и гипотезы", 
            order_index=1,
            content=(
                "<p>Учимся описывать целевую аудиторию и формулировать продуктовые гипотезы.</p>"
                "<p>Разбираем примеры пользовательских интервью.</p>"
            ),
        ),
        Lesson(
            id=7,
            module_id=4,
            title="Карта пути пользователя (CJM)", 
            order_index=2,
            content=(
                "<p>Строим карту пути пользователя от первого касания до целевого действия.</p>"
            ),
        ),

        # UX/UI: прототипы
        Lesson(
            id=8,
            module_id=5,
            title="Низкоуровневые прототипы", 
            order_index=1,
            content=(
                "<p>Делаем быстрованные прототипы экранов на бумаге или в Figma.</p>"
            ),
        ),

        # Аналитик данных: SQL
        Lesson(
            id=9,
            module_id=6,
            title="SELECT и фильтрация", 
            order_index=1,
            content=(
                "<p>Учимся выбирать данные из таблиц с помощью оператора <code>SELECT</code>.</p>"
                "<pre><code>SELECT * FROM users WHERE city = 'Москва';</code></pre>"
            ),
        ),
        Lesson(
            id=10,
            module_id=6,
            title="Группировка и агрегаты", 
            order_index=2,
            content=(
                "<p>Подсчитываем агрегаты с помощью <code>GROUP BY</code>, <code>COUNT</code>, <code>SUM</code>.</p>"
            ),
        ),

        # Аналитик данных: дашборды
        Lesson(
            id=11,
            module_id=7,
            title="Основы BI‑дашбордов", 
            order_index=1,
            content=(
                "<p>Разбираем принципы визуализации данных и типы графиков.</p>"
            ),
        ),

        # Backend на Python: основы языка
        Lesson(
            id=12,
            module_id=8,
            title="Знакомство с Python", 
            order_index=1,
            content=(
                "<p>В этом уроке вы настроите окружение и напишете первую программу на Python.</p>"
                "<p>Python — интерпретируемый язык программирования, который отлично подходит для backend‑разработки.</p>"
            ),
        ),
        Lesson(
            id=13,
            module_id=8,
            title="Переменные и типы данных", 
            order_index=2,
            content=(
                "<p>Разберём базовые типы данных: числа, строки, списки и словари.</p>"
                "<pre><code>name = 'Bravelearn'\nprint('Привет,', name)</code></pre>"
            ),
        ),

        # Backend на Python: веб‑фреймворк
        Lesson(
            id=14,
            module_id=9,
            title="Что такое backend и API", 
            order_index=1,
            content=(
                "<p>Объясняем, чем занимается backend‑разработчик и что такое REST API.</p>"
            ),
        ),

        # Digital‑маркетолог
        Lesson(
            id=15,
            module_id=10,
            title="Маркетинговая воронка", 
            order_index=1,
            content=(
                "<p>Разбираем этапы воронки: осведомлённость, интерес, решение и покупка.</p>"
            ),
        ),
        Lesson(
            id=16,
            module_id=11,
            title="Основы веб‑аналитики", 
            order_index=1,
            content=(
                "<p>Какие метрики важно отслеживать: CTR, CPC, CPA, ROI.</p>"
            ),
        ),

        # Fullstack‑разработчик
        Lesson(
            id=17,
            module_id=12,
            title="Архитектура SPA", 
            order_index=1,
            content=(
                "<p>Разбираем, чем одностраничные приложения отличаются от многостраничных.</p>"
            ),
        ),
        Lesson(
            id=18,
            module_id=13,
            title="Связь frontend и backend", 
            order_index=1,
            content=(
                "<p>Понимаем, как фронтенд и бэкенд обмениваются данными по HTTP и через JSON.</p>"
            ),
        ),
    ]
    session.add_all(lessons)

    # Практические задания для технических курсов
    tasks = [
        # Backend: функция приветствия (как и раньше)
        Task(
            id=1,
            lesson_id=13,
            title="Напишите функцию приветствия",
            description=(
                "Напишите функцию <code>greet(name)</code>, которая возвращает строку "
                "<code>'Привет, {name}!'</code>."
            ),
            starter_code=textwrap.dedent(
                """\
                def greet(name):
                    # TODO: реализуйте функцию
                    pass
                """
            ),
            checker_code=textwrap.dedent(
                """\
                assert greet('Мир') == 'Привет, Мир!'
                assert greet('Bravelearn') == 'Привет, Bravelearn!'
                print('OK')
                """
            ),
        ),
        # Fullstack: форматирование имени
        Task(
            id=2,
            lesson_id=18,
            title="Форматирование имени пользователя",
            description=(
                "Реализуйте функцию <code>format_user(full_name)</code>, которая принимает строку "
                "вида <code>'имя фамилия'</code> и возвращает её в формате <code>'Фамилия, Имя'</code>."
            ),
            starter_code=textwrap.dedent(
                """\
                def format_user(full_name: str) -> str:
                    # Разбейте строку по пробелу и верните в формате 'Фамилия, Имя'
                    pass
                """
            ),
            checker_code=textwrap.dedent(
                """\
                assert format_user('Иван Петров') == 'Петров, Иван'
                assert format_user('Anna Smith') == 'Smith, Anna'
                print('OK')
                """
            ),
        ),
    ]
    session.add_all(tasks)


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


@eel.expose
def api_get_course_structure(course_id: int):
    session = get_session()
    try:
        course = session.get(Course, course_id)
        if not course:
            return None

        modules = (
            session.query(CourseModule)
            .filter_by(course_id=course_id)
            .order_by(CourseModule.order_index, CourseModule.id)
            .all()
        )

        module_ids = [m.id for m in modules]
        lessons = []
        if module_ids:
            lessons = (
                session.query(Lesson)
                .filter(Lesson.module_id.in_(module_ids))
                .order_by(Lesson.module_id, Lesson.order_index, Lesson.id)
                .all()
            )

        progress_map = {}
        if CURRENT_USER_ID is not None and lessons:
            lp_rows = (
                session.query(LessonProgress)
                .filter(
                    LessonProgress.user_id == CURRENT_USER_ID,
                    LessonProgress.lesson_id.in_([l.id for l in lessons]),
                )
                .all()
            )
            for lp in lp_rows:
                progress_map[lp.lesson_id] = lp.is_completed

        lessons_by_module = {}
        for lesson in lessons:
            lessons_by_module.setdefault(lesson.module_id, []).append(
                {
                    "id": lesson.id,
                    "title": lesson.title,
                    "order_index": lesson.order_index,
                    "is_completed": progress_map.get(lesson.id, False),
                }
            )

        total_lessons = len(lessons)
        completed = sum(1 for l in lessons if progress_map.get(l.id, False))
        progress_percent = int((completed / total_lessons) * 100) if total_lessons else 0

        return {
            "course": {
                "id": course.id,
                "title": course.title,
            },
            "progress_percent": progress_percent,
            "modules": [
                {
                    "id": m.id,
                    "title": m.title,
                    "order_index": m.order_index,
                    "lessons": lessons_by_module.get(m.id, []),
                }
                for m in modules
            ],
        }
    finally:
        session.close()


@eel.expose
def api_get_lesson(lesson_id: int):
    session = get_session()
    try:
        lesson = session.get(Lesson, lesson_id)
        if not lesson:
            return None

        task = (
            session.query(Task)
            .filter_by(lesson_id=lesson_id)
            .order_by(Task.id)
            .first()
        )

        task_data = None
        if task is not None:
            task_data = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "starter_code": task.starter_code,
            }

        is_completed = False
        if CURRENT_USER_ID is not None:
            lp = (
                session.query(LessonProgress)
                .filter_by(user_id=CURRENT_USER_ID, lesson_id=lesson_id)
                .first()
            )
            if lp:
                is_completed = lp.is_completed

        return {
            "id": lesson.id,
            "title": lesson.title,
            "content_html": lesson.content or "",
            "is_completed": is_completed,
            "task": task_data,
        }
    finally:
        session.close()


@eel.expose
def api_mark_lesson_completed(lesson_id: int):
    if CURRENT_USER_ID is None:
        return {"ok": False, "error": "Необходима авторизация"}
    session = get_session()
    try:
        lesson = session.get(Lesson, lesson_id)
        if not lesson:
            return {"ok": False, "error": "Урок не найден"}

        lp = (
            session.query(LessonProgress)
            .filter_by(user_id=CURRENT_USER_ID, lesson_id=lesson_id)
            .first()
        )
        if not lp:
            lp = LessonProgress(user_id=CURRENT_USER_ID, lesson_id=lesson_id)
            session.add(lp)
        lp.is_completed = True
        lp.completed_at = datetime.utcnow()
        session.commit()
        return {"ok": True}
    finally:
        session.close()


@eel.expose
def api_get_task(task_id: int):
    session = get_session()
    try:
        task = session.get(Task, task_id)
        if not task:
            return None
        return {
            "id": task.id,
            "lesson_id": task.lesson_id,
            "title": task.title,
            "description": task.description,
            "starter_code": task.starter_code,
        }
    finally:
        session.close()


def _run_python_user_code(user_code: str, checker_code: str | None = None, timeout: int = 3):
    # Создаем временный файл в UTF-8 и явно указываем кодировку в заголовке,
    # чтобы русские комментарии и строки не вызывали SyntaxError в Python.
    with NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        path = tmp.name
        tmp.write("# -*- coding: utf-8 -*-\n")
        if checker_code:
            tmp.write(user_code)
            tmp.write("\n\n")
            tmp.write(checker_code)
        else:
            tmp.write(user_code)

    try:
        completed = subprocess.run(
            [sys.executable, "-I", path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        ok = completed.returncode == 0
        return ok, stdout, stderr
    except subprocess.TimeoutExpired:
        return False, "", "Превышено время выполнения кода"


@eel.expose
def api_run_python(code: str, task_id: int | None = None):
    session = get_session()
    try:
        checker_code = None
        task = None
        if task_id is not None:
            task = session.get(Task, task_id)
            if not task:
                return {"ok": False, "error": "Задание не найдено"}
            checker_code = task.checker_code

        ok, stdout, stderr = _run_python_user_code(code, checker_code=checker_code)

        is_passed = ok and ("OK" in stdout or checker_code is None)

        attempt = TaskAttempt(
            task_id=task_id if task_id is not None else None,
            user_id=CURRENT_USER_ID if CURRENT_USER_ID is not None else 0,
            code=code,
            is_passed=is_passed,
            output=(stdout + "\n" + stderr).strip(),
        )
        session.add(attempt)
        session.commit()

        return {
            "ok": True,
            "is_passed": is_passed,
            "stdout": stdout,
            "stderr": stderr,
        }
    finally:
        session.close()


def main():
    init_db()
    eel.init(str(WEB_DIR))
    eel.start("index.html", size=(1200, 800), icon="static/logo.ico")


main()

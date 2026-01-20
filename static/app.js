async function apiLogin(username, password) {
  const res = await eel.api_login(username, password)();
  return res;
}

async function apiGetCurrentUser() {
  return await eel.api_get_current_user()();
}

async function apiGetCourses() {
  return await eel.api_get_courses()();
}

async function apiGetCourse(courseId) {
  return await eel.api_get_course(courseId)();
}

async function apiGetCourseStructure(courseId) {
  return await eel.api_get_course_structure(courseId)();
}

async function apiGetLesson(lessonId) {
  return await eel.api_get_lesson(lessonId)();
}

async function apiMarkLessonCompleted(lessonId) {
  return await eel.api_mark_lesson_completed(lessonId)();
}

async function apiRunPython(code, taskId = null) {
  return await eel.api_run_python(code, taskId)();
}

async function apiToggleFavorite(courseId) {
  return await eel.api_toggle_favorite(courseId)();
}

let catalogCourses = [];
let courseStructure = null;
let courseLessonsFlat = [];
let currentLessonId = null;
let currentTaskId = null;
let taskEditor = null;

function attachLoginHandlers() {
  const form = document.querySelector('#login-form');
  if (!form) return;
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = form.querySelector('input[name="username"]').value.trim();
    const password = form.querySelector('input[name="password"]').value.trim();
    if (!username || !password) return;
    const result = await apiLogin(username, password);
    const errorBox = document.querySelector('#login-error');
    if (!result.ok) {
      if (errorBox) errorBox.textContent = result.error || 'Ошибка входа';
      return;
    }
    window.location.href = 'profile.html';
  });
}

function renderCatalogCourses(courses) {
  const grid = document.querySelector('.courses-grid--catalog');
  if (!grid) return;
  grid.innerHTML = '';
  courses.forEach((c) => {
    const article = document.createElement('article');
    article.className = 'course-card';
    article.setAttribute('data-course-id', c.id);
    article.innerHTML = `
          <div class="course-card__badge">${c.category}</div>
          <div class="course-card__image">
              <img src="${c.image_path}" alt="${c.title}">
          </div>
          <div class="course-card__body">
              <h3>${c.title}</h3>
              <p>${c.description}</p>
              <div class="course-card__meta">
                  <span>${c.duration}</span>
                  <span>${c.level}</span>
              </div>
              <div class="course-card__actions">
                  <button class="course-card__fav" type="button">В избранное</button>
                  <button class="btn btn--secondary course-card__details" type="button">Подробнее о курсе</button>
              </div>
          </div>
    `;
    grid.appendChild(article);
  });

  attachFavoriteHandlers();
  initFavoritesForCards();
  attachDetailsHandlers();
}

function applyCatalogFilters() {
  if (!catalogCourses.length) return;
  let filtered = [...catalogCourses];

  const activeChip = document.querySelector('.catalog__chips .chip.chip--active');
  if (activeChip) {
    const chipText = activeChip.textContent.trim();
    if (chipText !== 'Все направления') {
      filtered = filtered.filter((c) => c.category === chipText);
    }
  }

  const levelSelect = document.querySelector('.catalog__selects select:nth-of-type(1)');
  if (levelSelect) {
    const value = levelSelect.value.trim();
    if (!value.startsWith('Уровень: любой')) {
      const level = value.replace('Уровень:', '').trim();
      filtered = filtered.filter((c) => c.level === level);
    }
  }

  renderCatalogCourses(filtered);
}

async function initCatalogPage() {
  catalogCourses = await apiGetCourses();

  const chips = document.querySelectorAll('.catalog__chips .chip');
  chips.forEach((chip) => {
    chip.addEventListener('click', () => {
      chips.forEach((c) => c.classList.remove('chip--active'));
      chip.classList.add('chip--active');
      applyCatalogFilters();
    });
  });

  const levelSelect = document.querySelector('.catalog__selects select:nth-of-type(1)');
  if (levelSelect) {
    levelSelect.addEventListener('change', applyCatalogFilters);
  }

  applyCatalogFilters();
}

function renderFavoriteState(button, isFavorite) {
  if (!button) return;
  button.classList.toggle('course-card__fav--active', isFavorite);
  button.textContent = isFavorite ? 'В избранном' : 'В избранное';
}

function attachFavoriteHandlers() {
  document.querySelectorAll('[data-course-id]').forEach((card) => {
    const id = parseInt(card.getAttribute('data-course-id'), 10);
    const favBtn = card.querySelector('.course-card__fav');
    if (!favBtn) return;
    favBtn.addEventListener('click', async () => {
      const res = await apiToggleFavorite(id);
      if (res.ok) {
        renderFavoriteState(favBtn, res.is_favorite);
      }
    });
  });
}

async function initFavoritesForCards() {
  const cards = document.querySelectorAll('[data-course-id]');
  if (!cards.length) return;
  const courses = await apiGetCourses();
  const byId = new Map(courses.map((c) => [c.id, c]));
  cards.forEach((card) => {
    const id = parseInt(card.getAttribute('data-course-id'), 10);
    const favBtn = card.querySelector('.course-card__fav');
    const course = byId.get(id);
    if (!favBtn || !course) return;
    if (course.is_favorite) {
      renderFavoriteState(favBtn, true);
    } else {
      renderFavoriteState(favBtn, false);
    }
  });
}

function attachDetailsHandlers() {
  document.querySelectorAll('[data-course-id]').forEach((card) => {
    const id = parseInt(card.getAttribute('data-course-id'), 10);
    const detailsBtn = card.querySelector('.course-card__details');
    const titleEl = card.querySelector('.course-card__body h3');

    if (detailsBtn) {
      detailsBtn.addEventListener('click', () => {
        window.location.href = `course.html?id=${id}`;
      });
    }

    if (titleEl) {
      titleEl.style.cursor = 'pointer';
      titleEl.addEventListener('click', () => {
        window.location.href = `course.html?id=${id}`;
      });
    }
  });
}

async function initProfilePage() {
  const user = await apiGetCurrentUser();
  const loginBlock = document.querySelector('#profile-login-block');
  const dataBlock = document.querySelector('#profile-data-block');
  if (!user) {
    if (loginBlock) loginBlock.style.display = 'block';
    if (dataBlock) dataBlock.style.display = 'none';
    attachLoginHandlers();
    return;
  }
  if (loginBlock) loginBlock.style.display = 'none';
  if (dataBlock) dataBlock.style.display = 'block';

  const usernameEl = document.querySelector('#profile-username');
  const passwordInput = document.querySelector('#profile-password');
  if (usernameEl) usernameEl.textContent = user.username;
  if (passwordInput) passwordInput.value = user.password;

  const toggleBtn = document.querySelector('#toggle-password-visibility');
  if (toggleBtn && passwordInput) {
    passwordInput.type = 'password';
    toggleBtn.addEventListener('click', () => {
      if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleBtn.textContent = 'Скрыть';
      } else {
        passwordInput.type = 'password';
        toggleBtn.textContent = 'Посмотреть';
      }
    });
  }

  const favoritesContainer = document.querySelector('#profile-favorites');
  if (favoritesContainer) {
    const courses = await apiGetCourses();
    favoritesContainer.innerHTML = '';
    courses
      .filter((c) => user.favorite_course_ids.includes(c.id))
      .forEach((c) => {
        const item = document.createElement('div');
        item.className = 'profile-fav-card';
        item.innerHTML = `
          <div class="profile-fav-thumb">
              <img src="${c.image_path}" alt="${c.title}">
          </div>
          <div class="profile-fav-body">
              <h3>${c.title}</h3>
              <p>${c.description}</p>
          </div>
        `;
        item.setAttribute('data-course-id', c.id);

        const titleEl = item.querySelector('h3');
        if (titleEl) {
          titleEl.style.cursor = 'pointer';
          titleEl.addEventListener('click', () => {
            window.location.href = `course.html?id=${c.id}`;
          });
        }

        favoritesContainer.appendChild(item);
      });
  }
}

function getPageTransitionOverlay() {
  return document.getElementById('page-transition');
}

function showPageTransition(duration = 600, callback) {
  const overlay = getPageTransitionOverlay();
  if (!overlay) {
    if (callback) callback();
    return;
  }
  overlay.classList.add('page-transition--visible');
  setTimeout(() => {
    if (callback) callback();
  }, duration);
}

function hidePageTransition(duration = 600) {
  const overlay = getPageTransitionOverlay();
  if (!overlay) return;
  overlay.classList.remove('page-transition--visible');
}

async function initCoursePage() {
  const params = new URLSearchParams(window.location.search);
  const id = parseInt(params.get('id'), 10);
  if (!id) return;
  const data = await apiGetCourse(id);
  if (!data) return;

  const titleEl = document.querySelector('#course-title');
  const descEl = document.querySelector('#course-description');
  const longDescEl = document.querySelector('#course-long-description');
  const imgEl = document.querySelector('#course-image');
  const metaEl = document.querySelector('#course-meta');
  const downloadBtn = document.querySelector('#course-download');

  if (titleEl) titleEl.textContent = data.title;
  if (descEl) descEl.textContent = data.description;
  if (longDescEl && data.long_description) longDescEl.textContent = data.long_description;
  if (imgEl) {
    imgEl.src = data.image_path;
    imgEl.alt = data.title;
  }
  if (metaEl) {
    metaEl.textContent = `${data.category} • ${data.duration} • ${data.level}`;
  }
  if (downloadBtn && data.materials_path) {
    downloadBtn.href = data.materials_path;
    downloadBtn.download = '';
  }

  courseStructure = await apiGetCourseStructure(id);
  if (!courseStructure || !courseStructure.modules) return;

  const lessonsContainer = document.querySelector('#course-lessons-list');
  const progressFill = document.querySelector('#course-progress-bar-fill');
  const progressText = document.querySelector('#course-progress-text');

  if (progressFill && typeof courseStructure.progress_percent === 'number') {
    progressFill.style.width = `${courseStructure.progress_percent}%`;
  }
  if (progressText) {
    progressText.textContent = `${courseStructure.progress_percent || 0}%`;
  }

  courseLessonsFlat = [];
  if (lessonsContainer) {
    lessonsContainer.innerHTML = '';
    courseStructure.modules.forEach((mod) => {
      const moduleEl = document.createElement('div');
      moduleEl.className = 'course-learning__module';
      const moduleTitle = document.createElement('h4');
      moduleTitle.textContent = mod.title;
      moduleEl.appendChild(moduleTitle);

      const ul = document.createElement('ul');
      ul.className = 'course-learning__lessons-list';
      (mod.lessons || []).forEach((lesson) => {
        courseLessonsFlat.push({ id: lesson.id, title: lesson.title, moduleId: mod.id });
        const li = document.createElement('li');
        li.className = 'course-learning__lesson-item';
        li.dataset.lessonId = String(lesson.id);
        if (lesson.is_completed) {
          li.classList.add('course-learning__lesson-item--completed');
        }
        li.innerHTML = `
          <button type="button" class="course-learning__lesson-button">
            <span class="course-learning__lesson-title">${lesson.title}</span>
            ${lesson.is_completed ? '<span class="course-learning__lesson-status-badge">Пройдено</span>' : ''}
          </button>
        `;
        li.querySelector('button').addEventListener('click', () => {
          loadLesson(lesson.id);
        });
        ul.appendChild(li);
      });

      moduleEl.appendChild(ul);
      lessonsContainer.appendChild(moduleEl);
    });
  }

  let firstLessonId = null;
  let firstUncompletedId = null;
  courseStructure.modules.forEach((mod) => {
    (mod.lessons || []).forEach((lesson) => {
      if (!firstLessonId) firstLessonId = lesson.id;
      if (!lesson.is_completed && !firstUncompletedId) firstUncompletedId = lesson.id;
    });
  });

  const startLessonId = firstUncompletedId || firstLessonId;
  if (startLessonId) {
    await loadLesson(startLessonId);
  }

  const prevBtn = document.querySelector('#lesson-prev');
  const nextBtn = document.querySelector('#lesson-next');
  const completeBtn = document.querySelector('#lesson-complete');

  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      if (!currentLessonId || !courseLessonsFlat.length) return;
      const idx = courseLessonsFlat.findIndex((l) => l.id === currentLessonId);
      if (idx > 0) {
        loadLesson(courseLessonsFlat[idx - 1].id);
      }
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      if (!currentLessonId || !courseLessonsFlat.length) return;
      const idx = courseLessonsFlat.findIndex((l) => l.id === currentLessonId);
      if (idx >= 0 && idx < courseLessonsFlat.length - 1) {
        loadLesson(courseLessonsFlat[idx + 1].id);
      }
    });
  }

  if (completeBtn) {
    completeBtn.addEventListener('click', async () => {
      if (!currentLessonId) return;
      const statusEl = document.querySelector('#lesson-status');
      if (statusEl) statusEl.textContent = 'Сохраняем прогресс...';
      const res = await apiMarkLessonCompleted(currentLessonId);
      if (!res || !res.ok) {
        if (statusEl) statusEl.textContent = res && res.error ? res.error : 'Не удалось сохранить прогресс';
        return;
      }
      if (statusEl) statusEl.textContent = 'Урок отмечен как пройденный';

      const listItem = document.querySelector(`.course-learning__lesson-item[data-lesson-id="${currentLessonId}"]`);
      if (listItem) {
        listItem.classList.add('course-learning__lesson-item--completed');
        const badge = listItem.querySelector('.course-learning__lesson-status-badge');
        if (!badge) {
          const btn = listItem.querySelector('button');
          if (btn) {
            const span = document.createElement('span');
            span.className = 'course-learning__lesson-status-badge';
            span.textContent = 'Пройдено';
            btn.appendChild(span);
          }
        }
      }

      courseStructure = await apiGetCourseStructure(id);
      if (courseStructure && typeof courseStructure.progress_percent === 'number') {
        if (progressFill) progressFill.style.width = `${courseStructure.progress_percent}%`;
        if (progressText) progressText.textContent = `${courseStructure.progress_percent}%`;
      }
    });
  }
}

async function loadLesson(lessonId) {
  const data = await apiGetLesson(lessonId);
  if (!data) return;
  currentLessonId = lessonId;

  const titleEl = document.querySelector('#lesson-title');
  const contentEl = document.querySelector('#lesson-content');
  const statusEl = document.querySelector('#lesson-status');
  const lessonItemEls = document.querySelectorAll('.course-learning__lesson-item');

  if (titleEl) titleEl.textContent = data.title;
  if (contentEl) contentEl.innerHTML = data.content_html || '';
  if (statusEl) {
    statusEl.textContent = data.is_completed ? 'Урок уже отмечен как пройденный' : '';
  }

  lessonItemEls.forEach((li) => {
    if (parseInt(li.dataset.lessonId, 10) === lessonId) {
      li.classList.add('course-learning__lesson-item--active');
    } else {
      li.classList.remove('course-learning__lesson-item--active');
    }
  });

  const taskBlock = document.querySelector('#lesson-task-block');
  const taskTitleEl = document.querySelector('#task-title');
  const taskDescEl = document.querySelector('#task-description');
  const taskCodeEl = document.querySelector('#task-code');
  const taskStatusEl = document.querySelector('#task-status');
  const taskOutputEl = document.querySelector('#task-output');
  const runBtn = document.querySelector('#task-run');

  if (!data.task) {
    if (taskBlock) taskBlock.style.display = 'none';
    currentTaskId = null;
    return;
  }

  currentTaskId = data.task.id;
  if (taskBlock) taskBlock.style.display = 'block';
  if (taskTitleEl) taskTitleEl.textContent = data.task.title;
  if (taskDescEl) taskDescEl.innerHTML = data.task.description || '';
  if (taskCodeEl) taskCodeEl.value = data.task.starter_code || '';
  if (taskStatusEl) taskStatusEl.textContent = '';
  if (taskOutputEl) taskOutputEl.textContent = '';

  // Инициализируем или обновляем CodeMirror над textarea
  if (window.CodeMirror && taskCodeEl) {
    if (!taskEditor) {
      taskEditor = window.CodeMirror.fromTextArea(taskCodeEl, {
        mode: 'python',
        theme: 'dracula',
        lineNumbers: true,
        indentUnit: 4,
        tabSize: 4,
        indentWithTabs: false,
        lineWrapping: true,
        autofocus: false,
      });
    }
    taskEditor.setValue(data.task.starter_code || '');
    taskEditor.focus();
  }

  if (runBtn) {
    runBtn.onclick = async () => {
      if (!taskCodeEl) return;
      const code = taskEditor ? taskEditor.getValue() : taskCodeEl.value;
      if (!code.trim()) return;
      if (taskStatusEl) taskStatusEl.textContent = 'Запускаем код...';
      const res = await apiRunPython(code, currentTaskId);
      if (!res || !res.ok) {
        if (taskStatusEl) taskStatusEl.textContent = res && res.error ? res.error : 'Ошибка при выполнении кода';
        return;
      }
      if (taskOutputEl) {
        const out = `${res.stdout || ''}${res.stderr ? `\n[stderr]\n${res.stderr}` : ''}`.trim();
        taskOutputEl.textContent = out || '(нет вывода)';
      }
      if (taskStatusEl) {
        taskStatusEl.textContent = res.is_passed ? 'Тесты пройдены 🎉' : 'Тесты не пройдены, попробуйте ещё раз';
      }
    };
  }
}

function initPage() {
  if (document.body.classList.contains('catalog-body')) {
    initCatalogPage();
  }
  if (document.body.classList.contains('profile-body')) {
    initProfilePage();
  }
  if (document.body.classList.contains('index-body')) {
    attachFavoriteHandlers();
    initFavoritesForCards();
    attachDetailsHandlers();
  }
  if (document.body.classList.contains('course-body')) {
    initCoursePage();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // Показать загрузочную заставку при старте и плавно скрыть её
  showPageTransition(500, () => {
    hidePageTransition(600);
  });

  // После инициализации страницы подхватываем переходы между *.html
  initPage();

  document.querySelectorAll('a[href$=".html"]').forEach((link) => {
    const href = link.getAttribute('href');
    if (!href) return;
    link.addEventListener('click', (e) => {
      const target = e.currentTarget;
      if (target.dataset && target.dataset.noFade === 'true') return;
      e.preventDefault();
      showPageTransition(400, () => {
        window.location.href = href;
      });
    });
  });
});

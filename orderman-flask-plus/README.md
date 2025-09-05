# Oderman (Flask + Jinja2 + DB + Weather + Survey)

Простий сайт піцерії з БД (SQLite), адмін-форми, уроки, погода (OpenWeather), опитування.

## Запуск
```
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
# ДЛЯ ПОГОДИ: експортуй ключ
# PowerShell: $env:OPENWEATHER_API_KEY="YOUR_KEY"
# Bash: export OPENWEATHER_API_KEY="YOUR_KEY"
python app.py
```
Відкрий: http://127.0.0.1:5000

## Навігація
- Головна (`/`) — назва, фото, **погода за містом і датою** + рекомендація піци.
- Меню (`/menu`) — таблиця страв з БД, сортування за назвою/ціною, **редагування/видалення** (через пароль `admin123`).
- Адмін: додати страву (`/admin/menu/new`).
- Уроки: список (`/lessons`) і **додати урок** (`/admin/lessons/new`).
- Опитування (`/survey`) і **результати** (`/survey/results`).

## База даних
- `menu_items(id, name, description, price)`
- `lessons(id, title, lesson_date, note)`
- `votes(id, menu_item_id, created_at)`
База `orderman.sqlite3` створиться автоматично; демо-дані додаються при першому запуску.

## Погода (OpenWeather)
- Потрібен API key `OPENWEATHER_API_KEY`.
- Якщо обрана дата **сьогодні або в минулому** — береться поточна погода.
- Якщо **майбутня** (до 5 днів) — прогноз 5-day/3h, найближчий до 12:00.
- Показуємо температуру, стан і **рекомендацію піци** по погоді.

Все зроблено просто, як навчальний приклад.

## Відгуки (Flask-WTF)
- Форма: `GET/POST /feedback` (CSRF, валідатори: повідомлення 5..1000 символів, рейтинг 1..5, ім'я необов'язкове).
- Перегляд: `GET /feedbacks`.  
  Додатково: **гарні** відгуки (4–5) показуються зеленим, **погані** (1–2) — червоним.

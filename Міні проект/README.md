# Сайт‑визитка на Django (одна страница, AJAX, SQLite)

## Технические требования — реализовано
- Одна страница с общей информацией, описанием, изображениями, отзывами и кнопками «Оставить заявку / Заказать».
- При нажатии открывается **модальное окно** с формой.
- Создание заказа происходит **в модальном окне через AJAX** (без перезагрузки) на `POST /api/order/`.
- Все заявки/заказы сохраняются в **БД SQLite** (модель `Order`).
- Добавлено аккуратное **оформление** (темная тема, адаптив) и готовые **надписи/контент**.

## Структура
```
landing_site/
├─ manage.py
├─ landing_site/
│  ├─ __init__.py
│  ├─ settings.py
│  ├─ urls.py
│  ├─ asgi.py
│  └─ wsgi.py
└─ landing/
   ├─ __init__.py
   ├─ admin.py
   ├─ apps.py
   ├─ models.py
   ├─ urls.py
   ├─ views.py
   ├─ migrations/
   │  ├─ __init__.py
   │  └─ 0001_initial.py
   ├─ templates/landing/index.html
   └─ static/landing/
      ├─ css/styles.css
      ├─ js/app.js
      └─ img/preview.png
```

## Запуск локально
1) Python 3.10+
2) (Опционально) виртуальное окружение
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```
3) Установка зависимостей
```bash
pip install -r requirements.txt
```
4) Применить миграции и запустить сервер
```bash
cd landing_site
python manage.py migrate
python manage.py runserver
```
5) Открыть: http://127.0.0.1:8000/

## Где смотреть заявки
- Заявки сохраняются в таблицу `landing_order` (SQLite `db.sqlite3` в корне проекта).
- При желании можно зайти в админку `/admin` (создайте суперпользователя: `python manage.py createsuperuser`).

## Настройка под себя
- Тексты/надписи — в `templates/landing/index.html`.
- Стили — `static/landing/css/styles.css`.
- Список продуктов в селекте — там же (шаблон).
- Модель заявки — `landing/models.py`.

## Превью
Смотри `static/landing/img/preview.png`.

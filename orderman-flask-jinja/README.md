# Oderman (Flask + Jinja2)

Перероблена версія з **Jinja2 наслідуванням шаблонів**: є `base.html`, а сторінки його розширюють.
Також є SQLite база і адмін-форма для додавання страв.

## Запуск
```
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Відкрий: http://127.0.0.1:5000

## Маршрути
- `/` — головна (назва, фото, кнопка "МЕНЮ").
- `/menu` — таблиця страв з бази.
- `/admin/menu/new` — форма додавання (пароль: `admin123`).

## Шаблони
- `templates/base.html` — базовий макет (блоки: `title`, `extra_head`, `content`, `extra_scripts`).
- `templates/index.html`, `menu.html`, `admin_form.html` — **extends base**.
- `templates/partials/nav.html`, `partials/flash.html` — include частини.
- `templates/macros.html` — макрос форматування ціни.

Все зроблено просто, як навчальний приклад.

## Сортування в меню
На сторінці `/menu` можна перемикати сортування:
- `за назвою` (за замовчуванням),
- `ціна ↑` (дешевше зверху),
- `ціна ↓` (дорожче зверху).
Посилання просто додають `?sort=name|price_asc|price_desc`.

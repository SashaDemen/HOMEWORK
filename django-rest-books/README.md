# Домашнє завдання — Django REST API (Книги, Реєстрація, Події)

## Частина 1 — Книги
- `GET /api/books/` — список усіх книг (JSON, 200 OK)
- `POST /api/books/` — додати книгу (JSON, 201 Created або 400 Bad Request)
- `GET /api/books/{id}/` — деталі книги (JSON, 200 OK або 404 Not Found)

**Структура книги**: `{ id, title, author, year, quantity }` з валідацією.

## Частина 2 — Реєстрація користувачів
- `POST /api/users/register/` — глибока валідація:
  - Ім'я/Прізвище: мін. 2 символи, лише літери (укр/лат).
  - Email: валідний.
  - Пароль: ≥8, велика/маленька літера, цифра, спецсимвол.
  - Телефон: мобільний формат (`+` та 10–15 цифр).
- 201 Created при успіху, 400 Bad Request при помилках, 409 Conflict якщо email уже існує.

## Частина 3 — Події (з чіткими статус-кодами)
- `POST /api/events/` — створення події (201 Created; 400 Bad Request; 403 Forbidden якщо не staff)
- `GET /api/events/` — список (200 OK; 204 No Content якщо порожньо)
- `GET /api/events/{id}/` — деталі (200 OK; 404 Not Found)
- `PUT /api/events/{id}/` — оновлення (200 OK; 400 Bad Request; 404 Not Found; 422 Unprocessable Entity якщо намагаєтесь змінити заборонені поля)
- `DELETE /api/events/{id}/` — видалення (200 OK; 404 Not Found; 403 Forbidden якщо немає прав)
- `PATCH /api/events/{id}/reschedule/` — перенести (200 OK; 400 Bad Request якщо дата в минулому; 404 Not Found)
- `POST /api/events/{id}/rsvp/` — реєстрація (200 OK; 404 Not Found; 409 Conflict якщо вже зареєстрований)

### Права доступу для подій
- Перегляд (GET) — доступний усім.
- Створення/оновлення/видалення — **тільки staff** користувачі (інакше 403).

## Запуск
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd api_project
python manage.py migrate
python manage.py createsuperuser  # (щоб мати staff-акаунт)
python manage.py runserver
# API буде на http://127.0.0.1:8000/api/
```

## Приклади запитів
**Створити книгу:**
```bash
curl -X POST http://127.0.0.1:8000/api/books/ -H 'Content-Type: application/json' -d '{
  "title":"Чистий код","author":"Роберт Мартін","year":2008,"quantity":5
}'
```

**Реєстрація користувача:**
```bash
curl -X POST http://127.0.0.1:8000/api/users/register/ -H 'Content-Type: application/json' -d '{
  "first_name":"Іван","last_name":"Петренко","email":"ivan@example.com",
  "password":"Strong#123","phone":"+380501112233"
}'
```

**Створити подію (потрібно бути staff і автентифікованим, наприклад через BasicAuth):**
```bash
curl -u admin:password -X POST http://127.0.0.1:8000/api/events/ -H 'Content-Type: application/json' -d '{
  "title":"Міт-ап Django","description":"Лекція та Q&A",
  "start_at":"2030-01-01T10:00:00Z","end_at":"2030-01-01T12:00:00Z","location":"Online"
}'
```

**Перенести подію:**
```bash
curl -X PATCH http://127.0.0.1:8000/api/events/1/reschedule/ -H 'Content-Type: application/json' -d '{
  "start_at":"2030-02-01T10:00:00Z"
}'
```

**RSVP:**
```bash
curl -X POST http://127.0.0.1:8000/api/events/1/rsvp/ -H 'Content-Type: application/json' -d '{
  "email":"user@example.com"
}'
```

## Нотатки
- Для 422 при PUT ми блокуємо зміну полів, що не входять до дозволених (`title, description, start_at, end_at, location`). 
- Сховище — SQLite (файл `db.sqlite3` в корені `api_project/`).

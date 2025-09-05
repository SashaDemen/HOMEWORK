# FastAPI Middleware Demo

## Опис
Цей проєкт демонструє створення **власного middleware** у FastAPI, яке виконує дві основні функції:
1. **Логування** кожного HTTP-запиту (метод, URL, час отримання).
2. **Перевірка заголовка `X-Custom-Header`**. Якщо він відсутній — повертається `400 Bad Request` і запит не передається далі.

## Функціонал
- Логування у консоль: `[час] METHOD URL`.
- Якщо запит іде без `X-Custom-Header` — відповідь: `400 {"detail":"Missing required header: X-Custom-Header"}`.
- Є винятки для шляхів `/docs`, `/redoc`, `/openapi.json`, `/public`.

## Маршрути
- `/` — інфо про API.
- `/public` — публічний маршрут, не вимагає заголовка.
- `/ping` — потребує заголовок, відповідає {"ok": true, "msg": "pong"}.
- `/echo` (POST) — потребує заголовок, повертає тіло запиту.
- `/secure-info` — потребує заголовок, повертає секретне повідомлення.
- `/docs` — Swagger UI (зручно тестувати навіть без заголовка).

## Запуск
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Сервер підніметься на http://127.0.0.1:8000

## Приклади
### Без заголовка (очікувано 400)
```bash
curl -i http://127.0.0.1:8000/ping
```

### З заголовком (200)
```bash
curl -i -H "X-Custom-Header: demo" http://127.0.0.1:8000/ping
```

### POST /echo
```bash
curl -i -H "Content-Type: application/json" -H "X-Custom-Header: demo"   -d '{"hello":"world"}' http://127.0.0.1:8000/echo
```

### Публічний маршрут
```bash
curl -i http://127.0.0.1:8000/public
```

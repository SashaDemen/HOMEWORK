# Movies API (FastAPI + Pydantic)

## Опис
Простий бекенд для керування колекцією фільмів (як у стрімінговому сервісі).
Pydantic моделі з валідацією, ендпоінти CRUD (часткові). Дані — в пам'яті.

## Моделі
- `MovieCreate`: `title` (str, не порожній), `director` (str, не порожній),
  `release_year` (int, 1888..поточний, не в майбутньому), `rating` (0..10).
- `Movie`: як вище + `id` (int).
- Відповіді серіалізуються через Pydantic (`response_model`).

## Ендпоінти
- `GET /movies` — список фільмів.
- `POST /movies` — додати фільм (201 Created).
- `GET /movies/{id}` — отримати фільм за ID (404 якщо немає).
- `DELETE /movies/{id}` — видалити (204 No Content або 404).

## Запуск
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Приклади
```bash
# Додати
curl -X POST http://127.0.0.1:8000/movies -H "Content-Type: application/json" -d '{
  "title":"Inception","director":"Christopher Nolan","release_year":2010,"rating":8.8
}'

# Список
curl http://127.0.0.1:8000/movies

# Деталі
curl http://127.0.0.1:8000/movies/1

# Видалити
curl -X DELETE http://127.0.0.1:8000/movies/1 -i
```

## Тести
```bash
pytest -q
```
Перевіряються: додавання/список/деталі, валідація (майбутній рік, порожній title, rating поза діапазоном), видалення та 404.

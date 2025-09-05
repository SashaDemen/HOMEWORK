# FastAPI Auth Demo (basic + oauth2)

просто приклад як зробити http basic і oauth2 у fastapi. 
код максимально простий і з коментарями в main.py

## як запустити
```
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
відкриваєте http://127.0.0.1:8000/docs і там все можна потестити

## що є
- GET /basic/secret — потребує HTTP Basic (alice / Secret#123 або bob / qwerty123)
- POST /token — видає bearer токен (форма username/password)
- GET /me — треба Authorization: Bearer <token>
- GET /data — теж приватне
- GET /debug/tokens — просто подивитись, скільки токенів (для навчання)

## тести
```
pytest -q
```
там перевіряється basic, отримання токена і доступ до приватних маршрутів.

p.s. тут немає справжньої бази даних і хешування паролів, бо це демка. у реалі треба інакше.

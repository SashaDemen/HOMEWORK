# FastAPI WebSocket Chat (JWT, sanitize, sessions)

## Функціонал
- `/auth/login` — отримати JWT (демо-користувачі: `alice` / `bob`, пароль `Secret#123`).
- `/ws` — WebSocket-чат з автентифікацією (JWT у `Authorization: Bearer <token>` або `?token=`).
- Санітизація повідомлень (escape HTML).
- Облік активних сесій: `GET /sessions/active`.
- Простий ліміт повідомлень (антиспам).
- Перевірка `Origin` для WS (бази: localhost, 127.0.0.1, testserver).

## Безпека
- Автентифікація — JWT (підпис HS256). `SECRET_KEY` береться з env, інакше dev.
- WS допускає тільки дозволені `Origin` (налаштовується у `settings.py`).
- Санітизація тексту + обрізання довгих повідомлень, видалення control chars.
- CSRF: ми не використовуємо cookie, а токен у заголовку — ризик CSRF мінімізовано. Для продакшену: термінація TLS (Nginx/Traefik), увімкнути HSTS, перевірка `Origin`/`Sec-WebSocket-Protocol`.
- Масштабування: для багатьох процесів/серверів додайте брокер (Redis pub/sub) для широкомовлення між нодами.

## Запуск
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Приклад
1) Отримати токен:
```bash
curl -X POST http://127.0.0.1:8000/auth/login -H "Content-Type: application/json" -d '{"username":"alice","password":"Secret#123"}'
```
2) Підключитись до WS (wscat):
```bash
wscat -c "ws://127.0.0.1:8000/ws?token=<TOKEN>"
```
Надіслати повідомлення:
```json
{ "message": "Hello <script>alert(1)</script>" }
```
Інші клієнти отримають:
```json
{ "type": "chat", "from": "alice", "message": "Hello &lt;script&gt;alert(1)&lt;/script&gt;" }
```

## Тести
```bash
pytest -q
```
Тести перевіряють:
- автентифікацію,
- відмову для WS без токена,
- відправлення/отримання повідомлень з санітизацією,
- лічильник активних сесій.

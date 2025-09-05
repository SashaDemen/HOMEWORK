# Messaging API (FastAPI, background queue)

## Що є
- `/emails/send` — приймає користувача, subject, body; ставить у чергу надсилання листа (асинхронно). Повертає `202` і `task_id`.
- `/files/upload` — приймає файли; ставить у чергу обробку (ресайз зображень). Повертає `202` і список `task_ids`.
- `/tasks/{id}` — статус завдання (PENDING/RUNNING/DONE/ERROR), результат/помилка.
- `/tasks` — список завдань (для моніторингу).
- `/health` — перевірка живості.
- Логування у `logs/app.log`: дата, час, тип дії, користувач/дані.

## Запуск
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Приклади
### Надсилання листа
```bash
curl -X POST http://127.0.0.1:8000/emails/send -H "Content-Type: application/json" -d '{
  "user": {"email":"user@example.com","name":"User"},
  "subject":"Hello",
  "body":"Test message"
}'
```
Потім перевірити статус:
```bash
curl http://127.0.0.1:8000/tasks/<TASK_ID>
```
Лист збережеться як файл `.eml` у папці `outbox/`.

### Завантаження файлів (зображення)
```bash
curl -F "files=@some.jpg" -F "files=@another.png" http://127.0.0.1:8000/files/upload
```
Статус кожного:
```bash
curl http://127.0.0.1:8000/tasks/<TASK_ID>
```
Результат — шлях до зменшеного зображення у `storage/processed/`.

## Черга фонових завдань
Всередині — простий worker-потік (in-memory) з моніторингом станів і помилок. Для продакшену можна замінити на Redis/Celery.

## Тести
```bash
pytest -q
```

## Примітка
Проєкт зроблено без зайвих коментарів, як простий повний приклад.

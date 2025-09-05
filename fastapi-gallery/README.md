# Photo Gallery API (FastAPI)

## Що вміє
- Приймає JPG/PNG (multipart), один або кілька.
- Перевіряє тип і розмір (до 4MB/файл).
- Санітизує назви файлів, запобігає traversal.
- Зберігає оригінали в `storage/uploads/`.
- Фонова обробка: ресайз до 1600x1600, конвертація в WEBP, збереження у `storage/processed/`.
- Асинхронно: повертає `202` + `task_ids`, стеження через `/tasks/{id}`.
- Логи у `logs/gallery.log`.
- Завантаження обробленого: `GET /gallery/download/{name}` (ім'я — з `processed`).

## Запуск
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API
### Upload
```bash
curl -F "files=@img1.jpg" -F "files=@img2.png" http://127.0.0.1:8000/gallery/upload
```
-> `202 {"items":[...], "task_ids":[...]}`
Потім:
```bash
curl http://127.0.0.1:8000/tasks/<TASK_ID>
```

### Download
Після `DONE` беріть ім'я з `storage/processed/` і:
```bash
curl -OJ http://127.0.0.1:8000/gallery/download/<processed_name.webp>
```

## Безпека
- Перевірка вмісту: тип, розмір, санітизація імені, права `0600`.
- Віддаємо лише з `processed` і тільки за безпечним ім'ям.
- Для продакшену: обмежте розмір запиту на рівні сервера, використовуйте CDN, додайте авторизацію.

## Тести
```bash
pytest -q
```

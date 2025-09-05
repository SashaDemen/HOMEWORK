from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.openapi.utils import get_openapi
from typing import List

# наші моделі і "база"
from .models import Movie, MovieCreate
from .store import store

# =====================================================
# FastAPI застосунок. Буду додавати summary/description/tags і тд
# =====================================================
app = FastAPI(
    title="Movies API (Docs Demo)",
    version="1.0.0",
    description=(
        "Це навчальний API для керування колекцією фільмів. "
        "Тут я спеціально зробив багато описів для Swagger."
    ),
    openapi_tags=[
        {"name": "movies", "description": "Операції з фільмами (створення, список, деталі, видалення)"},
        {"name": "system", "description": "Службові речі типу здоров'я/версії/скріншоти"},
    ],
)

# віддаємо статичні файли (скріншоти і логотип)
app.mount("/static", StaticFiles(directory=str((__file__.replace("__init__.py","") + "static"))), name="static")

# -------------------------
# System routes (прості)
# -------------------------
@app.get(
    "/",
    summary="Домашня сторінка",
    description="Просто повертає невеличкий JSON, щоб показати що API живий.",
    tags=["system"],
)
def root():
    return {"hello": "openapi demo", "docs": "/docs", "openapi": "/openapi.json"}

@app.get(
    "/health",
    summary="Перевірка здоров'я",
    description="Повертає ok=true якщо все працює.",
    tags=["system"],
)
def health():
    return {"ok": True}

@app.get(
    "/screenshots/swagger-list",
    summary="Скрін: список ендпоінтів у Swagger",
    description="Повертає PNG-картинку (мок-скрін) з виглядом списку ендпоінтів у Swagger UI.",
    tags=["system"],
    responses={200: {"content": {"image/png": {}}}},
)
def shot_list():
    return FileResponse("app/static/screenshots/swagger_list.png", media_type="image/png")

@app.get(
    "/screenshots/swagger-try",
    summary="Скрін: приклад Try it out у Swagger",
    description="Повертає PNG-картинку (мок) з формою запиту та відповіддю.",
    tags=["system"],
    responses={200: {"content": {"image/png": {}}}},
)
def shot_try():
    return FileResponse("app/static/screenshots/swagger_try.png", media_type="image/png")

# -------------------------
# Movies routes (основні)
# -------------------------

@app.get(
    "/movies",
    response_model=List[Movie],
    summary="Отримати список фільмів",
    description=(
        "Повертає **всі** фільми з нашої маленької колекції.\n\n"
        "Можна одразу натиснути `Try it out` у Swagger і зробити `Execute`."
    ),
    tags=["movies"],
    responses={200: {"description": "Успішно"}},
)
def list_movies():
    return store.list()

@app.post(
    "/movies",
    response_model=Movie,
    status_code=201,
    summary="Додати новий фільм",
    description=(
        "Додає фільм. Перевіряється, щоб `release_year` не був з майбутнього, "
        "`rating` між 0 і 10, і `title/director` не пусті.\n\n"
        "У Swagger є приклад у тілі запиту."
    ),
    tags=["movies"],
    responses={
        201: {"description": "Створено"},
        422: {"description": "Помилка валідації"},
    },
)
def add_movie(data: MovieCreate):
    return store.create(data)

@app.get(
    "/movies/{movie_id}",
    response_model=Movie,
    summary="Отримати фільм за ID",
    description="Шукає фільм по `movie_id`. Якщо не знайдено — 404.",
    tags=["movies"],
    responses={404: {"description": "Movie not found"}},
)
def get_movie(movie_id: int):
    m = store.get(movie_id)
    if not m:
        raise HTTPException(status_code=404, detail="Movie not found")
    return m

@app.delete(
    "/movies/{movie_id}",
    status_code=204,
    summary="Видалити фільм",
    description="Видаляє фільм по `movie_id`. Якщо не знайдено — 404.",
    tags=["movies"],
    responses={204: {"description": "Видалено"}, 404: {"description": "Movie not found"}},
)
def delete_movie(movie_id: int):
    ok = store.delete(movie_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Movie not found")
    # FastAPI сам поверне пусту відповідь з 204
    return None

# -------------------------
# кастомізація OpenAPI
# -------------------------
def custom_openapi():
    # генеруємо стандартну схему
    openapi_schema = get_openapi(
        title="Movies API (Student Docs Demo)",
        version="1.0.1",  # bump версію щоб було видно зміну
        description="Тут я трошки змінив OpenAPI: додав логотип, контакт, ліцензію, servers, tags.",
        routes=app.routes
    )
    # додаю логотип (Swagger UI його у FastAPI не рендерить автоматично, але поле буде у схемі)
    openapi_schema.setdefault("info", {}).setdefault("x-logo", {"url": "/static/logo.png"})
    # контакт + ліцензія (просто для прикладу)
    openapi_schema["info"]["contact"] = {"name": "Student Dev", "email": "student@example.com"}
    openapi_schema["info"]["license"] = {"name": "MIT", "url": "https://opensource.org/licenses/MIT"}
    # додаткові сервери
    openapi_schema["servers"] = [
        {"url": "http://127.0.0.1:8000", "description": "Local Dev"},
        {"url": "https://api.example.com", "description": "Fake Prod"},
    ]
    # опис тегів (навіть якщо вже в app=... — тут ще раз явно)
    openapi_schema["tags"] = [
        {"name": "movies", "description": "Movie operations"},
        {"name": "system", "description": "Health, root, and helper endpoints"},
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# підміняємо генератор
app.openapi = custom_openapi

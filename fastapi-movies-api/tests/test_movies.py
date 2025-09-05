from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_add_and_get_movie_list_and_detail():
    payload = {
        "title": "Inception",
        "director": "Christopher Nolan",
        "release_year": 2010,
        "rating": 8.8
    }
    r = client.post("/movies", json=payload)
    assert r.status_code == 201
    m = r.json()
    assert m["id"] >= 1
    assert m["title"] == payload["title"]

    r2 = client.get("/movies")
    assert r2.status_code == 200
    items = r2.json()
    assert isinstance(items, list) and len(items) >= 1

    movie_id = m["id"]
    r3 = client.get(f"/movies/{movie_id}")
    assert r3.status_code == 200
    assert r3.json()["director"] == payload["director"]

def test_validation_future_year():
    payload = {
        "title": "Future Film",
        "director": "Someone",
        "release_year": 3000,
        "rating": 7.0
    }
    r = client.post("/movies", json=payload)
    assert r.status_code == 422  # Pydantic validation error

def test_validation_rating_and_title():
    payload = {
        "title": "   ",
        "director": "Dir",
        "release_year": 2020,
        "rating": 11.5
    }
    r = client.post("/movies", json=payload)
    assert r.status_code == 422

def test_delete_movie_and_404():
    payload = {
        "title": "Temp",
        "director": "X",
        "release_year": 2000,
        "rating": 5.0
    }
    r = client.post("/movies", json=payload)
    movie_id = r.json()["id"]

    d = client.delete(f"/movies/{movie_id}")
    assert d.status_code == 204

    g = client.get(f"/movies/{movie_id}")
    assert g.status_code == 404

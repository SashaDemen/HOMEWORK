from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)

def test_docs_and_openapi_available():
    r = c.get("/openapi.json")
    assert r.status_code == 200
    assert r.json()["info"]["title"].startswith("Movies API")
    d = c.get("/docs")
    # HTML сторінка Swagger UI
    assert d.status_code == 200

def test_movies_crud_and_validation():
    # create
    payload = {"title":"Inception","director":"Christopher Nolan","release_year":2010,"rating":8.8}
    r = c.post("/movies", json=payload)
    assert r.status_code == 201
    mid = r.json()["id"]
    # list
    r2 = c.get("/movies")
    assert r2.status_code == 200 and isinstance(r2.json(), list)
    # get
    r3 = c.get(f"/movies/{mid}")
    assert r3.status_code == 200 and r3.json()["title"] == "Inception"
    # validate: future year -> 422
    r4 = c.post("/movies", json={"title":"X","director":"Y","release_year":3000,"rating":5})
    assert r4.status_code == 422
    # delete
    d = c.delete(f"/movies/{mid}")
    assert d.status_code == 204

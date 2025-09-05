import time
from pathlib import Path
from fastapi.testclient import TestClient
from PIL import Image
from app.main import app
from app.settings import PROCESSED_DIR, MAX_FILE_SIZE_MB

client = TestClient(app)

def wait_task(tid, timeout=5):
    t0 = time.time()
    while time.time()-t0 < timeout:
        r = client.get(f"/tasks/{tid}")
        if r.status_code == 200 and r.json()["status"] in ("DONE","ERROR"):
            return r.json()
        time.sleep(0.05)
    return None

def test_upload_and_process_png(tmp_path):
    p = tmp_path/"x.png"
    Image.new("RGB",(300,200),(120,160,200)).save(p)
    with p.open("rb") as f:
        r = client.post("/gallery/upload", files={"files": ("x.png", f, "image/png")})
    assert r.status_code == 202
    tid = r.json()["task_ids"][0]
    t = wait_task(tid)
    assert t and t["status"] == "DONE"
    out = Path(t["result"])
    assert out.exists()
    assert out.suffix == ".webp"

def test_reject_wrong_type(tmp_path):
    p = tmp_path/"a.txt"
    p.write_text("hello")
    with p.open("rb") as f:
        r = client.post("/gallery/upload", files={"files": ("a.txt", f, "text/plain")})
    assert r.status_code == 400
    assert "unsupported type" in r.text

def test_reject_large_file(tmp_path):
    size = (MAX_FILE_SIZE_MB*1024*1024) + 1024
    big = tmp_path/"big.bin"
    big.write_bytes(b"0"*int(size))
    with big.open("rb") as f:
        r = client.post("/gallery/upload", files={"files": ("big.png", f, "image/png")})
    assert r.status_code == 400
    assert "file too large" in r.text

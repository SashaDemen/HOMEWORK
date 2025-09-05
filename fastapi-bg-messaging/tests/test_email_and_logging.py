import os, time
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.settings import LOG_FILE, OUTBOX_DIR

client = TestClient(app)

def test_email_send_and_log(tmp_path, monkeypatch):
    # Redirect base dirs to temp if needed (not necessary here, using defaults)
    if LOG_FILE.exists():
        LOG_FILE.unlink()

    r = client.post("/emails/send", json={
        "user": {"email":"test@example.com","name":"T"},
        "subject":"Hi",
        "body":"Body"
    })
    assert r.status_code == 202
    tid = r.json()["id"]
    # Wait for worker
    for _ in range(50):
        s = client.get(f"/tasks/{tid}")
        if s.json()["status"] in ("DONE","ERROR"):
            break
        time.sleep(0.05)
    data = s.json()
    assert data["status"] == "DONE"
    # Email file exists
    out = Path(data["result"])
    assert out.exists()
    # Log file contains entries
    time.sleep(0.05)
    text = LOG_FILE.read_text(encoding="utf-8")
    assert "ACTION=email_request" in text
    assert "ACTION=email_send_done" in text

def test_upload_and_process_image(tmp_path):
    # Create a small image
    from PIL import Image
    img_path = tmp_path/"x.png"
    Image.new("RGB", (200, 200), (100, 150, 200)).save(img_path)
    with img_path.open("rb") as f:
        r = client.post("/files/upload", files={"files": ("x.png", f, "image/png")})
    assert r.status_code == 202
    tids = r.json()["task_ids"]
    assert tids and isinstance(tids, list)
    # wait
    for tid in tids:
        for _ in range(50):
            s = client.get(f"/tasks/{tid}")
            if s.json()["status"] in ("DONE","ERROR"):
                break
            time.sleep(0.05)
        assert s.json()["status"] == "DONE"

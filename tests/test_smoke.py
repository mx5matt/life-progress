import os
import tempfile

db_file = tempfile.NamedTemporaryFile(delete=False)
db_file.close()
os.environ["LIFE_PROGRESS_DB"] = db_file.name

from app.app import app, init_db

init_db()
client = app.test_client()

response = client.get("/health")
assert response.status_code == 200
assert response.get_json()["status"] == "ok"

response = client.get("/")
assert response.status_code == 302

os.unlink(db_file.name)
print("Smoke tests passed.")

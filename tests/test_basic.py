from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_serves_index():
    r = client.get('/')
    assert r.status_code == 200
    assert 'API Veterinaria' in r.text


def test_healthz_default_ok():
    r = client.get('/healthz')
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

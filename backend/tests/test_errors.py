from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.errors import AppError, register_exception_handlers


class _Body(BaseModel):
    name: str


def _make_test_app() -> FastAPI:
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/boom")
    def boom() -> None:
        raise AppError(400, "TEST_ERROR", "test mesajı")

    @test_app.post("/validate")
    def validate(payload: _Body) -> dict:
        return {"ok": True}

    return test_app


def test_app_error_format():
    client = TestClient(_make_test_app())
    response = client.get("/boom")
    assert response.status_code == 400
    assert response.json() == {"detail": "test mesajı", "code": "TEST_ERROR"}


def test_validation_error_format():
    client = TestClient(_make_test_app())
    response = client.post("/validate", json={})
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert body["detail"] == "Lütfen form alanlarını kontrol edin"
    assert body["errors"][0]["field"] == "name"
    assert body["errors"][0]["message"] == "Bu alan zorunlu"


def test_unknown_route_404_format(client):
    response = client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "NOT_FOUND"

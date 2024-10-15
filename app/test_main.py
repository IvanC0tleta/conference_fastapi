import pytest
from fastapi.testclient import TestClient
from .main import app, get_db, Base
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import Session
from . import models


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
            yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_index(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong!"}


def test_create_presentation(session: Session, client: TestClient):
    test_user = models.User(username="test_user", role=models.Roles.Presenter)
    session.add(test_user)
    session.commit()

    response = client.post("/presentations/create", json={
        "title": "test_presentation",
        "presenters": test_user.username
    })

    data = response.json()

    assert response.status_code == 200
    assert data["title"] == "test_presentation"
    assert data["presenters"][0]["username"] == test_user.username


def test_create_presentation_invalid(session: Session, client: TestClient):
    test_user = models.User(username="test_user", role=models.Roles.Listener)
    session.add(test_user)
    session.commit()

    response = client.post("/presentations/create", json={
        "title": "test_presentation",
        "presenters": test_user.username
    })

    assert response.status_code == 400


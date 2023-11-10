import pytest
from website import create_app, db
from website.models import User

@pytest.fixture()
def app():
    app = create_app("sqlite://")

    with app.app_context():
        db.create_all()

    print("CREATING DATABASE")

    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

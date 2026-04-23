"""
Placeholder test suite for FitAct CI/CD pipeline.

These tests verify the application can be created and configured correctly.
Full test coverage will be implemented in the Testing phase of the project.
"""

import pytest
from app import create_app, db


@pytest.fixture
def app():
    """Create a FitAct app instance configured for testing with SQLite."""
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///test_fitact.db",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "fitact-test-secret-key",
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Return a test client for the FitAct app."""
    return app.test_client()


def test_app_created_successfully(app):
    """Verify the FitAct application factory creates an app instance."""
    assert app is not None


def test_app_is_in_testing_mode(app):
    """Verify the app is correctly configured in testing mode."""
    assert app.config["TESTING"] is True


def test_app_uses_sqlite_in_tests(app):
    """Verify the test database is SQLite, not the production database."""
    assert "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]


def test_home_page_returns_200(client):
    """Verify the home/landing page redirects and resolves successfully."""
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200


def test_login_page_returns_200(client):
    """Verify the login page is accessible."""
    response = client.get("/login")
    assert response.status_code == 200


def test_signup_page_returns_200(client):
    """Verify the register page is accessible."""
    response = client.get("/register")
    assert response.status_code == 200

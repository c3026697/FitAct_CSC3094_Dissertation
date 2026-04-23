"""
Tests for FR10 — User Account Creation and Login.

FR10: The system shall allow users to create an account and log in
to securely store and retrieve their allocated programme, saved
workouts, and progress history across multiple sessions.
"""

import pytest


class TestRegistration:
    """FR10 — User registration behaviour."""

    def test_register_page_loads(self, client, db):
        """Register page returns HTTP 200."""
        response = client.get("/register")
        assert response.status_code == 200

    def test_register_valid_user(self, client, db):
        """
        A user with valid credentials is registered successfully
        and redirected to the success page.
        """
        response = client.post(
            "/register",
            data={
                "username": "newuser",
                "email": "new@fitact.com",
                "password": "Test@1234",
                "confirm_password": "Test@1234",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_register_creates_user_in_database(self, client, db):
        """A registered user exists in the database after sign-up."""
        from app.models import User

        client.post(
            "/register",
            data={
                "username": "dbuser",
                "email": "db@fitact.com",
                "password": "Test@1234",
                "confirm_password": "Test@1234",
            },
        )
        with client.application.app_context():
            user = User.query.filter_by(email="db@fitact.com").first()
            assert user is not None
            assert user.username == "dbuser"

    def test_register_password_is_hashed(self, client, db):
        """The stored password hash is not the plain-text password."""
        from app.models import User

        client.post(
            "/register",
            data={
                "username": "hashuser",
                "email": "hash@fitact.com",
                "password": "Test@1234",
                "confirm_password": "Test@1234",
            },
        )
        with client.application.app_context():
            user = User.query.filter_by(email="hash@fitact.com").first()
            assert user.password_hash != "Test@1234"

    def test_register_duplicate_email_rejected(self, client, db):
        """Registering with an already-used email is rejected."""
        data = {
            "username": "user1",
            "email": "dup@fitact.com",
            "password": "Test@1234",
            "confirm_password": "Test@1234",
        }
        client.post("/register", data=data)
        data["username"] = "user2"
        response = client.post("/register", data=data, follow_redirects=True)
        assert b"already exists" in response.data

    def test_register_duplicate_username_rejected(self, client, db):
        """Registering with an already-used username is rejected."""
        data = {
            "username": "sameuser",
            "email": "first@fitact.com",
            "password": "Test@1234",
            "confirm_password": "Test@1234",
        }
        client.post("/register", data=data)
        data["email"] = "second@fitact.com"
        response = client.post("/register", data=data, follow_redirects=True)
        assert b"already taken" in response.data

    def test_register_password_mismatch_rejected(self, client, db):
        """Registration fails when passwords do not match."""
        response = client.post(
            "/register",
            data={
                "username": "mismatch",
                "email": "mismatch@fitact.com",
                "password": "Test@1234",
                "confirm_password": "Different@1234",
            },
            follow_redirects=True,
        )
        assert b"do not match" in response.data

    def test_register_short_username_rejected(self, client, db):
        """Registration fails when username is fewer than 3 characters."""
        response = client.post(
            "/register",
            data={
                "username": "ab",
                "email": "short@fitact.com",
                "password": "Test@1234",
                "confirm_password": "Test@1234",
            },
            follow_redirects=True,
        )
        assert b"at least 3" in response.data

    def test_register_weak_password_no_uppercase_rejected(self, client, db):
        """Registration fails when password has no uppercase letter."""
        response = client.post(
            "/register",
            data={
                "username": "weakuser",
                "email": "weak@fitact.com",
                "password": "test@1234",
                "confirm_password": "test@1234",
            },
            follow_redirects=True,
        )
        assert b"uppercase" in response.data

    def test_register_weak_password_no_digit_rejected(self, client, db):
        """Registration fails when password has no digit."""
        response = client.post(
            "/register",
            data={
                "username": "nodigit",
                "email": "nodigit@fitact.com",
                "password": "Test@abcd",
                "confirm_password": "Test@abcd",
            },
            follow_redirects=True,
        )
        assert b"digit" in response.data

    def test_register_weak_password_no_special_char_rejected(self, client, db):
        """Registration fails when password has no special character."""
        response = client.post(
            "/register",
            data={
                "username": "nospecial",
                "email": "nospecial@fitact.com",
                "password": "Test12345",
                "confirm_password": "Test12345",
            },
            follow_redirects=True,
        )
        assert b"special" in response.data

    def test_register_password_too_short_rejected(self, client, db):
        """Registration fails when password is fewer than 8 characters."""
        response = client.post(
            "/register",
            data={
                "username": "tooshort",
                "email": "tooshort@fitact.com",
                "password": "T@1",
                "confirm_password": "T@1",
            },
            follow_redirects=True,
        )
        assert b"between 8" in response.data

    def test_register_password_too_long_rejected(self, client, db):
        """Registration fails when password exceeds 15 characters."""
        response = client.post(
            "/register",
            data={
                "username": "toolong",
                "email": "toolong@fitact.com",
                "password": "Test@12345678901",
                "confirm_password": "Test@12345678901",
            },
            follow_redirects=True,
        )
        assert b"between 8" in response.data


class TestLogin:
    """FR10 — User login behaviour."""

    def test_login_page_loads(self, client, db):
        """Login page returns HTTP 200."""
        response = client.get("/login")
        assert response.status_code == 200

    def test_login_valid_credentials(self, client, seeded_db):
        """A registered user can log in with correct credentials."""
        client.post(
            "/register",
            data={
                "username": "loginuser",
                "email": "login@fitact.com",
                "password": "Test@1234",
                "confirm_password": "Test@1234",
            },
        )
        response = client.post(
            "/login",
            data={"email": "login@fitact.com", "password": "Test@1234"},
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_login_invalid_password_rejected(self, client, seeded_db):
        """Login fails with an incorrect password."""
        client.post(
            "/register",
            data={
                "username": "wrongpass",
                "email": "wrongpass@fitact.com",
                "password": "Test@1234",
                "confirm_password": "Test@1234",
            },
        )
        response = client.post(
            "/login",
            data={"email": "wrongpass@fitact.com", "password": "WrongPass@99"},
            follow_redirects=True,
        )
        assert b"Invalid email or password" in response.data

    def test_login_nonexistent_user_rejected(self, client, db):
        """Login fails for an email that does not exist."""
        response = client.post(
            "/login",
            data={"email": "nobody@fitact.com", "password": "Test@1234"},
            follow_redirects=True,
        )
        assert b"Invalid email or password" in response.data

    def test_login_redirects_to_questionnaire_without_programme(
        self, client, seeded_db
    ):
        """
        A user with no allocated programme is redirected to the
        questionnaire after login (FR1 onboarding flow).
        """
        client.post(
            "/register",
            data={
                "username": "noprog",
                "email": "noprog@fitact.com",
                "password": "Test@1234",
                "confirm_password": "Test@1234",
            },
        )
        response = client.post(
            "/login",
            data={"email": "noprog@fitact.com", "password": "Test@1234"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/questionnaire" in response.location

    def test_login_redirects_to_workout_with_programme(self, client, seeded_db):
        """
        A user with an allocated programme is redirected to the
        workout page after login (FR3).
        """
        from app.extensions import db
        from app.models import User

        client.post(
            "/register",
            data={
                "username": "withprog",
                "email": "withprog@fitact.com",
                "password": "Test@1234",
                "confirm_password": "Test@1234",
            },
        )
        with client.application.app_context():
            user = User.query.filter_by(email="withprog@fitact.com").first()
            user.current_programme_id = seeded_db["programme"].id
            db.session.commit()

        response = client.post(
            "/login",
            data={"email": "withprog@fitact.com", "password": "Test@1234"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/workout" in response.location


class TestLogout:
    """FR10 — User logout behaviour."""

    def test_logout_redirects_to_login(self, logged_in_client_with_programme):
        """Logging out redirects the user to the login page."""
        response = logged_in_client_with_programme.get(
            "/logout", follow_redirects=False
        )
        assert response.status_code == 302
        assert "/login" in response.location

    def test_logout_ends_session(self, logged_in_client_with_programme):
        """After logout, protected routes redirect to login."""
        logged_in_client_with_programme.get("/logout", follow_redirects=True)
        response = logged_in_client_with_programme.get(
            "/workout", follow_redirects=False
        )
        assert response.status_code == 302
        assert "/login" in response.location

"""
Shared pytest fixtures for the FitAct test suite.

Provides the app, db, client, and authenticated client fixtures
used across all test modules. All tests run against an in-memory
SQLite database to ensure isolation from production data.
"""

import pytest

from app import create_app
from app.extensions import db as _db
from app.models import (
    Achievement,
    Exercise,
    Programme,
    ProgrammeWorkout,
    User,
    Workout,
    WorkoutExercise,
)
from config import TestingConfig


@pytest.fixture(scope="session")
def app():
    """Create a FitAct app instance configured for testing."""
    app = create_app(TestingConfig)
    with app.app_context():
        yield app


@pytest.fixture(scope="function")
def db(app):
    """Create all tables before each test and drop them after."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app, db):
    """Return a Flask test client with a clean database."""
    return app.test_client()


@pytest.fixture(scope="function")
def seeded_db(db):
    """
    Seed the test database with the minimum data required for most tests.

    Inserts:
        - 1 Exercise (Bench Press)
        - 2 Workouts (Upper Body A, Full Body A)
        - 2 Programmes (3-Day Full Body, 2-Day Full Body)
        - 1 Achievement (first_workout milestone)
    """
    exercise = Exercise(
        name="Bench Press",
        muscle_group="Chest",
        guidance_text="Lie flat on a bench and press the bar upward.",
    )
    _db.session.add(exercise)
    _db.session.flush()

    workout = Workout(name="Upper Body A", type="Upper", is_custom=False)
    _db.session.add(workout)
    _db.session.flush()

    we = WorkoutExercise(
        workout_id=workout.id,
        exercise_id=exercise.id,
        sets_target=3,
        reps_target=8,
        exercise_order=1,
    )
    _db.session.add(we)

    workout2 = Workout(name="Full Body A", type="Full Body", is_custom=False)
    _db.session.add(workout2)
    _db.session.flush()

    we2 = WorkoutExercise(
        workout_id=workout2.id,
        exercise_id=exercise.id,
        sets_target=3,
        reps_target=10,
        exercise_order=1,
    )
    _db.session.add(we2)

    programme = Programme(
        name="3-Day Full Body",
        split_type="Full Body",
        description="A three-day full body programme.",
    )
    _db.session.add(programme)
    _db.session.flush()

    pw = ProgrammeWorkout(
        programme_id=programme.id,
        workout_id=workout.id,
        day_number=1,
        workout_order=1,
    )
    _db.session.add(pw)

    programme2 = Programme(
        name="2-Day Full Body",
        split_type="Full Body",
        description="A two-day full body programme.",
    )
    _db.session.add(programme2)
    _db.session.flush()

    pw2 = ProgrammeWorkout(
        programme_id=programme2.id,
        workout_id=workout2.id,
        day_number=1,
        workout_order=1,
    )
    _db.session.add(pw2)

    achievement = Achievement(
        title="First Workout Completed",
        description="You completed your very first workout!",
        milestone_type="first_workout",
    )
    _db.session.add(achievement)
    _db.session.commit()

    return {
        "exercise": exercise,
        "workout": workout,
        "workout2": workout2,
        "programme": programme,
        "programme2": programme2,
        "achievement": achievement,
    }


@pytest.fixture(scope="function")
def registered_user(client, seeded_db):
    """Register a test user and return their credentials."""
    client.post(
        "/register",
        data={
            "username": "testuser",
            "email": "test@fitact.com",
            "password": "Test@1234",
            "confirm_password": "Test@1234",
        },
    )
    return {"username": "testuser", "email": "test@fitact.com", "password": "Test@1234"}


@pytest.fixture(scope="function")
def logged_in_client(client, registered_user, seeded_db):
    """Return a test client with an authenticated session."""
    client.post(
        "/login",
        data={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
        follow_redirects=True,
    )
    return client


@pytest.fixture(scope="function")
def logged_in_client_with_programme(client, registered_user, seeded_db):
    """
    Return an authenticated client where the user already has
    a programme allocated (skips the questionnaire redirect).
    """
    from app.extensions import db
    from app.models import User

    # First assign the programme BEFORE logging in
    with client.application.app_context():
        user = User.query.filter_by(email=registered_user["email"]).first()
        user.current_programme_id = seeded_db["programme"].id
        db.session.commit()

    # Then log in
    client.post(
        "/login",
        data={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
        follow_redirects=True,
    )

    return client

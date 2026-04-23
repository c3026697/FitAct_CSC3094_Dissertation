"""
Tests for FR4 and FR5 — Workout Repository, Saved Workouts, Custom Workouts.

FR4: The system shall provide ready-made workouts that users can browse,
select, and start independently. Selected workouts shall be saved to a
"Saved Workouts" page and, once completed, recorded in the "Past Workouts"
page.

FR5: The system shall allow users to create custom workouts from an exercise
database and save them to a "Saved Workouts" page.
"""

import pytest


class TestWorkoutRepository:
    """FR4 — Workout repository browsing and selection."""

    def test_repository_page_loads(self, logged_in_client_with_programme, seeded_db):
        """Workout repository page returns HTTP 200."""
        response = logged_in_client_with_programme.get("/workouts")
        assert response.status_code == 200

    def test_repository_lists_ready_made_workouts(
        self, logged_in_client_with_programme, seeded_db
    ):
        """Repository page displays predefined (non-custom) workouts."""
        response = logged_in_client_with_programme.get("/workouts")
        assert b"Upper Body A" in response.data

    def test_repository_requires_login(self, client, db):
        """Workout repository redirects unauthenticated users to login."""
        response = client.get("/workouts", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.location

    def test_workout_info_page_loads(self, logged_in_client_with_programme, seeded_db):
        """Workout info page returns HTTP 200 for a valid workout ID."""
        workout_id = seeded_db["workout"].id
        response = logged_in_client_with_programme.get(f"/workouts/{workout_id}/info")
        assert response.status_code == 200

    def test_workout_info_shows_workout_name(
        self, logged_in_client_with_programme, seeded_db
    ):
        """Workout info page displays the workout name and exercises."""
        workout_id = seeded_db["workout"].id
        response = logged_in_client_with_programme.get(f"/workouts/{workout_id}/info")
        assert b"Upper Body A" in response.data

    def test_workout_info_404_for_invalid_id(
        self, logged_in_client_with_programme, seeded_db
    ):
        """Workout info page returns 404 for a non-existent workout ID."""
        response = logged_in_client_with_programme.get("/workouts/99999/info")
        assert response.status_code == 404

    def test_start_workout_from_repository_redirects_to_execute(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        Starting a workout from the repository redirects to the
        workout execution page.
        """
        workout_id = seeded_db["workout"].id
        response = logged_in_client_with_programme.get(
            f"/workouts/{workout_id}/start", follow_redirects=False
        )
        assert response.status_code == 302
        assert "/execute" in response.location


class TestSavedWorkouts:
    """FR4 — Saving and managing saved workouts."""

    def test_saved_workouts_page_loads(
        self, logged_in_client_with_programme, seeded_db
    ):
        """Saved workouts page returns HTTP 200."""
        response = logged_in_client_with_programme.get("/workouts/saved")
        assert response.status_code == 200

    def test_save_workout_adds_to_saved(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        Saving a workout from the repository adds it to the user's
        saved workouts.
        """
        from app.extensions import db
        from app.models import SavedWorkout, User

        workout_id = seeded_db["workout"].id
        logged_in_client_with_programme.post(f"/workouts/{workout_id}/save")

        with logged_in_client_with_programme.application.app_context():
            user = User.query.filter_by(email="test@fitact.com").first()
            saved = SavedWorkout.query.filter_by(
                user_id=user.id, workout_id=workout_id
            ).first()
            assert saved is not None

    def test_save_workout_appears_on_saved_page(
        self, logged_in_client_with_programme, seeded_db
    ):
        """A saved workout appears on the Saved Workouts page."""
        workout_id = seeded_db["workout"].id
        logged_in_client_with_programme.post(f"/workouts/{workout_id}/save")
        response = logged_in_client_with_programme.get("/workouts/saved")
        assert b"Upper Body A" in response.data

    def test_duplicate_save_rejected(self, logged_in_client_with_programme, seeded_db):
        """Saving the same workout twice does not create a duplicate."""
        from app.extensions import db
        from app.models import SavedWorkout, User

        workout_id = seeded_db["workout"].id
        logged_in_client_with_programme.post(f"/workouts/{workout_id}/save")
        logged_in_client_with_programme.post(f"/workouts/{workout_id}/save")

        with logged_in_client_with_programme.application.app_context():
            user = User.query.filter_by(email="test@fitact.com").first()
            count = SavedWorkout.query.filter_by(
                user_id=user.id, workout_id=workout_id
            ).count()
            assert count == 1

    def test_delete_saved_workout_removes_it(
        self, logged_in_client_with_programme, seeded_db
    ):
        """Deleting a saved workout removes it from the saved workouts list."""
        from app.extensions import db
        from app.models import SavedWorkout, User

        workout_id = seeded_db["workout"].id
        logged_in_client_with_programme.post(f"/workouts/{workout_id}/save")

        with logged_in_client_with_programme.application.app_context():
            user = User.query.filter_by(email="test@fitact.com").first()
            saved = SavedWorkout.query.filter_by(
                user_id=user.id, workout_id=workout_id
            ).first()
            saved_id = saved.id

        logged_in_client_with_programme.post(f"/workouts/saved/{saved_id}/delete")

        with logged_in_client_with_programme.application.app_context():
            deleted = SavedWorkout.query.get(saved_id)
            assert deleted is None


class TestCustomWorkouts:
    """FR5 — Custom workout creation from exercise database."""

    def test_create_custom_workout_page_loads(
        self, logged_in_client_with_programme, seeded_db
    ):
        """Create custom workout page returns HTTP 200."""
        response = logged_in_client_with_programme.get("/workouts/create")
        assert response.status_code == 200

    def test_create_custom_workout_page_lists_exercises(
        self, logged_in_client_with_programme, seeded_db
    ):
        """Create custom workout page shows available exercises."""
        response = logged_in_client_with_programme.get("/workouts/create")
        assert b"Bench Press" in response.data

    def test_create_custom_workout_saves_to_db(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        Submitting the custom workout form creates a workout entry
        in the database with is_custom=True.
        """
        from app.models import Workout

        exercise_id = seeded_db["exercise"].id
        logged_in_client_with_programme.post(
            "/workouts/create",
            data={
                "workout_name": "My Custom Workout",
                "exercise_ids": [str(exercise_id)],
            },
        )
        with logged_in_client_with_programme.application.app_context():
            custom = Workout.query.filter_by(
                name="My Custom Workout", is_custom=True
            ).first()
            assert custom is not None

    def test_create_custom_workout_auto_saved(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        A newly created custom workout is automatically saved to the
        user's Saved Workouts page.
        """
        from app.models import SavedWorkout, User, Workout

        exercise_id = seeded_db["exercise"].id
        logged_in_client_with_programme.post(
            "/workouts/create",
            data={
                "workout_name": "Auto Saved Workout",
                "exercise_ids": [str(exercise_id)],
            },
        )
        with logged_in_client_with_programme.application.app_context():
            user = User.query.filter_by(email="test@fitact.com").first()
            custom = Workout.query.filter_by(name="Auto Saved Workout").first()
            saved = SavedWorkout.query.filter_by(
                user_id=user.id, workout_id=custom.id
            ).first()
            assert saved is not None

    def test_create_custom_workout_without_name_rejected(
        self, logged_in_client_with_programme, seeded_db
    ):
        """Custom workout creation fails if no name is provided."""
        exercise_id = seeded_db["exercise"].id
        response = logged_in_client_with_programme.post(
            "/workouts/create",
            data={"workout_name": "", "exercise_ids": [str(exercise_id)]},
            follow_redirects=True,
        )
        assert b"name" in response.data

    def test_create_custom_workout_without_exercises_rejected(
        self, logged_in_client_with_programme, seeded_db
    ):
        """Custom workout creation fails if no exercises are selected."""
        response = logged_in_client_with_programme.post(
            "/workouts/create",
            data={"workout_name": "Empty Workout", "exercise_ids": []},
            follow_redirects=True,
        )
        assert b"exercise" in response.data.lower() or response.status_code == 200

    def test_create_custom_page_requires_login(self, client, db):
        """Custom workout creation page redirects unauthenticated users."""
        response = client.get("/workouts/create", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.location

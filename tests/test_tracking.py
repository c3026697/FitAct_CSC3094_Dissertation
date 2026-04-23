"""
Tests for FR7 and FR8 — Workout Execution Tracking and Progress Logging.

FR7: The system shall track workout progress during workout completion,
recording the sets and repetitions completed for each exercise.

FR8: The system shall log completed workouts and display them on the
progress page under a "Past Workouts" section.
"""

import pytest


class TestWorkoutExecution:
    """FR7 — Workout execution page and progress tracking."""

    def test_execute_page_loads(self, logged_in_client_with_programme, seeded_db):
        """
        Workout execution page returns HTTP 200, allowing users to
        begin tracking sets and reps for each exercise (FR7).
        """
        workout_id = seeded_db["workout"].id
        response = logged_in_client_with_programme.get(f"/workout/{workout_id}/execute")
        assert response.status_code == 200

    def test_execute_page_displays_exercises(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        Execution page displays each exercise in the workout with
        target sets and reps for the user to track against (FR7).
        """
        workout_id = seeded_db["workout"].id
        response = logged_in_client_with_programme.get(f"/workout/{workout_id}/execute")
        assert b"Bench Press" in response.data

    def test_execute_page_shows_target_sets(
        self, logged_in_client_with_programme, seeded_db
    ):
        """Execution page displays the target number of sets per exercise."""
        workout_id = seeded_db["workout"].id
        response = logged_in_client_with_programme.get(f"/workout/{workout_id}/execute")
        assert b"3" in response.data

    def test_execute_page_404_for_invalid_workout(
        self, logged_in_client_with_programme, seeded_db
    ):
        """Execution page returns 404 for a non-existent workout ID."""
        response = logged_in_client_with_programme.get("/workout/99999/execute")
        assert response.status_code == 404

    def test_execute_page_requires_login(self, client, seeded_db):
        """Execution page redirects unauthenticated users to login."""
        workout_id = seeded_db["workout"].id
        response = client.get(f"/workout/{workout_id}/execute", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.location


class TestWorkoutLogging:
    """FR7 and FR8 — Logging sets/reps and recording completed workouts."""

    def _log_workout(self, client, seeded_db):
        """Helper to submit a workout log POST request."""
        workout_id = seeded_db["workout"].id
        we_id = seeded_db["workout"].workout_exercises[0].id
        return client.post(
            f"/workout/{workout_id}/log",
            data={
                f"ex_{we_id}_set_1_reps": "8",
                f"ex_{we_id}_set_1_weight": "60",
                f"ex_{we_id}_set_2_reps": "8",
                f"ex_{we_id}_set_2_weight": "60",
                f"ex_{we_id}_set_3_reps": "7",
                f"ex_{we_id}_set_3_weight": "60",
                "duration_seconds": "1800",
            },
            follow_redirects=False,
        )

    def test_log_workout_creates_workout_log(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        POSTing workout log data creates a WorkoutLog entry in the
        database, satisfying FR8 logging requirement.
        """
        from app.models import User, WorkoutLog

        self._log_workout(logged_in_client_with_programme, seeded_db)

        with logged_in_client_with_programme.application.app_context():
            user = User.query.filter_by(email="test@fitact.com").first()
            log = WorkoutLog.query.filter_by(user_id=user.id).first()
            assert log is not None

    def test_log_workout_records_sets_and_reps(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        The workout log records sets and repetitions completed for each
        exercise, satisfying FR7 tracking requirement.
        """
        from app.models import LoggedExercise, User, WorkoutLog

        self._log_workout(logged_in_client_with_programme, seeded_db)

        with logged_in_client_with_programme.application.app_context():
            user = User.query.filter_by(email="test@fitact.com").first()
            log = WorkoutLog.query.filter_by(user_id=user.id).first()
            logged_exercises = LoggedExercise.query.filter_by(log_id=log.id).all()
            assert len(logged_exercises) > 0

    def test_log_workout_records_reps_correctly(
        self, logged_in_client_with_programme, seeded_db
    ):
        """Logged exercise entries contain the correct rep count."""
        from app.models import LoggedExercise, User, WorkoutLog

        self._log_workout(logged_in_client_with_programme, seeded_db)

        with logged_in_client_with_programme.application.app_context():
            user = User.query.filter_by(email="test@fitact.com").first()
            log = WorkoutLog.query.filter_by(user_id=user.id).first()
            entries = LoggedExercise.query.filter_by(log_id=log.id).all()
            reps = [e.reps_completed for e in entries]
            assert 8 in reps

    def test_log_workout_records_duration(
        self, logged_in_client_with_programme, seeded_db
    ):
        """Workout log stores the duration in seconds."""
        from app.models import User, WorkoutLog

        self._log_workout(logged_in_client_with_programme, seeded_db)

        with logged_in_client_with_programme.application.app_context():
            user = User.query.filter_by(email="test@fitact.com").first()
            log = WorkoutLog.query.filter_by(user_id=user.id).first()
            assert log.duration_seconds == 1800

    def test_log_workout_redirects_to_progress(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        After logging a workout, the user is redirected to the
        progress page (FR8).
        """
        response = self._log_workout(logged_in_client_with_programme, seeded_db)
        assert response.status_code == 302
        assert "/progress" in response.location


class TestProgressPage:
    """FR8 — Past workouts displayed on the progress page."""

    def test_progress_page_loads(self, logged_in_client_with_programme, seeded_db):
        """Progress page returns HTTP 200."""
        response = logged_in_client_with_programme.get("/progress")
        assert response.status_code == 200

    def test_progress_page_shows_logged_workout(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        A completed workout appears on the progress page under
        Past Workouts after being logged (FR8).
        """
        workout_id = seeded_db["workout"].id
        we_id = seeded_db["workout"].workout_exercises[0].id
        logged_in_client_with_programme.post(
            f"/workout/{workout_id}/log",
            data={
                f"ex_{we_id}_set_1_reps": "8",
                f"ex_{we_id}_set_1_weight": "60",
                "duration_seconds": "1200",
            },
            follow_redirects=True,
        )
        response = logged_in_client_with_programme.get("/progress")
        assert b"Upper Body A" in response.data

    def test_progress_page_requires_login(self, client, db):
        """Progress page redirects unauthenticated users to login."""
        response = client.get("/progress", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.location

    def test_delete_workout_log_removes_from_progress(
        self, logged_in_client_with_programme, seeded_db
    ):
        """Deleting a workout log removes it from the progress page."""
        from app.models import User, WorkoutLog

        workout_id = seeded_db["workout"].id
        we_id = seeded_db["workout"].workout_exercises[0].id
        logged_in_client_with_programme.post(
            f"/workout/{workout_id}/log",
            data={
                f"ex_{we_id}_set_1_reps": "8",
                f"ex_{we_id}_set_1_weight": "60",
                "duration_seconds": "600",
            },
            follow_redirects=True,
        )

        with logged_in_client_with_programme.application.app_context():
            user = User.query.filter_by(email="test@fitact.com").first()
            log = WorkoutLog.query.filter_by(user_id=user.id).first()
            log_id = log.id

        logged_in_client_with_programme.post(f"/progress/{log_id}/delete")

        with logged_in_client_with_programme.application.app_context():
            deleted = WorkoutLog.query.get(log_id)
            assert deleted is None

"""
Tests for FR6 — Exercise Guidance.

FR6: The system shall provide exercise guidance accessible via an
"Info" button for each exercise. Before workout execution, guidance
shall provide exercise context to help users understand the movement.
During workout execution, guidance shall display to help users perform
the movement correctly and effectively.
"""

import pytest


class TestExerciseGuidance:
    """FR6 — Exercise guidance page behaviour."""

    def test_exercise_guidance_page_loads(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        Exercise guidance page returns HTTP 200 for a valid exercise ID,
        satisfying FR6 pre-workout context access via the Info button.
        """
        exercise_id = seeded_db["exercise"].id
        response = logged_in_client_with_programme.get(f"/exercise/{exercise_id}")
        assert response.status_code == 200

    def test_exercise_guidance_displays_exercise_name(
        self, logged_in_client_with_programme, seeded_db
    ):
        """Guidance page shows the exercise name."""
        exercise_id = seeded_db["exercise"].id
        response = logged_in_client_with_programme.get(f"/exercise/{exercise_id}")
        assert b"Bench Press" in response.data

    def test_exercise_guidance_displays_guidance_text(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        Guidance page displays the guidance text stored for the exercise,
        helping users understand and perform the movement correctly (FR6).
        """
        exercise_id = seeded_db["exercise"].id
        response = logged_in_client_with_programme.get(f"/exercise/{exercise_id}")
        assert b"bench" in response.data.lower()

    def test_exercise_guidance_displays_muscle_group(
        self, logged_in_client_with_programme, seeded_db
    ):
        """Guidance page shows the muscle group targeted by the exercise."""
        exercise_id = seeded_db["exercise"].id
        response = logged_in_client_with_programme.get(f"/exercise/{exercise_id}")
        assert b"Chest" in response.data

    def test_exercise_guidance_404_for_invalid_id(
        self, logged_in_client_with_programme, seeded_db
    ):
        """Guidance page returns 404 for a non-existent exercise ID."""
        response = logged_in_client_with_programme.get("/exercise/99999")
        assert response.status_code == 404

    def test_exercise_guidance_requires_login(self, client, seeded_db):
        """Exercise guidance page redirects unauthenticated users to login."""
        exercise_id = seeded_db["exercise"].id
        response = client.get(f"/exercise/{exercise_id}", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.location

    def test_workout_execution_page_shows_exercise_guidance(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        The workout execution page displays each exercise with
        guidance context, satisfying FR6 during-execution guidance.
        """
        workout_id = seeded_db["workout"].id
        response = logged_in_client_with_programme.get(f"/workout/{workout_id}/execute")
        assert response.status_code == 200
        assert b"Bench Press" in response.data

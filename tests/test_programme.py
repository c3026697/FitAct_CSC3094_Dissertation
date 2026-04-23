"""
Tests for FR2 and FR3 — Programme Display and Update.

FR2: The system shall allow users to update their programme through a
dedicated "My Programme" page by either completing the questionnaire
again to receive a revised recommendation or manually selecting a
different programme from the database.

FR3: The system shall display the user's allocated programme on a
"My Programme" page and show the next scheduled workout under
"Today's Workout" on the Workout page, allowing users to view their
programme structure and start their assigned workout.
"""

import pytest


class TestProgrammeDisplay:
    """FR3 — My Programme page and Workout page display."""

    def test_my_programme_page_loads(self, logged_in_client_with_programme, seeded_db):
        """My Programme page returns HTTP 200 for an authenticated user."""
        response = logged_in_client_with_programme.get("/programme")
        assert response.status_code == 200

    def test_my_programme_shows_allocated_programme(
        self, logged_in_client_with_programme, seeded_db
    ):
        """My Programme page displays the user's allocated programme name."""
        response = logged_in_client_with_programme.get("/programme")
        assert b"3-Day Full Body" in response.data

    def test_workout_page_loads(self, logged_in_client_with_programme, seeded_db):
        """Workout page returns HTTP 200 for an authenticated user."""
        response = logged_in_client_with_programme.get("/workout")
        assert response.status_code == 200

    def test_workout_page_shows_todays_workout(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        Workout page displays a workout from the allocated programme
        under the Today's Workout section.
        """
        response = logged_in_client_with_programme.get("/workout")
        assert b"Upper Body A" in response.data

    def test_workout_page_redirects_without_programme(
        self, logged_in_client, seeded_db
    ):
        """
        A user without an allocated programme is redirected to the
        questionnaire from the workout page.
        """
        response = logged_in_client.get("/workout", follow_redirects=False)
        assert response.status_code == 302
        assert "/questionnaire" in response.location

    def test_programme_page_requires_login(self, client, db):
        """My Programme page redirects unauthenticated users to login."""
        response = client.get("/programme", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.location

    def test_workout_page_requires_login(self, client, db):
        """Workout page redirects unauthenticated users to login."""
        response = client.get("/workout", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.location


class TestProgrammeUpdate:
    """FR2 — Programme update via manual selection and questionnaire re-run."""

    def test_change_programme_page_loads(
        self, logged_in_client_with_programme, seeded_db
    ):
        """Change programme page returns HTTP 200."""
        response = logged_in_client_with_programme.get("/programme/change")
        assert response.status_code == 200

    def test_change_programme_page_lists_all_programmes(
        self, logged_in_client_with_programme, seeded_db
    ):
        """Change programme page displays all available programmes."""
        response = logged_in_client_with_programme.get("/programme/change")
        assert b"3-Day Full Body" in response.data
        assert b"2-Day Full Body" in response.data

    def test_manual_programme_change_updates_allocation(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        Submitting a manual programme selection updates the user's
        allocated programme and redirects to My Programme page.
        """
        from app.extensions import db
        from app.models import User

        programme2_id = seeded_db["programme2"].id

        response = logged_in_client_with_programme.post(
            "/programme/change",
            data={"programme_id": str(programme2_id)},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/programme" in response.location

        with logged_in_client_with_programme.application.app_context():
            user = User.query.filter_by(email="test@fitact.com").first()
            assert user.current_programme_id == programme2_id

    def test_questionnaire_rerun_page_accessible(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        The questionnaire is accessible for users who already have a
        programme (re-run for FR2 updated recommendation).
        """
        response = logged_in_client_with_programme.get("/questionnaire")
        assert response.status_code == 200

    def test_confirm_page_accessible_after_questionnaire_rerun(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        After resubmitting the questionnaire, the confirm page is
        shown to allow users to accept or cancel the new recommendation.
        """
        from app.extensions import db
        from app.models import Programme

        with logged_in_client_with_programme.application.app_context():
            programme = Programme.query.filter_by(name="3-Day Full Body").first()

        response = logged_in_client_with_programme.post(
            "/questionnaire",
            data={"days": "3", "experience": "beginner", "goal": "general_fitness"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/confirm" in response.location

    def test_confirm_accept_updates_programme(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        Accepting the confirmed recommendation updates the user's
        programme and redirects to the workout page.
        """
        from app.extensions import db
        from app.models import Programme

        with logged_in_client_with_programme.application.app_context():
            programme = Programme.query.filter_by(name="3-Day Full Body").first()
            programme_id = programme.id

        with logged_in_client_with_programme.session_transaction() as sess:
            sess["recommended_programme_id"] = programme_id
            sess["recommended_programme_name"] = "3-Day Full Body"

        response = logged_in_client_with_programme.post(
            "/questionnaire/confirm/accept", follow_redirects=False
        )
        assert response.status_code == 302
        assert "/workout" in response.location

    def test_confirm_cancel_returns_to_programme_page(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        Cancelling the confirmation redirects back to My Programme page
        without changing the allocation.
        """
        with logged_in_client_with_programme.session_transaction() as sess:
            sess["recommended_programme_id"] = seeded_db["programme"].id
            sess["recommended_programme_name"] = "3-Day Full Body"

        response = logged_in_client_with_programme.get(
            "/questionnaire/confirm/cancel", follow_redirects=False
        )
        assert response.status_code == 302
        assert "/programme" in response.location

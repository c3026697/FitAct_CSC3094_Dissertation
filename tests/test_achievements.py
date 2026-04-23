"""
Tests for FR9 — Milestone-Based Badges and Achievements.

FR9: The system shall include milestone-based badges to encourage
continued user engagement.
"""

import pytest


class TestAchievementsPage:
    """FR9 — Achievements page display."""

    def test_achievements_page_loads(self, logged_in_client_with_programme, seeded_db):
        """Achievements page returns HTTP 200."""
        response = logged_in_client_with_programme.get("/achievements")
        assert response.status_code == 200

    def test_achievements_page_displays_all_badges(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        Achievements page lists all available milestone badges,
        including those not yet earned (FR9).
        """
        response = logged_in_client_with_programme.get("/achievements")
        assert b"First Workout Completed" in response.data

    def test_achievements_page_requires_login(self, client, db):
        """Achievements page redirects unauthenticated users to login."""
        response = client.get("/achievements", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.location


class TestFirstWorkoutBadge:
    """FR9 — First workout milestone badge award logic."""

    def test_first_workout_badge_awarded_after_first_log(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        The 'First Workout Completed' milestone badge is awarded
        automatically when a user logs their first workout (FR9).
        """
        from app.models import User, UserAchievement

        workout_id = seeded_db["workout"].id
        we_id = seeded_db["workout"].workout_exercises[0].id

        logged_in_client_with_programme.post(
            f"/workout/{workout_id}/log",
            data={
                f"ex_{we_id}_set_1_reps": "8",
                f"ex_{we_id}_set_1_weight": "60",
                "duration_seconds": "900",
            },
            follow_redirects=True,
        )

        with logged_in_client_with_programme.application.app_context():
            user = User.query.filter_by(email="test@fitact.com").first()
            awarded = UserAchievement.query.filter_by(user_id=user.id).first()
            assert awarded is not None

    def test_first_workout_badge_not_awarded_twice(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        The first workout badge is only awarded once, even if the
        user logs multiple workouts.
        """
        from app.models import Achievement, User, UserAchievement

        workout_id = seeded_db["workout"].id
        we_id = seeded_db["workout"].workout_exercises[0].id

        for _ in range(2):
            logged_in_client_with_programme.post(
                f"/workout/{workout_id}/log",
                data={
                    f"ex_{we_id}_set_1_reps": "8",
                    f"ex_{we_id}_set_1_weight": "60",
                    "duration_seconds": "900",
                },
                follow_redirects=True,
            )

        with logged_in_client_with_programme.application.app_context():
            user = User.query.filter_by(email="test@fitact.com").first()
            achievement = Achievement.query.filter_by(
                milestone_type="first_workout"
            ).first()
            count = UserAchievement.query.filter_by(
                user_id=user.id, achievement_id=achievement.id
            ).count()
            assert count == 1

    def test_badge_appears_on_achievements_page_after_award(
        self, logged_in_client_with_programme, seeded_db
    ):
        """
        After earning the first workout badge, it appears as earned
        on the achievements page.
        """
        workout_id = seeded_db["workout"].id
        we_id = seeded_db["workout"].workout_exercises[0].id

        logged_in_client_with_programme.post(
            f"/workout/{workout_id}/log",
            data={
                f"ex_{we_id}_set_1_reps": "8",
                f"ex_{we_id}_set_1_weight": "60",
                "duration_seconds": "900",
            },
            follow_redirects=True,
        )

        response = logged_in_client_with_programme.get("/achievements")
        assert b"First Workout Completed" in response.data
        assert response.status_code == 200

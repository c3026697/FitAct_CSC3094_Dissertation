"""
Tests for FR1 — Onboarding Questionnaire and Programme Recommendation.

FR1: The system shall present new users with an onboarding questionnaire
during their first login and use their responses to allocate them to a
suitable workout programme from the predefined programme database.
"""

import pytest

from app.questionnaire.routes import recommend_programme


class TestRecommendationEngine:
    """
    FR1 — Unit tests for the constraint-based recommendation engine.

    Tests the recommend_programme() function directly without HTTP,
    verifying that the correct programme name is returned for every
    valid combination of training days and experience level.
    """

    # ── Beginner cap (max 3 days) ────────────────────────────────────────

    def test_beginner_1_day_returns_2_day_full_body(self):
        """Beginner with 1 day → 2-Day Full Body."""
        assert recommend_programme(1, "beginner") == "2-Day Full Body"

    def test_beginner_2_days_returns_2_day_full_body(self):
        """Beginner with 2 days → 2-Day Full Body."""
        assert recommend_programme(2, "beginner") == "2-Day Full Body"

    def test_beginner_3_days_returns_3_day_full_body(self):
        """Beginner with 3 days → 3-Day Full Body."""
        assert recommend_programme(3, "beginner") == "3-Day Full Body"

    def test_beginner_capped_at_3_days(self):
        """
        Beginner requesting 5 days is capped to 3 days and receives
        the 3-Day Full Body programme.
        """
        assert recommend_programme(5, "beginner") == "3-Day Full Body"

    def test_beginner_capped_at_3_days_for_6_input(self):
        """
        Beginner requesting 6 days is capped to 3 days and receives
        the 3-Day Full Body programme.
        """
        assert recommend_programme(6, "beginner") == "3-Day Full Body"

    # ── Intermediate cap (max 5 days) ───────────────────────────────────

    def test_intermediate_3_days_returns_3_day_full_body(self):
        """Intermediate with 3 days → 3-Day Full Body."""
        assert recommend_programme(3, "intermediate") == "3-Day Full Body"

    def test_intermediate_4_days_returns_upper_lower(self):
        """Intermediate with 4 days → 4-Day Upper/Lower."""
        assert recommend_programme(4, "intermediate") == "4-Day Upper / Lower"

    def test_intermediate_5_days_returns_upper_lower_plus(self):
        """Intermediate with 5 days → 5-Day Upper/Lower + Full Body."""
        assert (
            recommend_programme(5, "intermediate") == "5-Day Upper / Lower + Full Body"
        )

    def test_intermediate_capped_at_5_days(self):
        """
        Intermediate requesting 6 days is capped to 5 days and receives
        the 5-Day Upper/Lower + Full Body programme.
        """
        assert (
            recommend_programme(6, "intermediate") == "5-Day Upper / Lower + Full Body"
        )

    # ── Advanced (no cap) ────────────────────────────────────────────────

    def test_advanced_4_days_returns_upper_lower(self):
        """Advanced with 4 days → 4-Day Upper/Lower (no cap applied)."""
        assert recommend_programme(4, "advanced") == "4-Day Upper / Lower"

    def test_advanced_5_days_returns_upper_lower_plus(self):
        """Advanced with 5 days → 5-Day Upper/Lower + Full Body."""
        assert recommend_programme(5, "advanced") == "5-Day Upper / Lower + Full Body"

    def test_advanced_6_days_returns_ppl(self):
        """Advanced with 6 days → 6-Day Push/Pull/Legs."""
        assert recommend_programme(6, "advanced") == "6-Day Push / Pull / Legs"

    def test_advanced_not_capped(self):
        """
        Advanced users are not capped — 6 days returns PPL not
        an upper/lower split.
        """
        result = recommend_programme(6, "advanced")
        assert result == "6-Day Push / Pull / Legs"

    # ── Edge cases ───────────────────────────────────────────────────────

    def test_2_days_any_experience_returns_2_day_full_body(self):
        """2 training days always maps to 2-Day Full Body."""
        assert recommend_programme(2, "advanced") == "2-Day Full Body"

    def test_3_days_advanced_returns_3_day_full_body(self):
        """Advanced user with 3 days → 3-Day Full Body."""
        assert recommend_programme(3, "advanced") == "3-Day Full Body"


class TestQuestionnaireRoute:
    """FR1 — Questionnaire route and programme allocation via HTTP."""

    def test_questionnaire_page_loads_when_logged_in(self, logged_in_client, seeded_db):
        """Questionnaire page returns HTTP 200 for authenticated users."""
        response = logged_in_client.get("/questionnaire")
        assert response.status_code == 200

    def test_questionnaire_redirects_unauthenticated_user(self, client, db):
        """Unauthenticated users are redirected away from the questionnaire."""
        response = client.get("/questionnaire", follow_redirects=False)
        assert response.status_code == 302

    def test_questionnaire_submission_allocates_programme(
        self, logged_in_client, seeded_db
    ):
        """
        Submitting the questionnaire allocates a programme to the user
        and redirects to the workout page (first login, no confirm screen).
        """
        from app.extensions import db
        from app.models import Programme, User

        with logged_in_client.application.app_context():
            programme = Programme.query.filter_by(name="3-Day Full Body").first()
            if not programme:
                programme = Programme(
                    name="3-Day Full Body",
                    split_type="Full Body",
                    description="Test",
                )
                db.session.add(programme)
                db.session.commit()

        response = logged_in_client.post(
            "/questionnaire",
            data={"days": "3", "experience": "beginner", "goal": "general_fitness"},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/workout" in response.location

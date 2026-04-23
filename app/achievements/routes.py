"""Achievements blueprint for FitAct.

Displays all milestone-based badges and tracks which ones the
current user has earned (FR9).
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Achievement, UserAchievement

achievements_bp = Blueprint("achievements", __name__)


@achievements_bp.route("/achievements")
@login_required
def achievements():
    all_achievements = Achievement.query.all()
    earned_map = {
        ua.achievement_id: ua
        for ua in UserAchievement.query.filter_by(user_id=current_user.id).all()
    }
    return render_template(
        "achievements/achievements.html",
        all_achievements=all_achievements,
        earned_map=earned_map,
    )

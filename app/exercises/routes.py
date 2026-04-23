from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Exercise

exercises_bp = Blueprint("exercises", __name__)


@exercises_bp.route("/exercise/<int:exercise_id>")
@login_required
def guidance(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    return render_template("exercises/guidance.html", exercise=exercise)

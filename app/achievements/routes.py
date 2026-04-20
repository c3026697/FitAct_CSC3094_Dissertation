from flask import Blueprint, render_template
from flask_login import login_required

achievements_bp = Blueprint('achievements', __name__)

@achievements_bp.route('/achievements')
@login_required
def achievements():
    return render_template('achievements/achievements.html')
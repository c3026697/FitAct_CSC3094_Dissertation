from flask import Blueprint, render_template
from flask_login import login_required

exercises_bp = Blueprint('exercises', __name__)

@exercises_bp.route('/exercises')
@login_required
def guidance():
    return render_template('exercises/guidance.html')
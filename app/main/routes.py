from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('workouts.workout_page'))
    return redirect(url_for('auth.login'))


@main_bp.route('/account')
@login_required
def account():
    return render_template('main/account.html')
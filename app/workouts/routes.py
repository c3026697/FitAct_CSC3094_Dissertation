from flask import Blueprint, render_template
from flask_login import login_required

workouts_bp = Blueprint('workouts', __name__)

@workouts_bp.route('/workout')
@login_required
def workout_page():
    return render_template('workouts/workout_page.html')

@workouts_bp.route('/workout/change')
@login_required
def change_workout():
    return render_template('workouts/change_workout.html')

@workouts_bp.route('/workouts')
@login_required
def repository():
    return render_template('workouts/repository.html')

@workouts_bp.route('/workouts/saved')
@login_required
def saved():
    return render_template('workouts/saved.html')

@workouts_bp.route('/workouts/create')
@login_required
def create_custom():
    return render_template('workouts/create_custom.html')
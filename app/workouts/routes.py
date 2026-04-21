from flask import Blueprint, render_template, redirect, url_for, session
from flask_login import login_required, current_user
from app.models import ProgrammeWorkout, Workout, WorkoutExercise

workouts_bp = Blueprint('workouts', __name__)


def get_todays_workout():
    """
    Returns the current workout for the user.
    Uses session to track which day in the programme they are on.
    Defaults to day 1 (first workout in programme).
    """
    if not current_user.current_programme_id:
        return None

    programme_workouts = (
        ProgrammeWorkout.query
        .filter_by(programme_id=current_user.current_programme_id)
        .order_by(ProgrammeWorkout.day_number)
        .all()
    )

    if not programme_workouts:
        return None

    # Use session to remember which day the user is on
    current_day = session.get('current_day', 1)
    total_days = len(programme_workouts)

    # Clamp to valid range
    if current_day < 1:
        current_day = 1
    if current_day > total_days:
        current_day = 1
        session['current_day'] = 1

    pw = next((p for p in programme_workouts if p.day_number == current_day), programme_workouts[0])
    return pw.workout


@workouts_bp.route('/workout')
@login_required
def workout_page():
    if not current_user.current_programme_id:
        return redirect(url_for('questionnaire.questionnaire'))

    workout = get_todays_workout()
    programme = current_user.current_programme

    exercises = []
    if workout:
        exercises = (
            WorkoutExercise.query
            .filter_by(workout_id=workout.id)
            .order_by(WorkoutExercise.exercise_order)
            .all()
        )

    return render_template('workouts/workout_page.html',
                           workout=workout,
                           programme=programme,
                           exercises=exercises)


@workouts_bp.route('/workout/change')
@login_required
def change_workout():
    programme = current_user.current_programme
    programme_workouts = []

    if programme:
        programme_workouts = (
            ProgrammeWorkout.query
            .filter_by(programme_id=programme.id)
            .order_by(ProgrammeWorkout.day_number)
            .all()
        )

    return render_template('workouts/change_workout.html',
                           programme=programme,
                           programme_workouts=programme_workouts)


@workouts_bp.route('/workout/set/<int:workout_id>')
@login_required
def set_workout(workout_id):
    """Sets a specific workout as today's workout via session."""
    pw = ProgrammeWorkout.query.filter_by(
        programme_id=current_user.current_programme_id,
        workout_id=workout_id
    ).first()
    if pw:
        session['current_day'] = pw.day_number
    return redirect(url_for('workouts.workout_page'))


@workouts_bp.route('/workouts')
@login_required
def repository():
    workouts = Workout.query.filter_by(is_custom=False).order_by(Workout.name).all()
    return render_template('workouts/repository.html', workouts=workouts)


@workouts_bp.route('/workouts/saved')
@login_required
def saved():
    return render_template('workouts/saved.html')


@workouts_bp.route('/workouts/create')
@login_required
def create_custom():
    return render_template('workouts/create_custom.html')
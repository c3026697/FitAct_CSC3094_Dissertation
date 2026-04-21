from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import QuestionnaireResponse, Programme, User

questionnaire_bp = Blueprint('questionnaire', __name__)


# ── Recommendation engine ────────────────────────────────────────────────────

def recommend_programme(days, experience):
    """
    Constraint-based recommendation engine.
    Step 1: cap available days based on experience level.
    Step 2: map capped days to a programme name.
    """
    if experience == 'beginner':
        days = min(days, 3)
    elif experience == 'intermediate':
        days = min(days, 5)
    # advanced: no cap

    if days <= 2:
        return '2-Day Full Body'
    elif days == 3:
        return '3-Day Full Body'
    elif days == 4:
        return '4-Day Upper / Lower'
    elif days == 5:
        return '5-Day Upper / Lower + Full Body'
    else:
        return '6-Day Push / Pull / Legs'


# ── Questionnaire (onboarding + re-run) ─────────────────────────────────────

@questionnaire_bp.route('/questionnaire', methods=['GET', 'POST'])
@login_required
def questionnaire():
    # If already has a programme, this is a re-run (FR2)
    is_update = current_user.current_programme_id is not None

    if request.method == 'POST':
        days = int(request.form.get('days'))
        experience = request.form.get('experience')
        goal = request.form.get('goal')

        # Save QuestionnaireResponse to DB
        response = QuestionnaireResponse(
            user_id=current_user.id,
            training_days_per_week=days,
            primary_goal=goal,
            experience_level=experience,
            equipment_access='full_gym'
        )
        db.session.add(response)

        # Run recommendation engine
        programme_name = recommend_programme(days, experience)
        programme = Programme.query.filter_by(name=programme_name).first()

        if programme:
            # Store result in session for confirm screen (FR2)
            session['recommended_programme_id'] = programme.id
            session['recommended_programme_name'] = programme.name
            db.session.commit()

            if is_update:
                return redirect(url_for('questionnaire.confirm'))
            else:
                # Onboarding: assign immediately, no confirm screen needed
                current_user.current_programme_id = programme.id
                db.session.commit()
                flash(f'Welcome! You have been allocated to the {programme.name} programme.', 'success')
                return redirect(url_for('workouts.workout_page'))

    return render_template('questionnaire/questionnaire.html', is_update=is_update)


# ── Confirm new allocation (FR2) ─────────────────────────────────────────────

@questionnaire_bp.route('/questionnaire/confirm')
@login_required
def confirm():
    programme_id = session.get('recommended_programme_id')
    programme_name = session.get('recommended_programme_name')

    if not programme_id:
        return redirect(url_for('questionnaire.questionnaire'))

    return render_template('questionnaire/confirm.html',
                           programme_name=programme_name,
                           programme_id=programme_id)


@questionnaire_bp.route('/questionnaire/confirm/accept', methods=['POST'])
@login_required
def confirm_accept():
    programme_id = session.get('recommended_programme_id')
    programme_name = session.get('recommended_programme_name')

    if programme_id:
        user = User.query.get(current_user.id)  # ← fetch fresh from DB
        user.current_programme_id = programme_id
        db.session.commit()
        session.pop('recommended_programme_id', None)
        session.pop('recommended_programme_name', None)
        flash(f'Your programme has been updated to {programme_name}.', 'success')

    return redirect(url_for('workouts.workout_page'))


@questionnaire_bp.route('/questionnaire/confirm/cancel')
@login_required
def confirm_cancel():
    session.pop('recommended_programme_id', None)
    session.pop('recommended_programme_name', None)
    return redirect(url_for('programme.my_programme'))
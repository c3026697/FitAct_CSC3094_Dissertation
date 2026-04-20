from flask import Blueprint, render_template
from flask_login import login_required

programme_bp = Blueprint('programme', __name__)

@programme_bp.route('/programme')
@login_required
def my_programme():
    return render_template('programme/programme.html')

@programme_bp.route('/programme/change')
@login_required
def change_programme():
    return render_template('programme/change_programme.html')
from flask import Blueprint, render_template
from flask_login import login_required

tracking_bp = Blueprint('tracking', __name__)

@tracking_bp.route('/tracking')
@login_required
def execute():
    return render_template('tracking/execute.html')
"""FitAct application factory.

Creates and configures the Flask application instance, initialises
all extensions, and registers all blueprints.
"""

from flask import Flask, render_template
from app.extensions import db, migrate, login_manager, bcrypt
from config import Config
from flask_login import current_user


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    app.jinja_env.globals["enumerate"] = enumerate

    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.questionnaire.routes import questionnaire_bp
    from app.programme.routes import programme_bp
    from app.workouts.routes import workouts_bp
    from app.exercises.routes import exercises_bp
    from app.tracking.routes import tracking_bp
    from app.progress.routes import progress_bp
    from app.achievements.routes import achievements_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(questionnaire_bp)
    app.register_blueprint(programme_bp)
    app.register_blueprint(workouts_bp)
    app.register_blueprint(exercises_bp)
    app.register_blueprint(tracking_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(achievements_bp)

    # ── Error handlers ────────────────────────────────────────────────────
    @app.errorhandler(400)
    def bad_request(e):
        return render_template("errors/400.html", current_user=current_user), 400

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html", current_user=current_user), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html", current_user=current_user), 500

    @app.errorhandler(501)
    def not_implemented(e):
        return render_template("errors/501.html", current_user=current_user), 501

    return app

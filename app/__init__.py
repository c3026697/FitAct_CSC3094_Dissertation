from flask import Flask
from app.extensions import db, migrate, login_manager, bcrypt
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    app.jinja_env.globals['enumerate'] = enumerate

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

    return app
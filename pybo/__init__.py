from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_simplemde import SimpleMDE
from flaskext.markdown import Markdown

import config

db = SQLAlchemy()
migrate = Migrate() # 여기서 생성해주어야 블루프린트 등 다른 모듈에서 사용가능!


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    app.config['SIMPLEMDE_JS_IIFE'] = True
    app.config['SIMPLEMDE_USE_CDN'] = True
    SimpleMDE(app)

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)

    # Markdown
    Markdown(app, extensions=['nl2br', 'fenced_code'])

    from . import models
    
    # Blueprint
    from .views import main_views, question_views, answer_views, auth_views, comment_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(question_views.bp)
    app.register_blueprint(answer_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(comment_views.bp)

    # 필터
    from .filter import format_datetime
    app.jinja_env.filters['datetime'] = format_datetime

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=True)
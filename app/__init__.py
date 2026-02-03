from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import config

# Khởi tạo các extension
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'
login_manager.login_message_category = 'warning'


def create_app(config_name='default'):
    """App Factory Pattern - Tạo và cấu hình ứng dụng Flask"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Khởi tạo extensions với app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Import và đăng ký Blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    from app.routes.lecturer import lecturer_bp
    from app.routes.student import student_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(lecturer_bp, url_prefix='/lecturer')
    app.register_blueprint(student_bp, url_prefix='/student')
    
    # Tạo thư mục upload nếu chưa tồn tại
    import os
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Context processor để thêm biến global cho templates
    @app.context_processor
    def inject_globals():
        return {
            'app_name': 'SERVECARE',
            'app_short_name': 'SERVECARE'
        }
    
    return app


# Import models để Flask-Migrate nhận diện
from app import models

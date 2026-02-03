import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Cấu hình chung cho ứng dụng"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-ums-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'ums.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload config
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'zip', 'rar'}


class DevelopmentConfig(Config):
    """Cấu hình cho môi trường phát triển"""
    DEBUG = True


class ProductionConfig(Config):
    """Cấu hình cho môi trường sản xuất"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

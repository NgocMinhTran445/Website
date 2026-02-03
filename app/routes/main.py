from flask import Blueprint, redirect, url_for
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Trang chủ - Redirect theo role"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    elif current_user.is_lecturer():
        return redirect(url_for('lecturer.dashboard'))
    else:
        return redirect(url_for('student.dashboard'))

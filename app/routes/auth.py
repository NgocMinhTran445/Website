from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from app.models import User
from app import db

auth_bp = Blueprint('auth', __name__)


# ==================== DECORATORS ====================
def admin_required(f):
    """Decorator kiểm tra quyền Admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Bạn không có quyền truy cập trang này!', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def lecturer_required(f):
    """Decorator kiểm tra quyền Giảng viên"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_lecturer():
            flash('Bạn không có quyền truy cập trang này!', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """Decorator kiểm tra quyền Sinh viên"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_student():
            flash('Bạn không có quyền truy cập trang này!', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== FORMS ====================
class LoginForm(FlaskForm):
    """Form đăng nhập"""
    username = StringField('Tên đăng nhập', validators=[
        DataRequired(message='Vui lòng nhập tên đăng nhập'),
        Length(min=3, max=64, message='Tên đăng nhập từ 3-64 ký tự')
    ])
    password = PasswordField('Mật khẩu', validators=[
        DataRequired(message='Vui lòng nhập mật khẩu')
    ])
    remember_me = BooleanField('Ghi nhớ đăng nhập')
    submit = SubmitField('Đăng nhập')


class ChangePasswordForm(FlaskForm):
    """Form đổi mật khẩu"""
    current_password = PasswordField('Mật khẩu hiện tại', validators=[DataRequired()])
    new_password = PasswordField('Mật khẩu mới', validators=[
        DataRequired(),
        Length(min=6, message='Mật khẩu phải có ít nhất 6 ký tự')
    ])
    confirm_password = PasswordField('Xác nhận mật khẩu mới', validators=[DataRequired()])
    submit = SubmitField('Đổi mật khẩu')


# ==================== ROUTES ====================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Xử lý đăng nhập"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Tài khoản của bạn đã bị khóa. Vui lòng liên hệ quản trị viên.', 'danger')
                return render_template('auth/login.html', form=form)
            
            login_user(user, remember=form.remember_me.data)
            flash(f'Chào mừng {user.get_display_name()} đã đăng nhập!', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            # Redirect theo role
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            elif user.is_lecturer():
                return redirect(url_for('lecturer.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'danger')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Xử lý đăng xuất"""
    logout_user()
    flash('Bạn đã đăng xuất thành công!', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    """Trang hồ sơ cá nhân"""
    return render_template('auth/profile.html')


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Đổi mật khẩu"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Mật khẩu hiện tại không đúng!', 'danger')
            return render_template('auth/change_password.html', form=form)
        
        if form.new_password.data != form.confirm_password.data:
            flash('Mật khẩu xác nhận không khớp!', 'danger')
            return render_template('auth/change_password.html', form=form)
        
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Đổi mật khẩu thành công!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html', form=form)

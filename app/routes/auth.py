from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User, Student, Lecturer
from app import db
from datetime import date

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


class RegisterForm(FlaskForm):
    """Form đăng ký tài khoản"""
    role = SelectField('Vai trò', 
                      choices=[('student', 'Sinh viên'), ('lecturer', 'Giảng viên')],
                      validators=[DataRequired(message='Vui lòng chọn vai trò')])
    
    # Thông tin tài khoản
    username = StringField('Tên đăng nhập', validators=[
        DataRequired(message='Vui lòng nhập tên đăng nhập'),
        Length(min=3, max=64, message='Tên đăng nhập từ 3-64 ký tự')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Vui lòng nhập email'),
        Email(message='Email không hợp lệ')
    ])
    password = PasswordField('Mật khẩu', validators=[
        DataRequired(message='Vui lòng nhập mật khẩu'),
        Length(min=6, message='Mật khẩu phải có ít nhất 6 ký tự')
    ])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[
        DataRequired(message='Vui lòng xác nhận mật khẩu'),
        EqualTo('password', message='Mật khẩu xác nhận không khớp')
    ])
    
    # Thông tin cá nhân
    full_name = StringField('Họ và tên', validators=[
        DataRequired(message='Vui lòng nhập họ và tên'),
        Length(min=3, max=100, message='Họ tên từ 3-100 ký tự')
    ])
    
    # Thông tin cho sinh viên
    student_code = StringField('Mã sinh viên', validators=[
        Length(max=20, message='Mã sinh viên tối đa 20 ký tự')
    ])
    dob = DateField('Ngày sinh', format='%Y-%m-%d', validators=[])
    gender = SelectField('Giới tính', 
                        choices=[('', 'Chọn giới tính'), ('Nam', 'Nam'), ('Nữ', 'Nữ')],
                        validators=[])
    
    # Thông tin cho giảng viên
    lecturer_code = StringField('Mã giảng viên', validators=[
        Length(max=20, message='Mã giảng viên tối đa 20 ký tự')
    ])
    department = StringField('Khoa/Bộ môn', validators=[
        Length(max=100, message='Khoa/Bộ môn tối đa 100 ký tự')
    ])
    degree = SelectField('Học vị',
                        choices=[('', 'Chọn học vị'), ('Cử nhân', 'Cử nhân'), ('ThS', 'Thạc sĩ'), 
                                ('TS', 'Tiến sĩ'), ('PGS', 'Phó Giáo sư'), ('GS', 'Giáo sư')],
                        validators=[])
    
    phone = StringField('Số điện thoại', validators=[
        Length(max=15, message='Số điện thoại tối đa 15 ký tự')
    ])
    
    submit = SubmitField('Đăng ký')
    
    def validate_username(self, field):
        """Kiểm tra username đã tồn tại chưa"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Tên đăng nhập đã được sử dụng')
    
    def validate_email(self, field):
        """Kiểm tra email đã tồn tại chưa"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email đã được sử dụng')
    
    def validate_student_code(self, field):
        """Kiểm tra mã sinh viên đã tồn tại chưa"""
        if field.data and Student.query.filter_by(student_code=field.data).first():
            raise ValidationError('Mã sinh viên đã được sử dụng')
    
    def validate_lecturer_code(self, field):
        """Kiểm tra mã giảng viên đã tồn tại chưa"""
        if field.data and Lecturer.query.filter_by(lecturer_code=field.data).first():
            raise ValidationError('Mã giảng viên đã được sử dụng')


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


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Xử lý đăng ký tài khoản"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        try:
            # Tạo user
            user = User(
                username=form.username.data,
                email=form.email.data,
                role=form.role.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.flush()  # Để lấy user.id
            
            # Tạo thông tin chi tiết theo role
            if form.role.data == 'student':
                if not form.student_code.data:
                    flash('Vui lòng nhập mã sinh viên!', 'danger')
                    return render_template('auth/register.html', form=form)
                
                student = Student(
                    user_id=user.id,
                    student_code=form.student_code.data,
                    full_name=form.full_name.data,
                    dob=form.dob.data if form.dob.data else None,
                    gender=form.gender.data if form.gender.data else None,
                    phone=form.phone.data if form.phone.data else None,
                    enrollment_year=date.today().year
                )
                db.session.add(student)
                
            elif form.role.data == 'lecturer':
                if not form.lecturer_code.data:
                    flash('Vui lòng nhập mã giảng viên!', 'danger')
                    return render_template('auth/register.html', form=form)
                
                lecturer = Lecturer(
                    user_id=user.id,
                    lecturer_code=form.lecturer_code.data,
                    full_name=form.full_name.data,
                    department=form.department.data if form.department.data else None,
                    degree=form.degree.data if form.degree.data else None,
                    phone=form.phone.data if form.phone.data else None
                )
                db.session.add(lecturer)
            
            db.session.commit()
            flash(f'Đăng ký tài khoản thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
    
    return render_template('auth/register.html', form=form)

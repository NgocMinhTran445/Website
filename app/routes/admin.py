from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, IntegerField, DateField, TimeField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange
from app.routes.auth import admin_required
from app.models import User, Student, Lecturer, Major, Classroom, Subject, Schedule, Grade, Material
from app import db
import json

admin_bp = Blueprint('admin', __name__)


# ==================== FORMS ====================
class StudentForm(FlaskForm):
    """Form thêm/sửa Sinh viên"""
    student_code = StringField('Mã sinh viên', validators=[DataRequired(), Length(max=20)])
    full_name = StringField('Họ và tên', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Mật khẩu', validators=[Optional(), Length(min=6)])
    dob = DateField('Ngày sinh', validators=[Optional()])
    gender = SelectField('Giới tính', choices=[('Nam', 'Nam'), ('Nữ', 'Nữ')])
    phone = StringField('Số điện thoại', validators=[Optional(), Length(max=15)])
    address = StringField('Địa chỉ', validators=[Optional(), Length(max=200)])
    major_id = SelectField('Ngành học', coerce=int, validators=[Optional()])
    class_id = SelectField('Lớp', coerce=int, validators=[Optional()])
    enrollment_year = IntegerField('Năm nhập học', validators=[Optional()])


class LecturerForm(FlaskForm):
    """Form thêm/sửa Giảng viên"""
    lecturer_code = StringField('Mã giảng viên', validators=[DataRequired(), Length(max=20)])
    full_name = StringField('Họ và tên', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Mật khẩu', validators=[Optional(), Length(min=6)])
    department = StringField('Khoa/Bộ môn', validators=[Optional(), Length(max=100)])
    expertise = StringField('Chuyên môn', validators=[Optional(), Length(max=200)])
    degree = SelectField('Học vị', choices=[
        ('CN', 'Cử nhân'), ('ThS', 'Thạc sĩ'), ('TS', 'Tiến sĩ'), 
        ('PGS', 'Phó Giáo sư'), ('GS', 'Giáo sư')
    ])
    phone = StringField('Số điện thoại', validators=[Optional(), Length(max=15)])


class MajorForm(FlaskForm):
    """Form thêm/sửa Ngành học"""
    code = StringField('Mã ngành', validators=[DataRequired(), Length(max=20)])
    name = StringField('Tên ngành', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Mô tả', validators=[Optional()])


class ClassroomForm(FlaskForm):
    """Form thêm/sửa Lớp"""
    name = StringField('Tên lớp', validators=[DataRequired(), Length(max=50)])
    major_id = SelectField('Ngành học', coerce=int, validators=[Optional()])
    advisor_id = SelectField('Cố vấn học tập', coerce=int, validators=[Optional()])
    academic_year = StringField('Niên khóa', validators=[Optional(), Length(max=20)])


class SubjectForm(FlaskForm):
    """Form thêm/sửa Môn học"""
    code = StringField('Mã môn học', validators=[DataRequired(), Length(max=20)])
    name = StringField('Tên môn học', validators=[DataRequired(), Length(max=100)])
    credits = IntegerField('Số tín chỉ', validators=[DataRequired(), NumberRange(min=1, max=10)])
    theory_hours = IntegerField('Số giờ lý thuyết', validators=[Optional()])
    practice_hours = IntegerField('Số giờ thực hành', validators=[Optional()])
    description = TextAreaField('Mô tả', validators=[Optional()])


class ScheduleForm(FlaskForm):
    """Form thêm/sửa Lịch học"""
    subject_id = SelectField('Môn học', coerce=int, validators=[DataRequired()])
    lecturer_id = SelectField('Giảng viên', coerce=int, validators=[DataRequired()])
    class_id = SelectField('Lớp', coerce=int, validators=[DataRequired()])
    room_name = StringField('Phòng học', validators=[DataRequired(), Length(max=50)])
    day_of_week = SelectField('Thứ', coerce=int, choices=[
        (0, 'Thứ 2'), (1, 'Thứ 3'), (2, 'Thứ 4'), 
        (3, 'Thứ 5'), (4, 'Thứ 6'), (5, 'Thứ 7'), (6, 'Chủ nhật')
    ])
    start_time = TimeField('Giờ bắt đầu', validators=[DataRequired()])
    end_time = TimeField('Giờ kết thúc', validators=[DataRequired()])
    semester = StringField('Học kỳ', validators=[DataRequired(), Length(max=20)])


# ==================== ROUTES ====================
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Dashboard Admin - Hiển thị thống kê tổng quan"""
    # Thống kê cơ bản
    stats = {
        'total_students': Student.query.count(),
        'total_lecturers': Lecturer.query.count(),
        'total_subjects': Subject.query.count(),
        'total_classrooms': Classroom.query.count(),
        'total_majors': Major.query.count(),
        'total_materials': Material.query.count()
    }
    
    # Sinh viên mới nhất
    recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()
    
    # Phân bố sinh viên theo ngành
    majors = Major.query.all()
    major_names = [m.name for m in majors] if majors else ['Chưa có ngành']
    major_counts = [m.students.count() for m in majors] if majors else [0]
    
    # Phân bố điểm số
    grades = Grade.query.filter(Grade.score_total.isnot(None)).all()
    grade_distribution = [0, 0, 0, 0, 0]  # A, B, C, D, F
    for grade in grades:
        if grade.score_total >= 8.5:
            grade_distribution[0] += 1
        elif grade.score_total >= 7.0:
            grade_distribution[1] += 1
        elif grade.score_total >= 5.5:
            grade_distribution[2] += 1
        elif grade.score_total >= 4.0:
            grade_distribution[3] += 1
        else:
            grade_distribution[4] += 1
    
    if sum(grade_distribution) == 0:
        grade_distribution = [20, 35, 25, 15, 5]  # Demo data
    
    return render_template('admin/dashboard.html',
                           stats=stats,
                           recent_students=recent_students,
                           major_names=json.dumps(major_names),
                           major_counts=json.dumps(major_counts),
                           grade_distribution=json.dumps(grade_distribution))


# ==================== STUDENT MANAGEMENT ====================
@admin_bp.route('/students')
@login_required
@admin_required
def students():
    """Danh sách sinh viên"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Student.query
    if search:
        query = query.filter(
            (Student.full_name.ilike(f'%{search}%')) | 
            (Student.student_code.ilike(f'%{search}%'))
        )
    
    students = query.order_by(Student.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('admin/students/list.html', students=students, search=search)


@admin_bp.route('/students/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_student():
    """Thêm sinh viên mới"""
    form = StudentForm()
    form.major_id.choices = [(0, 'Chọn ngành học')] + [(m.id, m.name) for m in Major.query.all()]
    form.class_id.choices = [(0, 'Chọn lớp')] + [(c.id, c.name) for c in Classroom.query.all()]
    
    if form.validate_on_submit():
        # Kiểm tra username và email đã tồn tại
        if User.query.filter_by(username=form.username.data).first():
            flash('Tên đăng nhập đã tồn tại!', 'danger')
            return render_template('admin/students/form.html', form=form, title='Thêm Sinh viên')
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email đã được sử dụng!', 'danger')
            return render_template('admin/students/form.html', form=form, title='Thêm Sinh viên')
        
        # Tạo User
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='student'
        )
        user.set_password(form.password.data or '123456')
        db.session.add(user)
        db.session.flush()
        
        # Tạo Student
        student = Student(
            user_id=user.id,
            student_code=form.student_code.data,
            full_name=form.full_name.data,
            dob=form.dob.data,
            gender=form.gender.data,
            phone=form.phone.data,
            address=form.address.data,
            major_id=form.major_id.data if form.major_id.data != 0 else None,
            class_id=form.class_id.data if form.class_id.data != 0 else None,
            enrollment_year=form.enrollment_year.data
        )
        db.session.add(student)
        db.session.commit()
        
        flash(f'Đã thêm sinh viên {student.full_name} thành công!', 'success')
        return redirect(url_for('admin.students'))
    
    return render_template('admin/students/form.html', form=form, title='Thêm Sinh viên')


@admin_bp.route('/students/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student(id):
    """Sửa thông tin sinh viên"""
    student = Student.query.get_or_404(id)
    form = StudentForm(obj=student)
    form.major_id.choices = [(0, 'Chọn ngành học')] + [(m.id, m.name) for m in Major.query.all()]
    form.class_id.choices = [(0, 'Chọn lớp')] + [(c.id, c.name) for c in Classroom.query.all()]
    
    if request.method == 'GET':
        form.username.data = student.user.username
        form.email.data = student.user.email
    
    if form.validate_on_submit():
        student.student_code = form.student_code.data
        student.full_name = form.full_name.data
        student.dob = form.dob.data
        student.gender = form.gender.data
        student.phone = form.phone.data
        student.address = form.address.data
        student.major_id = form.major_id.data if form.major_id.data != 0 else None
        student.class_id = form.class_id.data if form.class_id.data != 0 else None
        student.enrollment_year = form.enrollment_year.data
        
        student.user.email = form.email.data
        if form.password.data:
            student.user.set_password(form.password.data)
        
        db.session.commit()
        flash('Cập nhật thông tin sinh viên thành công!', 'success')
        return redirect(url_for('admin.students'))
    
    return render_template('admin/students/form.html', form=form, title='Sửa Sinh viên', student=student)


@admin_bp.route('/students/delete/<int:id>')
@login_required
@admin_required
def delete_student(id):
    """Xóa sinh viên"""
    student = Student.query.get_or_404(id)
    user = student.user
    
    db.session.delete(student)
    if user:
        db.session.delete(user)
    db.session.commit()
    
    flash('Đã xóa sinh viên thành công!', 'success')
    return redirect(url_for('admin.students'))


# ==================== LECTURER MANAGEMENT ====================
@admin_bp.route('/lecturers')
@login_required
@admin_required
def lecturers():
    """Danh sách giảng viên"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Lecturer.query
    if search:
        query = query.filter(
            (Lecturer.full_name.ilike(f'%{search}%')) | 
            (Lecturer.lecturer_code.ilike(f'%{search}%'))
        )
    
    lecturers = query.order_by(Lecturer.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('admin/lecturers/list.html', lecturers=lecturers, search=search)


@admin_bp.route('/lecturers/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_lecturer():
    """Thêm giảng viên mới"""
    form = LecturerForm()
    
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Tên đăng nhập đã tồn tại!', 'danger')
            return render_template('admin/lecturers/form.html', form=form, title='Thêm Giảng viên')
        
        # Tạo User
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='lecturer'
        )
        user.set_password(form.password.data or '123456')
        db.session.add(user)
        db.session.flush()
        
        # Tạo Lecturer
        lecturer = Lecturer(
            user_id=user.id,
            lecturer_code=form.lecturer_code.data,
            full_name=form.full_name.data,
            department=form.department.data,
            expertise=form.expertise.data,
            degree=form.degree.data,
            phone=form.phone.data
        )
        db.session.add(lecturer)
        db.session.commit()
        
        flash(f'Đã thêm giảng viên {lecturer.full_name} thành công!', 'success')
        return redirect(url_for('admin.lecturers'))
    
    return render_template('admin/lecturers/form.html', form=form, title='Thêm Giảng viên')


@admin_bp.route('/lecturers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_lecturer(id):
    """Sửa thông tin giảng viên"""
    lecturer = Lecturer.query.get_or_404(id)
    form = LecturerForm(obj=lecturer)
    
    if request.method == 'GET':
        form.username.data = lecturer.user.username
        form.email.data = lecturer.user.email
    
    if form.validate_on_submit():
        lecturer.lecturer_code = form.lecturer_code.data
        lecturer.full_name = form.full_name.data
        lecturer.department = form.department.data
        lecturer.expertise = form.expertise.data
        lecturer.degree = form.degree.data
        lecturer.phone = form.phone.data
        
        lecturer.user.email = form.email.data
        if form.password.data:
            lecturer.user.set_password(form.password.data)
        
        db.session.commit()
        flash('Cập nhật thông tin giảng viên thành công!', 'success')
        return redirect(url_for('admin.lecturers'))
    
    return render_template('admin/lecturers/form.html', form=form, title='Sửa Giảng viên', lecturer=lecturer)


@admin_bp.route('/lecturers/delete/<int:id>')
@login_required
@admin_required
def delete_lecturer(id):
    """Xóa giảng viên"""
    lecturer = Lecturer.query.get_or_404(id)
    user = lecturer.user
    
    db.session.delete(lecturer)
    if user:
        db.session.delete(user)
    db.session.commit()
    
    flash('Đã xóa giảng viên thành công!', 'success')
    return redirect(url_for('admin.lecturers'))


# ==================== MAJOR MANAGEMENT ====================
@admin_bp.route('/majors')
@login_required
@admin_required
def majors():
    """Danh sách ngành học"""
    majors = Major.query.order_by(Major.name).all()
    return render_template('admin/majors/list.html', majors=majors)


@admin_bp.route('/majors/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_major():
    """Thêm ngành học"""
    form = MajorForm()
    
    if form.validate_on_submit():
        major = Major(
            code=form.code.data,
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(major)
        db.session.commit()
        flash(f'Đã thêm ngành {major.name} thành công!', 'success')
        return redirect(url_for('admin.majors'))
    
    return render_template('admin/majors/form.html', form=form, title='Thêm Ngành học')


@admin_bp.route('/majors/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_major(id):
    """Sửa ngành học"""
    major = Major.query.get_or_404(id)
    form = MajorForm(obj=major)
    
    if form.validate_on_submit():
        major.code = form.code.data
        major.name = form.name.data
        major.description = form.description.data
        db.session.commit()
        flash('Cập nhật ngành học thành công!', 'success')
        return redirect(url_for('admin.majors'))
    
    return render_template('admin/majors/form.html', form=form, title='Sửa Ngành học', major=major)


@admin_bp.route('/majors/delete/<int:id>')
@login_required
@admin_required
def delete_major(id):
    """Xóa ngành học"""
    major = Major.query.get_or_404(id)
    db.session.delete(major)
    db.session.commit()
    flash('Đã xóa ngành học thành công!', 'success')
    return redirect(url_for('admin.majors'))


# ==================== CLASSROOM MANAGEMENT ====================
@admin_bp.route('/classrooms')
@login_required
@admin_required
def classrooms():
    """Danh sách lớp học"""
    classrooms = Classroom.query.order_by(Classroom.name).all()
    return render_template('admin/classrooms/list.html', classrooms=classrooms)


@admin_bp.route('/classrooms/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_classroom():
    """Thêm lớp học"""
    form = ClassroomForm()
    form.major_id.choices = [(0, 'Chọn ngành')] + [(m.id, m.name) for m in Major.query.all()]
    form.advisor_id.choices = [(0, 'Chọn cố vấn')] + [(l.id, l.full_name) for l in Lecturer.query.all()]
    
    if form.validate_on_submit():
        classroom = Classroom(
            name=form.name.data,
            major_id=form.major_id.data if form.major_id.data != 0 else None,
            advisor_id=form.advisor_id.data if form.advisor_id.data != 0 else None,
            academic_year=form.academic_year.data
        )
        db.session.add(classroom)
        db.session.commit()
        flash(f'Đã thêm lớp {classroom.name} thành công!', 'success')
        return redirect(url_for('admin.classrooms'))
    
    return render_template('admin/classrooms/form.html', form=form, title='Thêm Lớp học')


@admin_bp.route('/classrooms/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_classroom(id):
    """Sửa lớp học"""
    classroom = Classroom.query.get_or_404(id)
    form = ClassroomForm(obj=classroom)
    form.major_id.choices = [(0, 'Chọn ngành')] + [(m.id, m.name) for m in Major.query.all()]
    form.advisor_id.choices = [(0, 'Chọn cố vấn')] + [(l.id, l.full_name) for l in Lecturer.query.all()]
    
    if form.validate_on_submit():
        classroom.name = form.name.data
        classroom.major_id = form.major_id.data if form.major_id.data != 0 else None
        classroom.advisor_id = form.advisor_id.data if form.advisor_id.data != 0 else None
        classroom.academic_year = form.academic_year.data
        db.session.commit()
        flash('Cập nhật lớp học thành công!', 'success')
        return redirect(url_for('admin.classrooms'))
    
    return render_template('admin/classrooms/form.html', form=form, title='Sửa Lớp học', classroom=classroom)


@admin_bp.route('/classrooms/delete/<int:id>')
@login_required
@admin_required
def delete_classroom(id):
    """Xóa lớp học"""
    classroom = Classroom.query.get_or_404(id)
    db.session.delete(classroom)
    db.session.commit()
    flash('Đã xóa lớp học thành công!', 'success')
    return redirect(url_for('admin.classrooms'))


# ==================== SUBJECT MANAGEMENT ====================
@admin_bp.route('/subjects')
@login_required
@admin_required
def subjects():
    """Danh sách môn học"""
    subjects = Subject.query.order_by(Subject.name).all()
    return render_template('admin/subjects/list.html', subjects=subjects)


@admin_bp.route('/subjects/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_subject():
    """Thêm môn học"""
    form = SubjectForm()
    
    if form.validate_on_submit():
        subject = Subject(
            code=form.code.data,
            name=form.name.data,
            credits=form.credits.data,
            theory_hours=form.theory_hours.data or 30,
            practice_hours=form.practice_hours.data or 15,
            description=form.description.data
        )
        db.session.add(subject)
        db.session.commit()
        flash(f'Đã thêm môn học {subject.name} thành công!', 'success')
        return redirect(url_for('admin.subjects'))
    
    return render_template('admin/subjects/form.html', form=form, title='Thêm Môn học')


@admin_bp.route('/subjects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_subject(id):
    """Sửa môn học"""
    subject = Subject.query.get_or_404(id)
    form = SubjectForm(obj=subject)
    
    if form.validate_on_submit():
        subject.code = form.code.data
        subject.name = form.name.data
        subject.credits = form.credits.data
        subject.theory_hours = form.theory_hours.data
        subject.practice_hours = form.practice_hours.data
        subject.description = form.description.data
        db.session.commit()
        flash('Cập nhật môn học thành công!', 'success')
        return redirect(url_for('admin.subjects'))
    
    return render_template('admin/subjects/form.html', form=form, title='Sửa Môn học', subject=subject)


@admin_bp.route('/subjects/delete/<int:id>')
@login_required
@admin_required
def delete_subject(id):
    """Xóa môn học"""
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    flash('Đã xóa môn học thành công!', 'success')
    return redirect(url_for('admin.subjects'))


# ==================== SCHEDULE MANAGEMENT ====================
@admin_bp.route('/schedules')
@login_required
@admin_required
def schedules():
    """Danh sách lịch học"""
    schedules = Schedule.query.order_by(Schedule.day_of_week, Schedule.start_time).all()
    return render_template('admin/schedules/list.html', schedules=schedules)


@admin_bp.route('/schedules/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_schedule():
    """Thêm lịch học"""
    form = ScheduleForm()
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]
    form.lecturer_id.choices = [(l.id, l.full_name) for l in Lecturer.query.all()]
    form.class_id.choices = [(c.id, c.name) for c in Classroom.query.all()]
    
    if form.validate_on_submit():
        schedule = Schedule(
            subject_id=form.subject_id.data,
            lecturer_id=form.lecturer_id.data,
            class_id=form.class_id.data,
            room_name=form.room_name.data,
            day_of_week=form.day_of_week.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            semester=form.semester.data
        )
        db.session.add(schedule)
        db.session.commit()
        flash('Đã thêm lịch học thành công!', 'success')
        return redirect(url_for('admin.schedules'))
    
    return render_template('admin/schedules/form.html', form=form, title='Thêm Lịch học')


@admin_bp.route('/schedules/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_schedule(id):
    """Sửa lịch học"""
    schedule = Schedule.query.get_or_404(id)
    form = ScheduleForm(obj=schedule)
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]
    form.lecturer_id.choices = [(l.id, l.full_name) for l in Lecturer.query.all()]
    form.class_id.choices = [(c.id, c.name) for c in Classroom.query.all()]
    
    if form.validate_on_submit():
        schedule.subject_id = form.subject_id.data
        schedule.lecturer_id = form.lecturer_id.data
        schedule.class_id = form.class_id.data
        schedule.room_name = form.room_name.data
        schedule.day_of_week = form.day_of_week.data
        schedule.start_time = form.start_time.data
        schedule.end_time = form.end_time.data
        schedule.semester = form.semester.data
        db.session.commit()
        flash('Cập nhật lịch học thành công!', 'success')
        return redirect(url_for('admin.schedules'))
    
    return render_template('admin/schedules/form.html', form=form, title='Sửa Lịch học', schedule=schedule)


@admin_bp.route('/schedules/delete/<int:id>')
@login_required
@admin_required
def delete_schedule(id):
    """Xóa lịch học"""
    schedule = Schedule.query.get_or_404(id)
    db.session.delete(schedule)
    db.session.commit()
    flash('Đã xóa lịch học thành công!', 'success')
    return redirect(url_for('admin.schedules'))

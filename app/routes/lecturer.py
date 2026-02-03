from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FloatField, SelectField
from wtforms.validators import DataRequired, Optional, NumberRange
from app.routes.auth import lecturer_required
from app.models import Lecturer, Student, Schedule, Grade, Subject, Material, Classroom
from app import db
import os
from werkzeug.utils import secure_filename

lecturer_bp = Blueprint('lecturer', __name__)


# ==================== FORMS ====================
class GradeForm(FlaskForm):
    """Form nhập điểm"""
    score_attendance = FloatField('Điểm chuyên cần', validators=[Optional(), NumberRange(0, 10)])
    score_midterm = FloatField('Điểm giữa kỳ', validators=[Optional(), NumberRange(0, 10)])
    score_final = FloatField('Điểm cuối kỳ', validators=[Optional(), NumberRange(0, 10)])
    note = StringField('Ghi chú', validators=[Optional()])


class MaterialForm(FlaskForm):
    """Form upload tài liệu"""
    subject_id = SelectField('Môn học', coerce=int, validators=[DataRequired()])
    title = StringField('Tiêu đề', validators=[DataRequired()])
    description = TextAreaField('Mô tả', validators=[Optional()])
    file = FileField('Tệp tin', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'zip', 'rar'], 
                    'Chỉ cho phép file PDF, Word, Excel, PowerPoint, ZIP!')
    ])


# ==================== ROUTES ====================
@lecturer_bp.route('/dashboard')
@login_required
@lecturer_required
def dashboard():
    """Dashboard Giảng viên"""
    lecturer = current_user.lecturer
    
    # Thống kê
    total_schedules = lecturer.schedules.count() if lecturer else 0
    total_materials = lecturer.materials.count() if lecturer else 0
    avg_rating = lecturer.get_average_rating() if lecturer else 0
    
    # Lịch dạy hôm nay
    from datetime import datetime
    today = datetime.now().weekday()  # 0 = Monday
    today_schedules = Schedule.query.filter_by(
        lecturer_id=lecturer.id, 
        day_of_week=today
    ).order_by(Schedule.start_time).all() if lecturer else []
    
    # Đánh giá gần đây
    recent_evaluations = lecturer.evaluations.order_by(
        db.text('created_at DESC')
    ).limit(5).all() if lecturer else []
    
    return render_template('lecturer/dashboard.html',
                           lecturer=lecturer,
                           total_schedules=total_schedules,
                           total_materials=total_materials,
                           avg_rating=avg_rating,
                           today_schedules=today_schedules,
                           recent_evaluations=recent_evaluations)


@lecturer_bp.route('/schedule')
@login_required
@lecturer_required
def schedule():
    """Xem lịch giảng dạy"""
    lecturer = current_user.lecturer
    schedules = Schedule.query.filter_by(lecturer_id=lecturer.id).order_by(
        Schedule.day_of_week, Schedule.start_time
    ).all() if lecturer else []
    
    # Nhóm theo ngày
    schedule_by_day = {}
    for s in schedules:
        day = s.day_of_week
        if day not in schedule_by_day:
            schedule_by_day[day] = []
        schedule_by_day[day].append(s)
    
    return render_template('lecturer/schedule.html', 
                           schedules=schedules, 
                           schedule_by_day=schedule_by_day)


@lecturer_bp.route('/grades')
@login_required
@lecturer_required
def grades():
    """Danh sách lớp để nhập điểm"""
    lecturer = current_user.lecturer
    schedules = Schedule.query.filter_by(lecturer_id=lecturer.id).all() if lecturer else []
    
    # Lấy danh sách các lớp/môn duy nhất
    class_subjects = []
    seen = set()
    for s in schedules:
        key = (s.class_id, s.subject_id)
        if key not in seen:
            seen.add(key)
            class_subjects.append({
                'classroom': s.classroom,
                'subject': s.subject,
                'semester': s.semester
            })
    
    return render_template('lecturer/grades/list.html', class_subjects=class_subjects)


@lecturer_bp.route('/grades/<int:class_id>/<int:subject_id>')
@login_required
@lecturer_required
def grade_class(class_id, subject_id):
    """Xem và nhập điểm cho một lớp/môn"""
    classroom = Classroom.query.get_or_404(class_id)
    subject = Subject.query.get_or_404(subject_id)
    semester = request.args.get('semester', 'HK2-2024')
    
    # Lấy danh sách sinh viên trong lớp
    students = Student.query.filter_by(class_id=class_id).all()
    
    # Lấy điểm hiện có
    grades_dict = {}
    for student in students:
        grade = Grade.query.filter_by(
            student_id=student.id,
            subject_id=subject_id,
            semester=semester
        ).first()
        grades_dict[student.id] = grade
    
    return render_template('lecturer/grades/input.html',
                           classroom=classroom,
                           subject=subject,
                           students=students,
                           grades_dict=grades_dict,
                           semester=semester)


@lecturer_bp.route('/grades/save', methods=['POST'])
@login_required
@lecturer_required
def save_grades():
    """Lưu điểm"""
    class_id = request.form.get('class_id', type=int)
    subject_id = request.form.get('subject_id', type=int)
    semester = request.form.get('semester', 'HK2-2024')
    
    students = Student.query.filter_by(class_id=class_id).all()
    
    for student in students:
        attendance = request.form.get(f'attendance_{student.id}', type=float) or 0
        midterm = request.form.get(f'midterm_{student.id}', type=float) or 0
        final = request.form.get(f'final_{student.id}', type=float) or 0
        
        # Tìm hoặc tạo mới grade
        grade = Grade.query.filter_by(
            student_id=student.id,
            subject_id=subject_id,
            semester=semester
        ).first()
        
        if not grade:
            grade = Grade(
                student_id=student.id,
                subject_id=subject_id,
                semester=semester
            )
            db.session.add(grade)
        
        grade.score_attendance = attendance
        grade.score_midterm = midterm
        grade.score_final = final
        grade.calculate_total()
    
    db.session.commit()
    flash('Đã lưu điểm thành công!', 'success')
    return redirect(url_for('lecturer.grade_class', class_id=class_id, subject_id=subject_id))


@lecturer_bp.route('/materials')
@login_required
@lecturer_required
def materials():
    """Danh sách tài liệu đã upload"""
    lecturer = current_user.lecturer
    materials = Material.query.filter_by(uploaded_by=lecturer.id).order_by(
        Material.created_at.desc()
    ).all() if lecturer else []
    
    return render_template('lecturer/materials/list.html', materials=materials)


@lecturer_bp.route('/materials/add', methods=['GET', 'POST'])
@login_required
@lecturer_required
def add_material():
    """Upload tài liệu mới"""
    lecturer = current_user.lecturer
    form = MaterialForm()
    
    # Lấy danh sách môn học giảng viên này dạy
    schedules = Schedule.query.filter_by(lecturer_id=lecturer.id).all() if lecturer else []
    subjects = list(set([s.subject for s in schedules]))
    form.subject_id.choices = [(s.id, s.name) for s in subjects]
    
    if form.validate_on_submit():
        file = form.file.data
        if file:
            filename = secure_filename(file.filename)
            from flask import current_app
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'materials', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)
            file_size = os.path.getsize(file_path)
            file_type = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        else:
            file_path = None
            file_size = 0
            file_type = ''
        
        material = Material(
            subject_id=form.subject_id.data,
            uploaded_by=lecturer.id,
            title=form.title.data,
            description=form.description.data,
            file_path=f'materials/{filename}' if file else None,
            file_type=file_type,
            file_size=file_size
        )
        db.session.add(material)
        db.session.commit()
        
        flash('Đã upload tài liệu thành công!', 'success')
        return redirect(url_for('lecturer.materials'))
    
    return render_template('lecturer/materials/form.html', form=form, title='Thêm Tài liệu')


@lecturer_bp.route('/materials/delete/<int:id>')
@login_required
@lecturer_required
def delete_material(id):
    """Xóa tài liệu"""
    material = Material.query.get_or_404(id)
    lecturer = current_user.lecturer
    
    if material.uploaded_by != lecturer.id:
        flash('Bạn không có quyền xóa tài liệu này!', 'danger')
        return redirect(url_for('lecturer.materials'))
    
    db.session.delete(material)
    db.session.commit()
    flash('Đã xóa tài liệu!', 'success')
    return redirect(url_for('lecturer.materials'))


@lecturer_bp.route('/students')
@login_required
@lecturer_required
def students():
    """Xem danh sách sinh viên trong các lớp đang dạy"""
    lecturer = current_user.lecturer
    schedules = Schedule.query.filter_by(lecturer_id=lecturer.id).all() if lecturer else []
    
    # Lấy các lớp duy nhất
    classrooms = list(set([s.classroom for s in schedules]))
    
    selected_class = request.args.get('class_id', type=int)
    students = []
    if selected_class:
        students = Student.query.filter_by(class_id=selected_class).all()
    
    return render_template('lecturer/students.html', 
                           classrooms=classrooms, 
                           students=students,
                           selected_class=selected_class)

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, TextAreaField, SelectField, RadioField
from wtforms.validators import DataRequired, NumberRange, Optional
from app.routes.auth import student_required
from app.models import Student, Schedule, Grade, Subject, Material, Lecturer, Evaluation
from app import db
from flask import current_app
import os

student_bp = Blueprint('student', __name__)


# ==================== FORMS ====================
class EvaluationForm(FlaskForm):
    """Form đánh giá giảng viên"""
    lecturer_id = SelectField('Giảng viên', coerce=int, validators=[DataRequired()])
    subject_id = SelectField('Môn học', coerce=int, validators=[DataRequired()])
    rating = RadioField('Đánh giá', choices=[
        ('5', '⭐⭐⭐⭐⭐ Xuất sắc'),
        ('4', '⭐⭐⭐⭐ Tốt'),
        ('3', '⭐⭐⭐ Khá'),
        ('2', '⭐⭐ Trung bình'),
        ('1', '⭐ Cần cải thiện')
    ], validators=[DataRequired()])
    comment = TextAreaField('Nhận xét', validators=[Optional()])


# ==================== ROUTES ====================
@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    """Dashboard Sinh viên"""
    student = current_user.student
    
    if not student:
        flash('Không tìm thấy thông tin sinh viên!', 'danger')
        return redirect(url_for('main.index'))
    
    # Tính GPA
    gpa = student.calculate_gpa()
    
    # Số môn đã học
    total_subjects = student.grades.count()
    
    # Số tín chỉ tích lũy
    total_credits = sum([g.subject.credits for g in student.grades if g.subject and g.score_total and g.score_total >= 4.0])
    
    # Lịch học hôm nay
    from datetime import datetime
    today = datetime.now().weekday()
    today_schedules = []
    if student.classroom:
        today_schedules = Schedule.query.filter_by(
            class_id=student.classroom.id,
            day_of_week=today
        ).order_by(Schedule.start_time).all()
    
    # Điểm gần đây
    recent_grades = student.grades.order_by(Grade.updated_at.desc()).limit(5).all()
    
    return render_template('student/dashboard.html',
                           student=student,
                           gpa=gpa,
                           total_subjects=total_subjects,
                           total_credits=total_credits,
                           today_schedules=today_schedules,
                           recent_grades=recent_grades)


@student_bp.route('/schedule')
@login_required
@student_required
def schedule():
    """Xem thời khóa biểu"""
    student = current_user.student
    
    if not student or not student.classroom:
        flash('Bạn chưa được phân lớp!', 'warning')
        return render_template('student/schedule.html', schedules=[], schedule_by_day={})
    
    schedules = Schedule.query.filter_by(class_id=student.classroom.id).order_by(
        Schedule.day_of_week, Schedule.start_time
    ).all()
    
    # Nhóm theo ngày
    schedule_by_day = {}
    for s in schedules:
        day = s.day_of_week
        if day not in schedule_by_day:
            schedule_by_day[day] = []
        schedule_by_day[day].append(s)
    
    return render_template('student/schedule.html', 
                           schedules=schedules,
                           schedule_by_day=schedule_by_day)


@student_bp.route('/grades')
@login_required
@student_required
def grades():
    """Xem kết quả học tập"""
    student = current_user.student
    
    if not student:
        flash('Không tìm thấy thông tin sinh viên!', 'danger')
        return redirect(url_for('main.index'))
    
    # Lấy tất cả điểm, nhóm theo học kỳ
    grades = student.grades.order_by(Grade.semester.desc()).all()
    
    # Nhóm theo học kỳ
    grades_by_semester = {}
    for g in grades:
        semester = g.semester or 'Không xác định'
        if semester not in grades_by_semester:
            grades_by_semester[semester] = []
        grades_by_semester[semester].append(g)
    
    # Tính GPA tổng
    gpa = student.calculate_gpa()
    
    return render_template('student/grades.html',
                           student=student,
                           grades_by_semester=grades_by_semester,
                           gpa=gpa)


@student_bp.route('/materials')
@login_required
@student_required
def materials():
    """Xem và tải tài liệu"""
    student = current_user.student
    
    # Lấy các môn học sinh viên đang học
    schedules = []
    if student and student.classroom:
        schedules = Schedule.query.filter_by(class_id=student.classroom.id).all()
    
    subject_ids = list(set([s.subject_id for s in schedules]))
    
    # Lấy tài liệu của các môn này
    materials = Material.query.filter(Material.subject_id.in_(subject_ids)).order_by(
        Material.created_at.desc()
    ).all() if subject_ids else []
    
    return render_template('student/materials.html', materials=materials)


@student_bp.route('/materials/download/<int:id>')
@login_required
@student_required
def download_material(id):
    """Tải tài liệu"""
    material = Material.query.get_or_404(id)
    
    if not material.file_path:
        flash('Tài liệu không có file đính kèm!', 'warning')
        return redirect(url_for('student.materials'))
    
    # Tăng lượt tải
    material.download_count += 1
    db.session.commit()
    
    directory = os.path.join(current_app.config['UPLOAD_FOLDER'])
    filename = material.file_path.replace('materials/', '')
    return send_from_directory(os.path.join(directory, 'materials'), filename, as_attachment=True)


@student_bp.route('/evaluations')
@login_required
@student_required
def evaluations():
    """Đánh giá giảng viên"""
    student = current_user.student
    
    # Lấy các giảng viên đang dạy sinh viên này
    schedules = []
    if student and student.classroom:
        schedules = Schedule.query.filter_by(class_id=student.classroom.id).all()
    
    # Lấy các đánh giá đã thực hiện
    my_evaluations = Evaluation.query.filter_by(student_id=student.id).all() if student else []
    evaluated_keys = set([(e.lecturer_id, e.subject_id) for e in my_evaluations])
    
    # Danh sách giảng viên có thể đánh giá
    lecturers_to_evaluate = []
    for s in schedules:
        key = (s.lecturer_id, s.subject_id)
        if key not in evaluated_keys:
            lecturers_to_evaluate.append({
                'lecturer': s.lecturer,
                'subject': s.subject
            })
    
    return render_template('student/evaluations/list.html',
                           my_evaluations=my_evaluations,
                           lecturers_to_evaluate=lecturers_to_evaluate)


@student_bp.route('/evaluations/add/<int:lecturer_id>/<int:subject_id>', methods=['GET', 'POST'])
@login_required
@student_required
def add_evaluation(lecturer_id, subject_id):
    """Thêm đánh giá"""
    student = current_user.student
    lecturer = Lecturer.query.get_or_404(lecturer_id)
    subject = Subject.query.get_or_404(subject_id)
    
    # Kiểm tra đã đánh giá chưa
    existing = Evaluation.query.filter_by(
        student_id=student.id,
        lecturer_id=lecturer_id,
        subject_id=subject_id
    ).first()
    
    if existing:
        flash('Bạn đã đánh giá giảng viên này cho môn học này rồi!', 'warning')
        return redirect(url_for('student.evaluations'))
    
    form = EvaluationForm()
    form.lecturer_id.choices = [(lecturer.id, lecturer.full_name)]
    form.subject_id.choices = [(subject.id, subject.name)]
    
    if form.validate_on_submit():
        evaluation = Evaluation(
            student_id=student.id,
            lecturer_id=lecturer_id,
            subject_id=subject_id,
            rating=int(form.rating.data),
            comment=form.comment.data,
            semester='HK2-2024',
            is_anonymous=True
        )
        db.session.add(evaluation)
        db.session.commit()
        
        flash('Đã gửi đánh giá thành công! Cảm ơn bạn đã phản hồi.', 'success')
        return redirect(url_for('student.evaluations'))
    
    return render_template('student/evaluations/form.html',
                           form=form,
                           lecturer=lecturer,
                           subject=subject)

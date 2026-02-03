from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager


# ==================== USER MODEL ====================
class User(UserMixin, db.Model):
    """Model người dùng - Quản lý đăng nhập và phân quyền"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # admin, lecturer, student
    avatar = db.Column(db.String(200), default='default_avatar.png')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('Student', backref='user', uselist=False, lazy=True)
    lecturer = db.relationship('Lecturer', backref='user', uselist=False, lazy=True)
    
    def set_password(self, password):
        """Mã hóa và lưu mật khẩu"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Kiểm tra mật khẩu"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_lecturer(self):
        return self.role == 'lecturer'
    
    def is_student(self):
        return self.role == 'student'
    
    def get_display_name(self):
        """Lấy tên hiển thị"""
        if self.role == 'student' and self.student:
            return self.student.full_name
        elif self.role == 'lecturer' and self.lecturer:
            return self.lecturer.full_name
        return self.username
    
    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """Load user cho Flask-Login"""
    return User.query.get(int(user_id))


# ==================== MAJOR MODEL ====================
class Major(db.Model):
    """Model Chuyên ngành/Ngành học"""
    __tablename__ = 'majors'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    students = db.relationship('Student', backref='major', lazy='dynamic')
    classrooms = db.relationship('Classroom', backref='major', lazy='dynamic')
    
    def __repr__(self):
        return f'<Major {self.name}>'


# ==================== CLASSROOM MODEL ====================
class Classroom(db.Model):
    """Model Lớp hành chính"""
    __tablename__ = 'classrooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    major_id = db.Column(db.Integer, db.ForeignKey('majors.id'))
    advisor_id = db.Column(db.Integer, db.ForeignKey('lecturers.id'))  # Cố vấn học tập
    academic_year = db.Column(db.String(20))  # Niên khóa VD: 2020-2024
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    students = db.relationship('Student', backref='classroom', lazy='dynamic')
    schedules = db.relationship('Schedule', backref='classroom', lazy='dynamic')
    
    def __repr__(self):
        return f'<Classroom {self.name}>'


# ==================== LECTURER MODEL ====================
class Lecturer(db.Model):
    """Model Giảng viên"""
    __tablename__ = 'lecturers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lecturer_code = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))  # Khoa/Bộ môn
    expertise = db.Column(db.String(200))   # Chuyên môn
    phone = db.Column(db.String(15))
    degree = db.Column(db.String(50))  # Học vị: ThS, TS, PGS, GS
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    advised_classes = db.relationship('Classroom', backref='advisor', lazy='dynamic',
                                       foreign_keys='Classroom.advisor_id')
    schedules = db.relationship('Schedule', backref='lecturer', lazy='dynamic')
    materials = db.relationship('Material', backref='uploader', lazy='dynamic')
    evaluations = db.relationship('Evaluation', backref='lecturer', lazy='dynamic')
    
    def get_average_rating(self):
        """Tính điểm đánh giá trung bình"""
        ratings = [e.rating for e in self.evaluations if e.rating]
        return round(sum(ratings) / len(ratings), 1) if ratings else 0
    
    def __repr__(self):
        return f'<Lecturer {self.full_name}>'


# ==================== STUDENT MODEL ====================
class Student(db.Model):
    """Model Sinh viên"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_code = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date)  # Ngày sinh
    gender = db.Column(db.String(10))  # Nam/Nữ
    phone = db.Column(db.String(15))
    address = db.Column(db.String(200))
    class_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'))
    major_id = db.Column(db.Integer, db.ForeignKey('majors.id'))
    enrollment_year = db.Column(db.Integer)  # Năm nhập học
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    grades = db.relationship('Grade', backref='student', lazy='dynamic')
    evaluations = db.relationship('Evaluation', backref='student', lazy='dynamic')
    
    def calculate_gpa(self):
        """Tính GPA tổng"""
        total_credits = 0
        weighted_sum = 0
        for grade in self.grades:
            if grade.score_total is not None and grade.subject:
                total_credits += grade.subject.credits
                weighted_sum += grade.score_total * grade.subject.credits
        return round(weighted_sum / total_credits, 2) if total_credits > 0 else 0
    
    def get_grade_letter(self, score):
        """Chuyển điểm số sang điểm chữ"""
        if score >= 8.5:
            return 'A'
        elif score >= 7.0:
            return 'B'
        elif score >= 5.5:
            return 'C'
        elif score >= 4.0:
            return 'D'
        else:
            return 'F'
    
    def __repr__(self):
        return f'<Student {self.full_name}>'


# ==================== SUBJECT MODEL ====================
class Subject(db.Model):
    """Model Môn học"""
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer, nullable=False, default=3)
    description = db.Column(db.Text)
    theory_hours = db.Column(db.Integer, default=30)  # Số giờ lý thuyết
    practice_hours = db.Column(db.Integer, default=15)  # Số giờ thực hành
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    schedules = db.relationship('Schedule', backref='subject', lazy='dynamic')
    grades = db.relationship('Grade', backref='subject', lazy='dynamic')
    materials = db.relationship('Material', backref='subject', lazy='dynamic')
    
    def __repr__(self):
        return f'<Subject {self.name}>'


# ==================== SCHEDULE MODEL ====================
class Schedule(db.Model):
    """Model Lịch học/Lịch dạy"""
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturers.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False)
    room_name = db.Column(db.String(50))  # Phòng học VD: A101, B202
    day_of_week = db.Column(db.Integer)   # 0=Thứ 2, 1=Thứ 3, ..., 6=Chủ nhật
    start_time = db.Column(db.Time)       # Giờ bắt đầu
    end_time = db.Column(db.Time)         # Giờ kết thúc
    semester = db.Column(db.String(20))   # VD: HK1-2024, HK2-2024
    start_date = db.Column(db.Date)       # Ngày bắt đầu học kỳ
    end_date = db.Column(db.Date)         # Ngày kết thúc học kỳ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    DAY_NAMES = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']
    
    def get_day_name(self):
        """Lấy tên thứ trong tuần"""
        if self.day_of_week is not None and 0 <= self.day_of_week <= 6:
            return self.DAY_NAMES[self.day_of_week]
        return ''
    
    def __repr__(self):
        return f'<Schedule {self.subject.name if self.subject else "Unknown"} - {self.get_day_name()}>'


# ==================== GRADE MODEL ====================
class Grade(db.Model):
    """Model Điểm số"""
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    score_attendance = db.Column(db.Float, default=0)   # Điểm chuyên cần
    score_midterm = db.Column(db.Float, default=0)      # Điểm giữa kỳ
    score_final = db.Column(db.Float, default=0)        # Điểm cuối kỳ
    score_total = db.Column(db.Float)                   # Điểm tổng kết
    semester = db.Column(db.String(20))
    note = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint để 1 sinh viên chỉ có 1 bảng điểm cho 1 môn trong 1 học kỳ
    __table_args__ = (db.UniqueConstraint('student_id', 'subject_id', 'semester', name='unique_student_subject_semester'),)
    
    def calculate_total(self):
        """Tính điểm tổng kết: Chuyên cần 10%, Giữa kỳ 30%, Cuối kỳ 60%"""
        attendance = self.score_attendance or 0
        midterm = self.score_midterm or 0
        final = self.score_final or 0
        self.score_total = round(attendance * 0.1 + midterm * 0.3 + final * 0.6, 2)
        return self.score_total
    
    def get_letter_grade(self):
        """Lấy điểm chữ"""
        if self.score_total is None:
            return '-'
        if self.score_total >= 8.5:
            return 'A'
        elif self.score_total >= 7.0:
            return 'B'
        elif self.score_total >= 5.5:
            return 'C'
        elif self.score_total >= 4.0:
            return 'D'
        else:
            return 'F'
    
    def __repr__(self):
        return f'<Grade {self.student.full_name if self.student else "Unknown"} - {self.subject.name if self.subject else "Unknown"}>'


# ==================== MATERIAL MODEL ====================
class Material(db.Model):
    """Model Tài liệu học tập"""
    __tablename__ = 'materials'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('lecturers.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(300))  # Đường dẫn file
    file_type = db.Column(db.String(20))   # pdf, docx, pptx, etc.
    file_size = db.Column(db.Integer)      # Kích thước file (bytes)
    download_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_file_size_formatted(self):
        """Format kích thước file"""
        if not self.file_size:
            return '0 KB'
        if self.file_size < 1024:
            return f'{self.file_size} B'
        elif self.file_size < 1024 * 1024:
            return f'{self.file_size / 1024:.1f} KB'
        else:
            return f'{self.file_size / (1024 * 1024):.1f} MB'
    
    def __repr__(self):
        return f'<Material {self.title}>'


# ==================== EVALUATION MODEL ====================
class Evaluation(db.Model):
    """Model Đánh giá giảng viên"""
    __tablename__ = 'evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturers.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    rating = db.Column(db.Integer, nullable=False)  # 1-5 sao
    comment = db.Column(db.Text)
    semester = db.Column(db.String(20))
    is_anonymous = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint để 1 SV chỉ đánh giá 1 GV cho 1 môn 1 lần/kỳ
    __table_args__ = (db.UniqueConstraint('student_id', 'lecturer_id', 'subject_id', 'semester', 
                                          name='unique_evaluation'),)
    
    def __repr__(self):
        return f'<Evaluation {self.rating} stars>'

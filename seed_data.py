"""
Script tạo dữ liệu mẫu cho hệ thống
Chạy: python seed_data.py
"""

from datetime import date, time
from app import create_app, db
from app.models import User, Student, Lecturer, Major, Classroom, Subject, Schedule, Grade

app = create_app('development')


def seed_database():
    """Tạo dữ liệu mẫu"""
    with app.app_context():
        # Tạo database
        db.create_all()
        
        # Kiểm tra nếu đã có dữ liệu
        if User.query.first():
            print("Dữ liệu đã tồn tại. Bỏ qua seeding.")
            return
        
        print("Đang tạo dữ liệu mẫu...")
        
        # ==================== ADMIN ====================
        admin = User(
            username='admin',
            email='admin@ums.edu.vn',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # ==================== MAJORS ====================
        majors_data = [
            ('CNTT', 'Công nghệ Thông tin', 'Đào tạo kỹ sư phần mềm, hệ thống thông tin'),
            ('QTKD', 'Quản trị Kinh doanh', 'Đào tạo quản lý doanh nghiệp'),
            ('KT', 'Kế toán', 'Đào tạo kế toán viên, kiểm toán viên'),
            ('DTVT', 'Điện tử Viễn thông', 'Đào tạo kỹ sư điện tử'),
            ('ATTT', 'An toàn Thông tin', 'Đào tạo chuyên gia bảo mật')
        ]
        
        majors = []
        for code, name, desc in majors_data:
            major = Major(code=code, name=name, description=desc)
            db.session.add(major)
            majors.append(major)
        
        db.session.flush()
        
        # ==================== LECTURERS ====================
        lecturers_data = [
            ('GV001', 'Nguyễn Văn An', 'lecturer1', 'nguyen.an@ums.edu.vn', 'Khoa CNTT', 'Lập trình', 'TS'),
            ('GV002', 'Trần Thị Bình', 'lecturer2', 'tran.binh@ums.edu.vn', 'Khoa CNTT', 'Cơ sở dữ liệu', 'ThS'),
            ('GV003', 'Lê Văn Cường', 'lecturer3', 'le.cuong@ums.edu.vn', 'Khoa QTKD', 'Marketing', 'PGS'),
            ('GV004', 'Phạm Thị Dung', 'lecturer4', 'pham.dung@ums.edu.vn', 'Khoa KT', 'Kế toán quản trị', 'ThS'),
            ('GV005', 'Hoàng Văn Em', 'lecturer5', 'hoang.em@ums.edu.vn', 'Khoa DTVT', 'Mạng máy tính', 'TS'),
        ]
        
        lecturers = []
        for lec_code, name, username, email, dept, expertise, degree in lecturers_data:
            user = User(username=username, email=email, role='lecturer')
            user.set_password('123456')
            db.session.add(user)
            db.session.flush()
            
            lecturer = Lecturer(
                user_id=user.id,
                lecturer_code=lec_code,
                full_name=name,
                department=dept,
                expertise=expertise,
                degree=degree
            )
            db.session.add(lecturer)
            lecturers.append(lecturer)
        
        db.session.flush()
        
        # ==================== CLASSROOMS ====================
        classrooms_data = [
            ('CNTT-K20A', majors[0].id, lecturers[0].id, '2020-2024'),
            ('CNTT-K20B', majors[0].id, lecturers[1].id, '2020-2024'),
            ('QTKD-K21A', majors[1].id, lecturers[2].id, '2021-2025'),
            ('KT-K21A', majors[2].id, lecturers[3].id, '2021-2025'),
            ('DTVT-K22A', majors[3].id, lecturers[4].id, '2022-2026'),
        ]
        
        classrooms = []
        for name, major_id, advisor_id, year in classrooms_data:
            classroom = Classroom(
                name=name,
                major_id=major_id,
                advisor_id=advisor_id,
                academic_year=year
            )
            db.session.add(classroom)
            classrooms.append(classroom)
        
        db.session.flush()
        
        # ==================== STUDENTS ====================
        students_data = [
            ('SV001', 'Nguyễn Thị Hương', 'student1', 'hương.nguyen@student.edu.vn', 'Nữ', classrooms[0], majors[0]),
            ('SV002', 'Trần Văn Minh', 'student2', 'minh.tran@student.edu.vn', 'Nam', classrooms[0], majors[0]),
            ('SV003', 'Lê Thị Lan', 'student3', 'lan.le@student.edu.vn', 'Nữ', classrooms[0], majors[0]),
            ('SV004', 'Phạm Văn Đức', 'student4', 'duc.pham@student.edu.vn', 'Nam', classrooms[1], majors[0]),
            ('SV005', 'Hoàng Thị Mai', 'student5', 'mai.hoang@student.edu.vn', 'Nữ', classrooms[1], majors[0]),
            ('SV006', 'Vũ Văn Nam', 'student6', 'nam.vu@student.edu.vn', 'Nam', classrooms[2], majors[1]),
            ('SV007', 'Đặng Thị Oanh', 'student7', 'oanh.dang@student.edu.vn', 'Nữ', classrooms[2], majors[1]),
            ('SV008', 'Bùi Văn Phong', 'student8', 'phong.bui@student.edu.vn', 'Nam', classrooms[3], majors[2]),
            ('SV009', 'Ngô Thị Quỳnh', 'student9', 'quynh.ngo@student.edu.vn', 'Nữ', classrooms[3], majors[2]),
            ('SV010', 'Đinh Văn Sơn', 'student10', 'son.dinh@student.edu.vn', 'Nam', classrooms[4], majors[3]),
        ]
        
        students = []
        for code, name, username, email, gender, classroom, major in students_data:
            user = User(username=username, email=email, role='student')
            user.set_password('123456')
            db.session.add(user)
            db.session.flush()
            
            student = Student(
                user_id=user.id,
                student_code=code,
                full_name=name,
                gender=gender,
                dob=date(2002, 1, 15),
                class_id=classroom.id,
                major_id=major.id,
                enrollment_year=2020
            )
            db.session.add(student)
            students.append(student)
        
        db.session.flush()
        
        # ==================== SUBJECTS ====================
        subjects_data = [
            ('IT001', 'Lập trình Python', 3, 30, 15),
            ('IT002', 'Cơ sở Dữ liệu', 4, 45, 15),
            ('IT003', 'Mạng máy tính', 3, 30, 15),
            ('IT004', 'Lập trình Web', 4, 30, 30),
            ('IT005', 'Trí tuệ Nhân tạo', 3, 30, 15),
            ('BA001', 'Quản trị Học', 3, 45, 0),
            ('BA002', 'Marketing cơ bản', 3, 45, 0),
            ('AC001', 'Kế toán đại cương', 3, 45, 0),
            ('AC002', 'Kế toán tài chính', 4, 45, 15),
            ('EE001', 'Điện tử cơ bản', 3, 30, 15),
        ]
        
        subjects = []
        for code, name, credits, theory, practice in subjects_data:
            subject = Subject(
                code=code,
                name=name,
                credits=credits,
                theory_hours=theory,
                practice_hours=practice
            )
            db.session.add(subject)
            subjects.append(subject)
        
        db.session.flush()
        
        # ==================== SCHEDULES ====================
        schedules_data = [
            (subjects[0], lecturers[0], classrooms[0], 'A101', 0, time(7, 30), time(9, 30), 'HK2-2024'),
            (subjects[1], lecturers[1], classrooms[0], 'B202', 1, time(13, 0), time(15, 0), 'HK2-2024'),
            (subjects[2], lecturers[4], classrooms[0], 'C303', 2, time(9, 30), time(11, 30), 'HK2-2024'),
            (subjects[3], lecturers[0], classrooms[0], 'Lab01', 3, time(7, 30), time(11, 30), 'HK2-2024'),
            (subjects[0], lecturers[0], classrooms[1], 'A102', 0, time(13, 0), time(15, 0), 'HK2-2024'),
            (subjects[5], lecturers[2], classrooms[2], 'D101', 1, time(7, 30), time(9, 30), 'HK2-2024'),
            (subjects[6], lecturers[2], classrooms[2], 'D101', 3, time(13, 0), time(15, 0), 'HK2-2024'),
            (subjects[7], lecturers[3], classrooms[3], 'E201', 2, time(7, 30), time(9, 30), 'HK2-2024'),
            (subjects[9], lecturers[4], classrooms[4], 'Lab02', 4, time(9, 30), time(11, 30), 'HK2-2024'),
        ]
        
        for subj, lec, cls, room, day, start, end, sem in schedules_data:
            schedule = Schedule(
                subject_id=subj.id,
                lecturer_id=lec.id,
                class_id=cls.id,
                room_name=room,
                day_of_week=day,
                start_time=start,
                end_time=end,
                semester=sem
            )
            db.session.add(schedule)
        
        # ==================== GRADES ====================
        # Thêm điểm mẫu cho một số sinh viên
        import random
        for i, student in enumerate(students[:5]):
            for subject in subjects[:4]:
                attendance = round(random.uniform(7, 10), 1)
                midterm = round(random.uniform(5, 9), 1)
                final = round(random.uniform(5, 9), 1)
                
                grade = Grade(
                    student_id=student.id,
                    subject_id=subject.id,
                    score_attendance=attendance,
                    score_midterm=midterm,
                    score_final=final,
                    semester='HK1-2024'
                )
                grade.calculate_total()
                db.session.add(grade)
        
        db.session.commit()
        print("✅ Tạo dữ liệu mẫu thành công!")
        print("\n📋 Tài khoản đăng nhập:")
        print("   Admin:    admin / admin123")
        print("   Giảng viên: lecturer1 / 123456")
        print("   Sinh viên:  student1 / 123456")


if __name__ == '__main__':
    seed_database()

"""
Hệ Thống Quản Lý Đại Học (UMS)
File chạy chính của ứng dụng
"""

from app import create_app, db
from app.models import User, Student, Lecturer, Major, Classroom, Subject, Schedule, Grade, Material, Evaluation

app = create_app('development')


@app.shell_context_processor
def make_shell_context():
    """Context cho Flask shell"""
    return {
        'db': db,
        'User': User,
        'Student': Student,
        'Lecturer': Lecturer,
        'Major': Major,
        'Classroom': Classroom,
        'Subject': Subject,
        'Schedule': Schedule,
        'Grade': Grade,
        'Material': Material,
        'Evaluation': Evaluation
    }


if __name__ == '__main__':
    with app.app_context():
        # Tạo database nếu chưa tồn tại
        db.create_all()
        print("✅ Database đã sẵn sàng!")
        print(f"🌐 Ứng dụng đang chạy tại: http://127.0.0.1:5000")
        print("📝 Tài khoản demo: admin / admin123")
    
    # Sử dụng use_reloader=False để tránh lỗi watchdog
    app.run(debug=True, port=5000, use_reloader=False)

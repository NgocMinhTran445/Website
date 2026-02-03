# BÁO CÁO ĐỒ ÁN MÔN HỌC LẬP TRÌNH WEB
## ĐỀ TÀI: XÂY DỰNG HỆ THỐNG QUẢN LÝ ĐẠI HỌC (UNIVERSITY MANAGEMENT SYSTEM - UMS)

---

**Sinh viên thực hiện:** [Tên Sinh Viên]
**Mã số sinh viên:** [MSSV]
**Lớp:** [Tên Lớp]
**Giảng viên hướng dẫn:** [Tên Giảng Viên]

---

## MỤC LỤC

1. [CHƯƠNG 1: GIỚI THIỆU ĐỀ TÀI](#chương-1-giới-thiệu-đề-tài)
    - 1.1. Lý do chọn đề tài
    - 1.2. Mục tiêu đề tài
    - 1.3. Phạm vi nghiên cứu
2. [CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ](#chương-2-cơ-sở-lý-thuyết-và-công-nghệ)
    - 2.1. Ngôn ngữ Python
    - 2.2. Flask Framework
    - 2.3. Hệ quản trị CSDL SQLite/SQLAlchemy
    - 2.4. Bootstrap 5
3. [CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG](#chương-3-phân-tích-và-thiết-kế-hệ-thống)
    - 3.1. Phân tích yêu cầu chức năng
        - 3.1.1. Phân hệ Admin (Quản trị viên)
        - 3.1.2. Phân hệ Giảng viên (Lecturer)
        - 3.1.3. Phân hệ Sinh viên (Student)
    - 3.2. Thiết kế Cơ sở dữ liệu (Database Design)
4. [CHƯƠNG 4: CÀI ĐẶT VÀ TRIỂN KHAI](#chương-4-cài-đặt-và-triển-khai)
    - 4.1. Cấu trúc dự án
    - 4.2. Hướng dẫn cài đặt và chạy ứng dụng
    - 4.3. Mô tả chi tiết các màn hình chính
5. [CHƯƠNG 5: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN](#chương-5-kết-luận-và-hướng-phát-triển)

---

## CHƯƠNG 1: GIỚI THIỆU ĐỀ TÀI

### 1.1. Lý do chọn đề tài
Trong kỷ nguyên số hóa hiện nay, việc ứng dụng công nghệ thông tin vào quản lý giáo dục là một nhu cầu cấp thiết. Các trường đại học cần một hệ thống quản lý tập trung, hiệu quả để kết nối giữa Nhà trường, Giảng viên và Sinh viên. Hệ thống Quản lý Đại học (UMS) ra đời nhằm giải quyết bài toán quản lý thông tin, lịch học, điểm số và tài liệu một cách khoa học, minh bạch và nhanh chóng.

### 1.2. Mục tiêu đề tài
Xây dựng một ứng dụng web hoàn chỉnh phục vụ công tác quản lý đào tạo với các mục tiêu cụ thể:
- **Quản lý tập trung:** Lưu trữ và quản lý thông tin sinh viên, giảng viên, môn học, lớp học trên một nền tảng duy nhất.
- **Tự động hóa:** Giảm thiểu các thao tác thủ công trong việc xếp lịch, nhập điểm, và thống kê báo cáo.
- **Tương tác hiệu quả:** Cung cấp kênh giao tiếp và chia sẻ tài liệu giữa giảng viên và sinh viên.
- **Minh bạch thông tin:** Giúp sinh viên dễ dàng theo dõi tiến độ học tập, điểm số và lịch học cá nhân.

### 1.3. Phạm vi nghiên cứu
Hệ thống tập trung vào các chức năng cốt lõi của một trường đại học quy mô vừa và nhỏ, bao gồm:
- Quản lý người dùng và phân quyền (Admin, Giảng viên, Sinh viên).
- Quản lý danh mục đào tạo (Khoa, Ngành, Lớp, Môn học).
- Quản lý lịch học và lịch giảng dạy.
- Quản lý điểm số và kết quả học tập.
- Quản lý tài liệu học tập và đánh giá giảng viên.

---

## CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ

Hệ thống được xây dựng dựa trên các công nghệ hiện đại, mã nguồn mở, đảm bảo tính ổn định và dễ dàng mở rộng.

### 2.1. Ngôn ngữ Python
Python là ngôn ngữ lập trình bậc cao, thông dịch, hướng đối tượng, nổi tiếng với cú pháp rõ ràng và thư viện phong phú. Trong dự án này, Python được sử dụng làm ngôn ngữ backend chính xử lý logic nghiệp vụ.

### 2.2. Flask Framework
Flask là một micro-framework web viết bằng Python.
- **Ưu điểm:** Nhẹ, linh hoạt, dễ mở rộng, không áp đặt cấu trúc thư mục cứng nhắc.
- **Các thư viện đi kèm:**
    - `Flask-SQLAlchemy`: ORM để làm việc với cơ sở dữ liệu.
    - `Flask-Login`: Quản lý session và xác thực người dùng.
    - `Flask-WTF`: Xử lý form và validate dữ liệu.
    - `Flask-Migrate`: Quản lý migration database.

### 2.3. Hệ quản trị CSDL SQLite/SQLAlchemy
- **SQLite:** CSDL quan hệ nhỏ gọn, không cần cấu hình server phức tạp, phù hợp cho phát triển và deployment quy mô nhỏ.
- **SQLAlchemy:** ORM (Object Relational Mapping) mạnh mẽ nhất của Python, giúp thao tác với dữ liệu thông qua các đối tượng Python thay vì viết câu lệnh SQL thuần.

### 2.4. Bootstrap 5
Framework CSS/JS phổ biến nhất thế giới để xây dựng giao diện web responsive (tương thích mọi thiết bị) và hiện đại. Dự án sử dụng Bootstrap 5 kết hợp với Font Awesome cho các icon trực quan.

---

## CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

### 3.1. Phân tích yêu cầu chức năng

Hệ thống được chia làm 3 phân hệ chính tương ứng với 3 vai trò người dùng (Actors).

#### 3.1.1. Phân hệ Admin (Quản trị viên)
Là người chịu trách nhiệm cấu hình và quản lý dữ liệu toàn hệ thống.
- **Đăng nhập/Đăng xuất:** Bảo mật thông tin quản trị.
- **Dashboard:** Xem thống kê tổng quan (số lượng SV, GV, Môn học...).
- **Quản lý Sinh viên:** Thêm, xem danh sách, sửa thông tin, xóa sinh viên.
- **Quản lý Giảng viên:** Thêm, xem, sửa, xóa giảng viên.
- **Quản lý Ngành đào tạo (Major):** Định nghĩa các ngành học trong trường.
- **Quản lý Lớp (Classroom):** Tạo lớp hành chính, phân công cố vấn học tập.
- **Quản lý Môn học (Subject):** Định nghĩa môn học, số tín chỉ, giờ lý thuyết/thực hành.
- **Quản lý Lịch học (Schedule):** Xếp lịch học cho các lớp theo môn, phòng và thời gian.

#### 3.1.2. Phân hệ Giảng viên (Lecturer)
- **Đăng nhập/Đổi mật khẩu:** Truy cập tài khoản cá nhân.
- **Xem Lịch dạy:** Theo dõi lịch giảng dạy cá nhân trong học kỳ.
- **Quản lý Điểm số:** Nhập và chỉnh sửa điểm thành phần (chuyên cần, giữa kỳ, cuối kỳ) cho sinh viên các lớp mình dạy.
- **Quản lý Tài liệu:** Upload/Xóa tài liệu môn học để chia sẻ với sinh viên.
- **Quản lý Lớp cố vấn:** Xem danh sách sinh viên thuộc lớp mình chủ nhiệm.
- **Xem Đánh giá:** Xem kết quả đánh giá từ sinh viên (ẩn danh).

#### 3.1.3. Phân hệ Sinh viên (Student)
- **Đăng nhập/Đổi mật khẩu:** Truy cập tài khoản cá nhân.
- **Xem Lịch học:** Theo dõi thời khóa biểu học tập.
- **Xem Điểm:** Tra cứu bảng điểm các môn đã học, xem điểm tổng kết và điểm chữ (A, B, C...).
- **Tài liệu học tập:** Tải về tài liệu do giảng viên chia sẻ.
- **Đánh giá Giảng viên:** Thực hiện đánh giá chất lượng giảng dạy của giảng viên (Rating 1-5 sao).

### 3.2. Thiết kế Cơ sở dữ liệu (Database Design)

Hệ thống sử dụng mô hình dữ liệu quan hệ với các bảng (Entities) chính sau:

1.  **users**: Bảng trung tâm lưu trữ thông tin đăng nhập.
    - `id` (PK), `username`, `email`, `password_hash`, `role` (admin/lecturer/student).

2.  **majors** (Ngành học):
    - `id`, `code`, `name`, `description`.

3.  **classrooms** (Lớp hành chính):
    - `id`, `name`, `major_id` (FK), `advisor_id` (FK - GV cố vấn).

4.  **lecturers** (Giảng viên - mở rộng từ user):
    - `id`, `user_id` (FK), `lecturer_code`, `full_name`, `department`, `degree`.

5.  **students** (Sinh viên - mở rộng từ user):
    - `id`, `user_id` (FK), `student_code`, `full_name`, `class_id` (FK), `major_id` (FK).

6.  **subjects** (Môn học):
    - `id`, `code`, `name`, `credits`.

7.  **schedules** (Thời khóa biểu):
    - `id`, `subject_id` (FK), `lecturer_id` (FK), `class_id` (FK), `room_name`, `day_of_week`, `time`.

8.  **grades** (Bảng điểm):
    - `id`, `student_id`, `subject_id`, `score_attendance`, `score_midterm`, `score_final`.

9.  **materials** (Tài liệu):
    - `id`, `subject_id`, `lecturer_id`, `file_path`.

10. **evaluations** (Đánh giá):
    - `id`, `student_id`, `lecturer_id`, `subject_id`, `rating`, `comment`.

---

## CHƯƠNG 4: CÀI ĐẶT VÀ TRIỂN KHAI

### 4.1. Cấu trúc dự án
Mã nguồn được tổ chức theo mô hình MVC (Model-View-Controller) giúp dễ dàng quản lý và bảo trì:

```text
/deadlineWebb20250113
├── app/
│   ├── models.py           # Định nghĩa Database Models
│   ├── routes/             # Controllers xử lý logic
│   │   ├── admin.py        # Logic cho Admin
│   │   ├── auth.py         # Logic xác thực
│   │   ├── lecturer.py     # Logic cho Giảng viên
│   │   └── student.py      # Logic cho Sinh viên
│   ├── templates/          # Views (Files HTML)
│   │   ├── admin/          # Giao diện Admin
│   │   ├── lecturer/       # Giao diện Giảng viên
│   │   └── student/        # Giao diện Sinh viên
│   └── static/             # CSS, JS, Images, Uploads
├── config.py               # Cấu hình hệ thống environment
├── run.py                  # File khởi chạy ứng dụng
├── requirements.txt        # Danh sách thư viện
└── seed_data.py            # Script tạo dữ liệu mẫu
```

### 4.2. Hướng dẫn cài đặt và chạy ứng dụng

**Yêu cầu hệ thống:** Python 3.8 trở lên.

**Bước 1:** Cài đặt thư viện phụ thuộc
```bash
pip install -r requirements.txt
```

**Bước 2:** Khởi tạo cơ sở dữ liệu và dữ liệu mẫu (Seeding)
Hệ thống cung cấp script tự động tạo database `ums.db` và các tài khoản mẫu.
```bash
python seed_data.py
```

**Bước 3:** Khởi chạy server
```bash
python run.py
```
Ứng dụng sẽ chạy tại địa chỉ: `http://127.0.0.1:5000`

**Thông tin tài khoản kiểm thử (Demo Accounts):**
- **Admin:** `admin` / `admin123`
- **Giảng viên:** `lecturer1` / `123456`
- **Sinh viên:** `student1` / `123456`

### 4.3. Mô tả các màn hình chính

#### 1. Màn hình Đăng nhập (Login)
Giao diện tập trung, đơn giản, bảo mật. Hệ thống tự động điều hướng người dùng đến Dashboard tương ứng dựa trên vai trò (Role) sau khi đăng nhập thành công.

#### 2. Dashboard Admin
Hiển thị các thẻ (Cards) thống kê số liệu tổng quan của hệ thống. Sidebar bên trái giúp Admin truy cập nhanh vào các chức năng quản lý CRUD (Create, Read, Update, Delete) cho Sinh viên, Giảng viên, Môn học, v.v.

#### 3. Màn hình Quản lý Điểm (Giảng viên)
Giảng viên chọn Môn học và Lớp học để hiển thị danh sách sinh viên. Giao diện dạng bảng cho phép nhập trực tiếp điểm Chuyên cần, Giữa kỳ, Cuối kỳ. Hệ thống tự động tính toán điểm Tổng kết và convert sang điểm Chữ.

#### 4. Màn hình Kết quả học tập (Sinh viên)
Sinh viên xem được bảng điểm chi tiết của mình theo từng học kỳ. Bao gồm tên môn, số tín chỉ, các đầu điểm thành phần và kết quả Đạt/Không đạt.

---

## CHƯƠNG 5: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

### 5.1. Kết quả đạt được
Dự án đã xây dựng thành công Hệ thống Quản lý Đại học UMS với đầy đủ các tính năng cơ bản theo yêu cầu:
- ✅ Hoàn thiện mô hình dữ liệu quan hệ chuẩn hóa.
- ✅ Phân quyền chặt chẽ 3 cấp độ: Admin, Lecturer, Student.
- ✅ Giao diện thân thiện, dễ sử dụng, chuẩn Bootstrap 5.
- ✅ Quy trình nghiệp vụ (Xếp lịch -> Dạy -> Nhập điểm -> Xem điểm) hoạt động trơn tru.

### 5.2. Hạn chế
- Chưa tích hợp tính năng chat realtime giữa sinh viên và giảng viên.
- Chưa có module quản lý học phí.
- Chức năng export/import dữ liệu từ file Excel còn hạn chế.

### 5.3. Hướng phát triển
Trong tương lai, hệ thống có thể được nâng cấp thêm:
- Tích hợp API để phát triển Mobile App (React Native/Flutter).
- Thêm module Thông báo (Notification) realtime.
- Tích hợp thanh toán học phí trực tuyến (VNPAY/Momo).
- Ứng dụng AI để phân tích kết quả học tập và gợi ý lộ trình học cho sinh viên.

---
**HẾT BÁO CÁO**

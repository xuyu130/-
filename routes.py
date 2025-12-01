# routes.py
import datetime
import copy
from flask import render_template, request, redirect, url_for, session, flash, g, jsonify
from functools import wraps

from models import Validator, BusinessException
from services import service_manager

def setup_routes(app, service_manager):
    """设置所有路由"""
    
    # 创建权限装饰器
    def login_required(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if 'user_id' not in session:
                flash('请先登录。', 'warning')
                return redirect(url_for('login'))
            return view(*args, **kwargs)
        return wrapped_view

    def admin_required(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if 'user_id' not in session or session.get('role') != 'admin':
                flash('您没有权限访问此页面。', 'danger')
                return redirect(url_for('index'))
            return view(*args, **kwargs)
        return wrapped_view

    def teacher_or_admin_required(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if 'user_id' not in session:
                flash('请先登录。', 'warning')
                return redirect(url_for('login'))
            if session.get('role') not in ['admin', 'teacher']:
                flash('您没有权限访问此页面。', 'danger')
                return redirect(url_for('index'))
            return view(*args, **kwargs)
        return wrapped_view

    def student_required(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if 'user_id' not in session:
                flash('请先登录。', 'warning')
                return redirect(url_for('login'))
            if session.get('role') != 'student':
                flash('您没有权限访问此页面。', 'danger')
                return redirect(url_for('index'))
            return view(*args, **kwargs)
        return wrapped_view

    # === 认证路由 ===
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            user = service_manager.user_service.authenticate_user(username, password)
            if user:
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                flash(f'欢迎回来, {user.username} ({user.role})!', 'success')
                return redirect(url_for('index'))
            else:
                flash('用户名或密码错误。', 'danger')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        session.clear()
        flash('您已成功退出。', 'info')
        return redirect(url_for('login'))

    # === 首页和仪表板 ===
    @app.route('/')
    @login_required
    def index():
        user_service = service_manager.user_service
        student_service = service_manager.student_service
        course_service = service_manager.course_service
        attendance_service = service_manager.attendance_service
        notice_service = service_manager.notice_service

        # 基本统计
        student_count = len(student_service.get_all_students())
        course_count = len(course_service.get_all_courses())
        
        # 今日考勤统计
        today_date = datetime.date.today().strftime('%Y-%m-%d')
        today_attendance = attendance_service.attendance_repo.get_by_date(today_date)
        present_count = sum(1 for a in today_attendance if a.status == 'present')
        absent_count = sum(1 for a in today_attendance if a.status == 'absent')
        leave_count = sum(1 for a in today_attendance if a.status == 'leave')

        # 获取最近通知
        recent_notices = notice_service.get_recent_notices(5)
        
        return render_template('index.html', 
                            student_count=student_count, 
                            course_count=course_count,
                            present_count=present_count,
                            absent_count=absent_count,
                            leave_count=leave_count,
                            recent_notices=[n.to_dict() for n in recent_notices])

    # === 学生管理路由 ===
    @app.route('/students')
    @teacher_or_admin_required
    def students():
        student_service = service_manager.student_service
        students = sorted(student_service.get_all_students(), key=lambda x: x.student_id)
        return render_template('students.html', students=[s.to_dict() for s in students])

    @app.route('/students/add', methods=['POST'])
    @teacher_or_admin_required
    def add_student():
        if request.method == 'POST':
            student_data = {
                'name': request.form['name'],
                'gender': request.form['gender'],
                'age': request.form['age'],
                'student_id': request.form['student_id'],
                'contact_phone': request.form.get('contact_phone', ''),
                'family_info': request.form.get('family_info', ''),
                'class_name': request.form.get('class_name', ''),
                'homeroom_teacher': request.form.get('homeroom_teacher', '')
            }
            
            success, student, message = service_manager.student_service.create_student(student_data)
            if success:
                g.data_modified = True
                flash(message, 'success')
            else:
                flash(message, 'danger')
        
        return redirect(url_for('students'))

    @app.route('/students/edit/<int:id>', methods=['POST'])
    @teacher_or_admin_required
    def edit_student(id):
        student_service = service_manager.student_service
        student = student_service.get_student_by_id(id)
        if not student:
            flash('学生未找到！', 'danger')
            return redirect(url_for('students'))

        if request.method == 'POST':
            student_data = {
                'name': request.form['name'],
                'gender': request.form['gender'],
                'age': request.form['age'],
                'student_id': request.form['student_id'],
                'contact_phone': request.form.get('contact_phone', ''),
                'family_info': request.form.get('family_info', ''),
                'class_name': request.form.get('class_name', ''),
                'homeroom_teacher': request.form.get('homeroom_teacher', '')
            }
            
            success, updated_student, message = student_service.update_student(id, student_data)
            if success:
                g.data_modified = True
                flash(message, 'success')
            else:
                flash(message, 'danger')
        
        return redirect(url_for('students'))

    @app.route('/students/delete/<int:id>', methods=['POST'])
    @teacher_or_admin_required
    def delete_student(id):
        student_service = service_manager.student_service
        
        student = student_service.get_student_by_id(id)
        if not student:
            flash('学生未找到！', 'danger')
            return redirect(url_for('students'))
        
        try:
            success, message = student_service.delete_student(id)
            if success:
                g.data_modified = True
                flash(message, 'success')
            else:
                flash(message, 'danger')
        except Exception as e:
            flash(f'删除学生时发生错误: {str(e)}', 'danger')
        
        return redirect(url_for('students'))

    # === 课程管理路由 ===
    @app.route('/courses')
    @login_required
    def courses():
        course_service = service_manager.course_service
        enrollment_service = service_manager.enrollment_service
        
        all_courses = sorted(course_service.get_all_courses(), key=lambda x: x.name)
        
        # 获取查询参数
        search = request.args.get('search', '')
        capacity_filter = request.args.get('capacity_filter', '')
        
        processed_courses = []
        current_student_info_id = None

        # 如果是学生用户，获取关联的学生信息ID
        if session.get('role') == 'student':
            current_user = service_manager.user_service.get_user_by_id(session['user_id'])
            if current_user:
                current_student_info_id = current_user.student_info_id

        for course in all_courses:
            # 搜索筛选
            if search and search.lower() not in course.name.lower() and \
            (not course.description or search.lower() not in course.description.lower()):
                continue
                
            course_data = course.to_dict()
            course_data['enrolled_count'] = course_service.get_enrolled_count(course.id)
            
            # 容量筛选
            if capacity_filter == 'available' and course.capacity:
                if course_data['enrolled_count'] >= course.capacity:
                    continue
            elif capacity_filter == 'full' and course.capacity:
                if course_data['enrolled_count'] < course.capacity:
                    continue
            
            # 检查当前学生是否已选修
            if current_student_info_id:
                course_data['is_enrolled_by_current_user'] = enrollment_service.is_student_enrolled(
                    current_student_info_id, course.id)
            else:
                course_data['is_enrolled_by_current_user'] = False

            processed_courses.append(course_data)

        return render_template('courses.html', courses=processed_courses)

    @app.route('/courses/add', methods=['GET', 'POST'])
    @teacher_or_admin_required
    def add_course():
        if request.method == 'POST':
            course_data = {
                'name': request.form['name'],
                'description': request.form['description'],
                'credits': request.form['credits'],
                'capacity': request.form.get('capacity', '')
            }
            
            success, course, message = service_manager.course_service.create_course(course_data)
            if success:
                g.data_modified = True
                flash(message, 'success')
                return redirect(url_for('courses'))
            else:
                flash(message, 'danger')
        
        return render_template('add_edit_course.html', course={})

    @app.route('/courses/edit/<int:id>', methods=['GET', 'POST'])
    @teacher_or_admin_required
    def edit_course(id):
        course_service = service_manager.course_service
        course = course_service.get_course_by_id(id)

        if not course:
            flash('课程未找到！', 'danger')
            return redirect(url_for('courses'))

        if request.method == 'POST':
            course_data = {
                'name': request.form['name'],
                'description': request.form['description'],
                'credits': request.form['credits'],
                'capacity': request.form.get('capacity', '')
            }
            
            success, updated_course, message = course_service.update_course(id, course_data)
            if success:
                g.data_modified = True
                flash(message, 'success')
                return redirect(url_for('courses'))
            else:
                flash(message, 'danger')
        
        return render_template('add_edit_course.html', course=course.to_dict())

    @app.route('/courses/delete/<int:id>', methods=['POST'])
    @teacher_or_admin_required
    def delete_course(id):
        success, message = service_manager.course_service.delete_course(id)
        if success:
            g.data_modified = True
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('courses'))

    @app.route('/course/<int:id>/enroll', methods=['POST'])
    @student_required
    def enroll_course(id):
        enrollment_service = service_manager.enrollment_service
        course_service = service_manager.course_service
        
        course = course_service.get_course_by_id(id)
        if not course:
            flash('课程未找到！', 'danger')
            return redirect(url_for('courses'))

        current_user = service_manager.user_service.get_user_by_id(session['user_id'])
        if not current_user or not current_user.student_info_id:
            flash('您的学生信息未关联，无法选课。', 'danger')
            return redirect(url_for('courses'))
        
        student_info_id = current_user.student_info_id

        success, enrollment, message = enrollment_service.enroll_student(student_info_id, id)
        if success:
            g.data_modified = True
            flash(message, 'success')
        else:
            flash(message, 'danger')
        
        return redirect(url_for('courses'))

    @app.route('/course/<int:id>/unenroll', methods=['POST'])
    @student_required
    def unenroll_course(id):
        enrollment_service = service_manager.enrollment_service
        course_service = service_manager.course_service
        
        course = course_service.get_course_by_id(id)
        if not course:
            flash('课程未找到！', 'danger')
            return redirect(url_for('courses'))

        current_user = service_manager.user_service.get_user_by_id(session['user_id'])
        if not current_user or not current_user.student_info_id:
            flash('您的学生信息未关联，无法退课。', 'danger')
            return redirect(url_for('courses'))
        
        student_info_id = current_user.student_info_id

        success, message = enrollment_service.unenroll_student(student_info_id, id)
        if success:
            g.data_modified = True
            flash(message, 'success')
        else:
            flash(message, 'info')  # 使用info而不是danger，因为可能是未选修的情况
        
        return redirect(url_for('courses'))

    # === 选课管理路由 ===
    @app.route('/students/<int:student_id>/enrollments')
    @teacher_or_admin_required
    def enrollments(student_id):
        student_service = service_manager.student_service
        enrollment_service = service_manager.enrollment_service
        course_service = service_manager.course_service
        
        student = student_service.get_student_by_id(student_id)
        if not student:
            flash('学生未找到！', 'danger')
            return redirect(url_for('students'))

        # 获取该学生的所有选课记录
        enrollments_list = []
        for enrollment in enrollment_service.get_student_enrollments(student_id):
            course = course_service.get_course_by_id(enrollment.course_id)
            if course:
                enrollment_data = enrollment.to_dict()
                enrollment_data['course_name'] = course.name
                enrollments_list.append(enrollment_data)
        
        # 获取可选的课程（排除已选的课程）
        available_courses = []
        student_courses = enrollment_service.enrollment_repo.get_courses_for_student(student_id)
        for course in course_service.get_all_courses():
            if course.id not in student_courses:
                available_courses.append(course.to_dict())
        
        return render_template('enrollments.html', 
                            student=student.to_dict(), 
                            enrollments=enrollments_list,
                            available_courses=available_courses)

    @app.route('/students/<int:student_id>/enrollments/add', methods=['POST'])
    @teacher_or_admin_required
    def add_enrollment(student_id):
        enrollment_service = service_manager.enrollment_service
        
        if request.method == 'POST':
            course_id = int(request.form['course_id'])
            exam_score = request.form.get('exam_score')
            performance_score = request.form.get('performance_score')

            # 先创建选课记录
            success, enrollment, message = enrollment_service.enroll_student(student_id, course_id)
            if success:
                # 如果有成绩，更新成绩
                if exam_score or performance_score:
                    exam_score_float = float(exam_score) if exam_score else None
                    performance_score_float = float(performance_score) if performance_score else None
                    
                    success, updated_enrollment, message = enrollment_service.update_scores(
                        enrollment.id, exam_score_float, performance_score_float
                    )
                
                g.data_modified = True
                flash('课程/成绩添加成功！', 'success')
            else:
                flash(message, 'danger')
        
        return redirect(url_for('enrollments', student_id=student_id))

    @app.route('/enrollments/edit/<int:enrollment_id>', methods=['POST'])
    @teacher_or_admin_required
    def edit_enrollment(enrollment_id):
        enrollment_service = service_manager.enrollment_service
        
        enrollment = enrollment_service.enrollment_repo.get_by_id(enrollment_id)
        if not enrollment:
            flash('选课记录未找到！', 'danger')
            return redirect(url_for('students'))
        
        student_id = enrollment.student_id
        
        if request.method == 'POST':
            exam_score = request.form.get('exam_score')
            performance_score = request.form.get('performance_score')
            
            exam_score_float = float(exam_score) if exam_score else None
            performance_score_float = float(performance_score) if performance_score else None
            
            success, updated_enrollment, message = enrollment_service.update_scores(
                enrollment_id, exam_score_float, performance_score_float
            )
            
            if success:
                g.data_modified = True
                flash(message, 'success')
            else:
                flash(message, 'danger')
        
        return redirect(url_for('enrollments', student_id=student_id))

    @app.route('/enrollments/delete/<int:enrollment_id>', methods=['POST'])
    @teacher_or_admin_required
    def delete_enrollment(enrollment_id):
        enrollment_service = service_manager.enrollment_service
        
        enrollment = enrollment_service.enrollment_repo.get_by_id(enrollment_id)
        if not enrollment:
            flash('选课记录未找到！', 'danger')
            return redirect(url_for('students'))

        student_id = enrollment.student_id
        
        try:
            success = enrollment_service.enrollment_repo.delete(enrollment_id)
            if success:
                g.data_modified = True
                flash('选课记录删除成功！', 'success')
            else:
                flash('删除选课记录失败！', 'danger')
        except Exception as e:
            flash(f'删除选课记录时发生错误: {str(e)}', 'danger')
        
        return redirect(url_for('enrollments', student_id=student_id))

    # === 考勤管理路由 ===
    @app.route('/attendance')
    @teacher_or_admin_required
    def attendance():
        attendance_service = service_manager.attendance_service
        student_service = service_manager.student_service
        
        attendance_records = []
        for attendance in attendance_service.attendance_repo.get_all():
            student = student_service.get_student_by_id(attendance.student_id)
            if student:
                record_data = attendance.to_dict()
                record_data['student_name'] = student.name
                record_data['student_id_str'] = student.student_id
                attendance_records.append(record_data)
        
        attendance_records = sorted(attendance_records, key=lambda x: (x['date'], x['student_name']), reverse=True)
        
        # 获取学生列表用于添加模态框
        students = sorted(student_service.get_all_students(), key=lambda x: x.name)
        
        return render_template('attendance.html', 
                            attendance_records=attendance_records, 
                            students=[s.to_dict() for s in students])

    @app.route('/attendance/add', methods=['POST'])
    @teacher_or_admin_required
    def add_attendance():
        attendance_service = service_manager.attendance_service
        
        if request.method == 'POST':
            student_id = int(request.form['student_id'])
            date = request.form['date']
            status = request.form['status']
            reason = request.form.get('reason', '')

            success, attendance, message = attendance_service.record_attendance(
                student_id, date, status, reason
            )
            
            if success:
                g.data_modified = True
                flash(message, 'success')
                return redirect(url_for('attendance'))
            else:
                flash(message, 'danger')
        
        students = sorted(service_manager.student_service.get_all_students(), key=lambda x: x.name)
        return render_template('add_edit_attendance.html', 
                            students=[s.to_dict() for s in students], 
                            attendance_record={})

    @app.route('/attendance/edit/<int:id>', methods=['POST'])
    @teacher_or_admin_required
    def edit_attendance(id):
        attendance_service = service_manager.attendance_service
        
        record = attendance_service.attendance_repo.get_by_id(id)
        if not record:
            flash('考勤记录未找到！', 'danger')
            return redirect(url_for('attendance'))
        
        status = request.form.get('status')
        reason = request.form.get('reason', '')
        referrer = request.form.get('referrer', '')
        
        success, updated_record, message = attendance_service.update_attendance(
            id, status, reason
        )
        
        if success:
            g.data_modified = True
            flash(message, 'success')
        else:
            flash(message, 'danger')
        
        # 根据referrer重定向
        if referrer:
            return redirect(referrer)
        else:
            return redirect(url_for('attendance'))

    @app.route('/attendance/delete/<int:id>', methods=['POST'])
    @teacher_or_admin_required
    def delete_attendance(id):
        attendance_service = service_manager.attendance_service
        
        record = attendance_service.attendance_repo.get_by_id(id)
        if not record:
            flash('考勤记录未找到！', 'danger')
            return redirect(url_for('attendance'))
        
        try:
            success = attendance_service.attendance_repo.delete(id)
            if success:
                g.data_modified = True
                flash('考勤记录删除成功！', 'success')
            else:
                flash('删除考勤记录失败！', 'danger')
        except Exception as e:
            flash(f'删除考勤记录时发生错误: {str(e)}', 'danger')
        
        return redirect(url_for('attendance'))

    @app.route('/student/checkin', methods=['POST'])
    @student_required
    def student_checkin():
        attendance_service = service_manager.attendance_service
        user_service = service_manager.user_service
        
        current_user_id = session['user_id']
        current_user = user_service.get_user_by_id(current_user_id)

        if not current_user or current_user.student_info_id is None:
            flash('您的学生信息未关联，无法进行签到。请联系管理员。', 'danger')
            return redirect(url_for('index'))

        student_info_id = current_user.student_info_id

        success, attendance, message = attendance_service.check_in_student(student_info_id)
        if success:
            g.data_modified = True
            flash(message, 'success')
        else:
            flash(message, 'info')  # 使用info而不是danger，因为可能是重复签到
        
        return redirect(url_for('index'))

    # === 奖励处分管理路由 ===
    @app.route('/rewards_punishments')
    @teacher_or_admin_required
    def rewards_punishments():
        rp_service = service_manager.reward_punishment_service
        student_service = service_manager.student_service
        
        records = []
        for rp in rp_service.reward_punishment_repo.get_all():
            student = student_service.get_student_by_id(rp.student_id)
            if student:
                record_data = rp.to_dict()
                record_data['student_name'] = student.name
                record_data['student_id'] = student.student_id
                records.append(record_data)
        
        records = sorted(records, key=lambda x: (x['date'], x['student_name']), reverse=True)
        
        # 获取学生列表用于下拉选择
        students = sorted(student_service.get_all_students(), key=lambda x: x.name)
        
        # 获取今天的日期用于默认值
        today = datetime.date.today().strftime('%Y-%m-%d')
        
        return render_template('rewards_punishments.html', 
                            records=records, 
                            students=[s.to_dict() for s in students],
                            today=today)

    @app.route('/rewards_punishments/add', methods=['POST'])
    @teacher_or_admin_required
    def add_reward_punishment():
        if request.method == 'POST':
            student_id = int(request.form['student_id'])
            rp_type = request.form['type']
            description = request.form['description']
            date = request.form['date']

            success, record, message = service_manager.reward_punishment_service.create_record(
                student_id, rp_type, description, date
            )
            
            if success:
                g.data_modified = True
                flash(message, 'success')
            else:
                flash(message, 'danger')
        
        return redirect(url_for('rewards_punishments'))

    @app.route('/rewards_punishments/edit/<int:id>', methods=['POST'])
    @teacher_or_admin_required
    def edit_reward_punishment(id):
        rp_service = service_manager.reward_punishment_service
        
        record = rp_service.reward_punishment_repo.get_by_id(id)
        if not record:
            flash('奖励/处分记录未找到！', 'danger')
            return redirect(url_for('rewards_punishments'))

        if request.method == 'POST':
            rp_type = request.form['type']
            description = request.form['description']
            date = request.form['date']

            success, updated_record, message = rp_service.update_record(
                id, rp_type, description, date
            )
            
            if success:
                g.data_modified = True
                flash(message, 'success')
            else:
                flash(message, 'danger')
        
        return redirect(url_for('rewards_punishments'))

    @app.route('/rewards_punishments/delete/<int:id>', methods=['POST'])
    @teacher_or_admin_required
    def delete_reward_punishment(id):
        rp_service = service_manager.reward_punishment_service
        
        record = rp_service.reward_punishment_repo.get_by_id(id)
        if not record:
            flash('奖励/处分记录未找到！', 'danger')
            return redirect(url_for('rewards_punishments'))
        
        try:
            success = rp_service.reward_punishment_repo.delete(id)
            if success:
                g.data_modified = True
                flash('奖励/处分记录删除成功！', 'success')
            else:
                flash('删除记录失败！', 'danger')
        except Exception as e:
            flash(f'删除记录时发生错误: {str(e)}', 'danger')
        
        return redirect(url_for('rewards_punishments'))

    # === 家长信息管理路由 ===
    @app.route('/parents')
    @teacher_or_admin_required
    def parents():
        parent_service = service_manager.parent_service
        student_service = service_manager.student_service
        
        parents_list = []
        for parent in parent_service.parent_repo.get_all():
            student = student_service.get_student_by_id(parent.student_id)
            if student:
                parent_data = parent.to_dict()
                parent_data['student_name'] = student.name
                parent_data['student_id_str'] = student.student_id
                parents_list.append(parent_data)
        
        parents_list = sorted(parents_list, key=lambda x: (x['student_name'], x['relationship']))
        
        # 获取学生列表用于模态框中的下拉选择
        students = sorted(student_service.get_all_students(), key=lambda x: x.name)
        
        return render_template('parents.html', 
                            parents=parents_list, 
                            students=[s.to_dict() for s in students])

    @app.route('/parents/add', methods=['POST'])
    @teacher_or_admin_required
    def add_parent():
        if request.method == 'POST':
            student_id = int(request.form['student_id'])
            parent_name = request.form['parent_name']
            relationship = request.form['relationship']
            contact_phone = request.form['contact_phone']
            email = request.form.get('email', '')
            address = request.form.get('address', '')

            success, parent, message = service_manager.parent_service.create_parent(
                student_id, parent_name, relationship, contact_phone, email, address
            )
            
            if success:
                g.data_modified = True
                flash(message, 'success')
            else:
                flash(message, 'danger')
        
        return redirect(url_for('parents'))

    @app.route('/parents/edit/<int:id>', methods=['POST'])
    @teacher_or_admin_required
    def edit_parent(id):
        parent_service = service_manager.parent_service
        
        parent = parent_service.parent_repo.get_by_id(id)
        if not parent:
            flash('家长信息未找到！', 'danger')
            return redirect(url_for('parents'))
        
        if request.method == 'POST':
            student_id = int(request.form['student_id'])
            parent_name = request.form['parent_name']
            relationship = request.form['relationship']
            contact_phone = request.form['contact_phone']
            email = request.form.get('email', '')
            address = request.form.get('address', '')

            success, updated_parent, message = parent_service.update_parent(
                id, parent_name, relationship, contact_phone, email, address
            )
            
            if success:
                g.data_modified = True
                flash(message, 'success')
            else:
                flash(message, 'danger')
        
        return redirect(url_for('parents'))

    # routes.py (补全家长信息删除路由)

    @app.route('/parents/delete/<int:id>', methods=['POST'])
    @teacher_or_admin_required
    def delete_parent(id):
        parent_service = service_manager.parent_service
        
        parent = parent_service.parent_repo.get_by_id(id)
        if not parent:
            flash('家长信息未找到！', 'danger')
            return redirect(url_for('parents'))
        
        try:
            success = parent_service.parent_repo.delete(id)
            if success:
                g.data_modified = True
                flash('家长信息删除成功！', 'success')
            else:
                flash('删除家长信息失败！', 'danger')
        except Exception as e:
            flash(f'删除家长信息时发生错误: {str(e)}', 'danger')
        
        return redirect(url_for('parents'))


    # === 通知管理路由 ===
    @app.route('/notices')
    @login_required
    def notices():
        notice_service = service_manager.notice_service
        user_role = session.get('role')
        
        # 根据用户角色获取可见通知
        notices_list = notice_service.get_notices_for_user(user_role)
        
        # 搜索和筛选功能
        search = request.args.get('search', '')
        target_filter = request.args.get('target', '')
        
        # 搜索功能
        if search:
            notices_list = [n for n in notices_list if search.lower() in n.title.lower() or search.lower() in n.content.lower()]
        
        # 目标筛选（仅对教师和管理员有效）
        if target_filter and user_role in ['admin', 'teacher']:
            notices_list = [n for n in notices_list if n.target == target_filter]
        
        notices_list = sorted(notices_list, key=lambda x: x.date, reverse=True)
        return render_template('notices.html', 
                            notices=[n.to_dict() for n in notices_list], 
                            user_role=user_role)

    @app.route('/notices/add', methods=['POST'])
    @teacher_or_admin_required
    def add_notice():
        if request.method == 'POST':
            title = request.form['title'].strip()
            content = request.form['content'].strip()
            target = request.form.get('target', '').strip()
            sender = request.form.get('sender', '').strip() or session.get('username', '系统')
            
            success, notice, message = service_manager.notice_service.create_notice(
                title, content, target, sender
            )
            
            if success:
                g.data_modified = True
                flash(message, 'success')
            else:
                flash(message, 'danger')
        
        return redirect(url_for('notices'))

    @app.route('/notices/edit/<int:id>', methods=['POST'])
    @teacher_or_admin_required
    def edit_notice(id):
        notice_service = service_manager.notice_service
        
        notice = notice_service.notice_repo.get_by_id(id)
        if not notice:
            flash('通知未找到！', 'danger')
            return redirect(url_for('notices'))
        
        if request.method == 'POST':
            title = request.form['title'].strip()
            content = request.form['content'].strip()
            target = request.form.get('target', '').strip()
            sender = request.form.get('sender', '').strip() or session.get('username', '系统')
            
            success, updated_notice, message = notice_service.update_notice(
                id, title, content, target, sender
            )
            
            if success:
                g.data_modified = True
                flash(message, 'success')
            else:
                flash(message, 'danger')
        
        return redirect(url_for('notices'))

    @app.route('/notices/delete/<int:id>', methods=['POST'])
    @teacher_or_admin_required
    def delete_notice(id):
        notice_service = service_manager.notice_service
        
        notice = notice_service.notice_repo.get_by_id(id)
        if not notice:
            flash('通知未找到！', 'danger')
            return redirect(url_for('notices'))
        
        try:
            success = notice_service.notice_repo.delete(id)
            if success:
                g.data_modified = True
                flash('通知删除成功！', 'success')
            else:
                flash('删除通知失败！', 'danger')
        except Exception as e:
            flash(f'删除通知时发生错误: {str(e)}', 'danger')
        
        return redirect(url_for('notices'))

    # === 用户管理路由 ===
    @app.route('/users')
    @admin_required
    def users():
        """用户管理页面"""
        user_service = service_manager.user_service
        student_service = service_manager.student_service
        
        # 获取所有用户
        users_list = sorted(user_service.get_all_users(), key=lambda x: x.username)
        
        # 获取所有学生用于下拉选择
        students_list = sorted(student_service.get_all_students(), key=lambda x: x.name)
        
        # 创建学生ID到学生信息的映射字典
        students_dict = {}
        for student in students_list:
            students_dict[student.id] = student.to_dict()
        
        print(f"📊 路由调试: 用户数量={len(users_list)}, 学生数量={len(students_list)}")
        
        return render_template('users.html', 
                            users=[u.to_dict() for u in users_list], 
                            students=[s.to_dict() for s in students_list],
                            students_dict=students_dict)

    @app.route('/users/add', methods=['POST'])
    @admin_required
    def add_user():
        """添加用户"""
        if request.method == 'POST':
            print("🎯 开始添加用户操作...")
            
            # 收集表单数据
            user_data = {
                'username': request.form['username'].strip(),
                'password': request.form['password'],
                'role': request.form['role'],
                'student_info_id': request.form.get('student_info_id')
            }
            
            print(f"📝 接收到的表单数据: {user_data}")
            
            # 验证学生信息
            if user_data['role'] == 'student':
                if not user_data.get('student_info_id'):
                    flash('学生用户必须关联一个学生信息', 'danger')
                    return redirect(url_for('users'))
                
                # 验证学生是否存在
                try:
                    student_id = int(user_data['student_info_id'])
                    student = service_manager.student_service.get_student_by_id(student_id)
                    if not student:
                        flash(f'关联的学生信息不存在 (ID: {student_id})', 'danger')
                        return redirect(url_for('users'))
                    print(f"✅ 学生验证通过: {student.name} (ID: {student.id})")
                except (ValueError, TypeError) as e:
                    flash('学生ID格式错误', 'danger')
                    return redirect(url_for('users'))
            
            # 调用服务创建用户
            success, user, message = service_manager.user_service.create_user(user_data)
            
            if success:
                print(f"✅ 用户创建成功: {user.username} (ID: {user.id})")
                flash(message, 'success')
            else:
                print(f"❌ 用户创建失败: {message}")
                flash(message, 'danger')
        
        return redirect(url_for('users'))

    @app.route('/users/edit/<int:id>', methods=['POST'])
    @admin_required
    def edit_user(id):
        """编辑用户"""
        if request.method == 'POST':
            print(f"🎯 开始编辑用户操作 (ID: {id})...")
            
            user_data = {
                'username': request.form['username'].strip(),
                'password': request.form.get('password', ''),  # 密码可选
                'role': request.form['role'],
                'student_info_id': request.form.get('student_info_id')
            }
            
            print(f"📝 接收到的编辑数据: {user_data}")
            
            # 验证学生信息
            if user_data['role'] == 'student':
                if not user_data.get('student_info_id'):
                    flash('学生用户必须关联一个学生信息', 'danger')
                    return redirect(url_for('users'))
                
                try:
                    student_id = int(user_data['student_info_id'])
                    student = service_manager.student_service.get_student_by_id(student_id)
                    if not student:
                        flash(f'关联的学生信息不存在 (ID: {student_id})', 'danger')
                        return redirect(url_for('users'))
                    print(f"✅ 学生验证通过: {student.name} (ID: {student.id})")
                except (ValueError, TypeError) as e:
                    flash('学生ID格式错误', 'danger')
                    return redirect(url_for('users'))
            
            # 调用服务更新用户
            success, user, message = service_manager.user_service.update_user(id, user_data)
            
            if success:
                print(f"✅ 用户更新成功: {user.username} (ID: {user.id})")
                flash(message, 'success')
            else:
                print(f"❌ 用户更新失败: {message}")
                flash(message, 'danger')
        
        return redirect(url_for('users'))

    @app.route('/users/delete/<int:id>', methods=['POST'])
    @admin_required
    def delete_user(id):
        """删除用户"""
        current_user_id = session.get('user_id')
        
        if id == current_user_id:
            flash('不能删除当前登录的用户', 'danger')
            return redirect(url_for('users'))
        
        success, message = service_manager.user_service.delete_user(id, current_user_id)
        
        if success:
            print(f"✅ 用户删除成功 (ID: {id})")
            flash(message, 'success')
        else:
            print(f"❌ 用户删除失败: {message}")
            flash(message, 'danger')
        
        return redirect(url_for('users'))

    # === 成绩查询路由 ===
    @app.route('/grades')
    @student_required
    def view_grades():
        if session['role'] != 'student':
            flash('您没有权限访问此页面。', 'danger')
            return redirect(url_for('index'))
        
        user_service = service_manager.user_service
        enrollment_service = service_manager.enrollment_service
        course_service = service_manager.course_service
        
        current_user_id = session['user_id']
        current_user = user_service.get_user_by_id(current_user_id)

        # 确保用户存在且有 student_info_id 关联
        if not current_user or current_user.student_info_id is None:
            flash('未找到您的学生信息，请联系管理员。', 'danger')
            return redirect(url_for('index'))

        student_id = current_user.student_info_id
        student_info = service_manager.student_service.get_student_by_id(student_id)

        if not student_info:
            flash('未找到您的学生信息，请联系管理员。', 'danger')
            return redirect(url_for('index'))

        grades_list = []
        for enrollment in enrollment_service.get_student_enrollments(student_id):
            if enrollment.exam_score is not None:
                course = course_service.get_course_by_id(enrollment.course_id)
                if course:
                    grade_data = {
                        'course_name': course.name,
                        'credits': course.credits,
                        'exam_score': enrollment.exam_score,
                        'performance_score': enrollment.performance_score
                    }
                    grades_list.append(grade_data)
        
        return render_template('grades.html', 
                            grades=grades_list, 
                            student_name=student_info.name)

    # === 排课管理路由 ===
    @app.route('/schedules')
    @teacher_or_admin_required
    def schedules():
        schedule_service = service_manager.schedule_service
        course_service = service_manager.course_service
        user_service = service_manager.user_service
        
        schedules_list = []
        for schedule in schedule_service.schedule_repo.get_all():
            schedule_data = schedule.to_dict()
            course = course_service.get_course_by_id(schedule.course_id)
            teacher = user_service.get_user_by_id(schedule.teacher_user_id)
            
            schedule_data['course_name'] = course.name if course else '未知课程'
            schedule_data['teacher_name'] = teacher.username if teacher else '未知教师'
            schedules_list.append(schedule_data)
        
        # 按星期、开始时间排序
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        schedules_list.sort(key=lambda x: (day_order.index(x['day_of_week']), x['start_time']))

        # 获取课程和教师列表用于模态框
        courses = sorted(course_service.get_all_courses(), key=lambda x: x.name)
        teachers = sorted([u for u in user_service.get_all_users() if u.role == 'teacher'], 
                         key=lambda x: x.username)

        return render_template('schedules.html', 
                            schedules=schedules_list,
                            courses=[c.to_dict() for c in courses],
                            teachers=[t.to_dict() for t in teachers])

    @app.route('/schedules/add', methods=['POST'])
    @teacher_or_admin_required
    def add_schedule():
        if request.method == 'POST':
            course_id = int(request.form['course_id'])
            teacher_user_id = int(request.form['teacher_user_id'])
            day_of_week = request.form['day_of_week']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            location = request.form['location']
            semester = request.form.get('semester', '未知学期')

            success, schedule, message = service_manager.schedule_service.create_schedule(
                course_id, teacher_user_id, day_of_week, start_time, end_time, location, semester
            )
            
            if success:
                g.data_modified = True
                flash(message, 'success')
            else:
                flash(message, 'danger')
        
        return redirect(url_for('schedules'))

    @app.route('/schedules/edit/<int:id>', methods=['POST'])
    @teacher_or_admin_required
    def edit_schedule(id):
        schedule_service = service_manager.schedule_service
        
        schedule = schedule_service.schedule_repo.get_by_id(id)
        if not schedule:
            flash('排课记录未找到！', 'danger')
            return redirect(url_for('schedules'))

        if request.method == 'POST':
            course_id = int(request.form['course_id'])
            teacher_user_id = int(request.form['teacher_user_id'])
            day_of_week = request.form['day_of_week']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            location = request.form['location']
            semester = request.form.get('semester', '未知学期')

            success, updated_schedule, message = schedule_service.update_schedule(
                id, course_id, teacher_user_id, day_of_week, start_time, end_time, location, semester
            )
            
            if success:
                g.data_modified = True
                flash(message, 'success')
            else:
                flash(message, 'danger')
        
        return redirect(url_for('schedules'))

    @app.route('/schedules/delete/<int:id>', methods=['POST'])
    @teacher_or_admin_required
    def delete_schedule(id):
        schedule_service = service_manager.schedule_service
        
        schedule = schedule_service.schedule_repo.get_by_id(id)
        if not schedule:
            flash('排课未找到！', 'danger')
            return redirect(url_for('schedules'))
        
        try:
            success = schedule_service.schedule_repo.delete(id)
            if success:
                g.data_modified = True
                flash('排课删除成功！', 'success')
            else:
                flash('删除排课失败！', 'danger')
        except Exception as e:
            flash(f'删除排课时发生错误: {str(e)}', 'danger')
        
        return redirect(url_for('schedules'))

    # === 统计分析路由 ===
    @app.route('/statistics')
    @login_required
    def statistics():
        statistics_service = service_manager.statistics_service
        
        stats_data = statistics_service.get_general_statistics()
        
        return render_template('statistics.html', 
                            total_students=stats_data['total_students'],
                            students_by_gender=stats_data['students_by_gender'],
                            total_courses=stats_data['total_courses'],
                            attendance_summary=stats_data['attendance_summary'],
                            avg_scores=stats_data['avg_scores'],
                            rp_summary=stats_data['rp_summary'])

    @app.route('/stu_statistics')
    @student_required
    def stu_statistics():
        """学生个人统计分析页面"""
        if session['role'] != 'student':
            flash('您没有权限访问此页面。', 'danger')
            return redirect(url_for('index'))
        
        user_service = service_manager.user_service
        statistics_service = service_manager.statistics_service
        
        current_user_id = session['user_id']
        current_user = user_service.get_user_by_id(current_user_id)
        
        if not current_user or current_user.student_info_id is None:
            flash('未找到您的学生信息，请联系管理员。', 'danger')
            return redirect(url_for('index'))
        
        student_id = current_user.student_info_id
        student_info = service_manager.student_service.get_student_by_id(student_id)
        
        if not student_info:
            flash('未找到您的学生信息，请联系管理员。', 'danger')
            return redirect(url_for('index'))
        
        # 获取学生统计信息
        stats_data = statistics_service.get_student_statistics(student_id)
        
        # 获取班级平均成绩（用于对比分析）
        class_avg_scores = {}
        for course in service_manager.course_service.get_all_courses():
            course_enrollments = service_manager.enrollment_service.get_course_enrollments(course.id)
            if course_enrollments:
                exam_scores = [e.exam_score for e in course_enrollments if e.exam_score is not None]
                if exam_scores:
                    avg_exam = sum(exam_scores) / len(exam_scores)
                    perf_scores = [e.performance_score for e in course_enrollments if e.performance_score is not None]
                    avg_perf = sum(perf_scores) / len(perf_scores) if perf_scores else None
                    avg_total = round((avg_exam + (avg_perf or avg_exam)) / 2, 2)
                    class_avg_scores[course.name] = {
                        'avg_exam': round(avg_exam, 2),
                        'avg_perf': round(avg_perf, 2) if avg_perf else None,
                        'avg_total': avg_total
                    }
        
        # 获取上课时间分布数据
        student_courses = service_manager.enrollment_service.get_courses_for_student(student_id)
        schedule_distribution = {}
        for schedule in service_manager.schedule_service.schedule_repo.get_all():
            if schedule.course_id in student_courses:
                day = schedule.day_of_week
                if day not in schedule_distribution:
                    schedule_distribution[day] = []
                course = service_manager.course_service.get_course_by_id(schedule.course_id)
                schedule_distribution[day].append({
                    'start_time': schedule.start_time,
                    'end_time': schedule.end_time,
                    'course_name': course.name if course else '未知课程',
                    'location': schedule.location
                })
        
        # 生成学习计划建议
        study_recommendations = _generate_study_recommendations(
            stats_data.get('grades_data', []),
            stats_data.get('attendance_records', []),
            stats_data.get('rewards', []),
            stats_data.get('punishments', [])
        )
        
        # 为图表准备数据
        chart_data = {
            'course_names': [grade['course_name'] for grade in stats_data.get('grades_data', [])],
            'my_scores': [grade['total_score'] for grade in stats_data.get('grades_data', [])],
            'class_avg_scores': []
        }
        
        # 为每个课程获取班级平均分
        for grade in stats_data.get('grades_data', []):
            course_name = grade['course_name']
            if course_name in class_avg_scores:
                chart_data['class_avg_scores'].append(class_avg_scores[course_name]['avg_total'])
            else:
                chart_data['class_avg_scores'].append(None)
        
        return render_template('stu_statistics.html',
                            student=student_info.to_dict(),
                            grades_data=stats_data.get('grades_data', []),
                            class_avg_scores=class_avg_scores,
                            attendance_rate=stats_data.get('attendance_rate', 0),
                            present_count=stats_data.get('present_count', 0),
                            absent_count=stats_data.get('absent_count', 0),
                            leave_count=stats_data.get('leave_count', 0),
                            rewards=stats_data.get('rewards', []),
                            punishments=stats_data.get('punishments', []),
                            schedule_distribution=schedule_distribution,
                            study_recommendations=study_recommendations,
                            chart_data=chart_data)

    def _generate_study_recommendations(grades_data, attendance_records, rewards, punishments):
        """生成学习计划建议"""
        recommendations = []
        
        # 基于成绩的建议
        if grades_data:
            low_score_courses = [course for course in grades_data if course['total_score'] < 60]
            if low_score_courses:
                course_names = ", ".join([course['course_name'] for course in low_score_courses[:3]])
                recommendations.append(f"📚 <strong>{course_names}</strong> 课程成绩较低，建议加强复习和练习")
            
            high_score_courses = [course for course in grades_data if course['total_score'] >= 90]
            if high_score_courses:
                course_names = ", ".join([course['course_name'] for course in high_score_courses[:2]])
                recommendations.append(f"🎯 <strong>{course_names}</strong> 课程表现优秀，可以尝试挑战更高难度的内容")
        
        # 基于出勤的建议
        recent_attendance = sorted(attendance_records, key=lambda x: x.date, reverse=True)[:10]
        recent_absences = [a for a in recent_attendance if a.status == 'absent']
        
        if len(recent_absences) >= 3:
            recommendations.append("⚠️ 近期缺勤较多，请注意调整作息，保证上课出勤率")
        
        # 基于奖励处分的建议
        if punishments:
            recommendations.append("❗ 有处分记录，请注意遵守校规校纪，表现良好可申请撤销处分")
        
        if rewards:
            recommendations.append("🏆 继续保持优秀表现，争取获得更多奖励")
        
        # 通用建议
        if not recommendations:
            recommendations.append("📊 学习状态良好，继续保持当前的学习节奏和习惯")
        
        recommendations.append("⏰ 建议制定每周学习计划，合理安排各科目学习时间")
        recommendations.append("📖 定期复习已学内容，做好课前预习和课后总结")
        
        return recommendations

    # === 学生课程页面 ===
    @app.route('/student/courses')
    @student_required
    def student_courses():
        user_service = service_manager.user_service
        course_service = service_manager.course_service
        enrollment_service = service_manager.enrollment_service
        
        # 获取当前登录的学生用户信息
        current_user = user_service.get_user_by_id(session['user_id'])
        if not current_user or not current_user.student_info_id:
            flash('您的学生信息未关联，无法查看课程。', 'danger')
            return redirect(url_for('index'))
        
        student_info_id = current_user.student_info_id
        
        # 获取所有课程并添加选课状态
        all_courses = sorted(course_service.get_all_courses(), key=lambda x: x.name)
        processed_courses = []
        
        for course in all_courses:
            course_data = course.to_dict()
            course_data['enrolled_count'] = course_service.get_enrolled_count(course.id)
            course_data['is_enrolled_by_current_user'] = enrollment_service.is_student_enrolled(
                student_info_id, course.id)
            
            processed_courses.append(course_data)
        
        return render_template('student_courses.html', courses=processed_courses)

    # === 课程学生列表 ===
    @app.route('/course/<int:id>/students')
    @teacher_or_admin_required
    def view_course_students(id):
        course_service = service_manager.course_service
        enrollment_service = service_manager.enrollment_service
        student_service = service_manager.student_service
        
        course = course_service.get_course_by_id(id)
        if not course:
            flash('课程未找到！', 'danger')
            return redirect(url_for('courses'))
        
        enrolled_students = []
        enrollments_list = []
        for enrollment in enrollment_service.get_course_enrollments(id):
            student = student_service.get_student_by_id(enrollment.student_id)
            if student:
                student_data = student.to_dict()
                student_data['exam_score'] = enrollment.exam_score
                student_data['performance_score'] = enrollment.performance_score
                enrolled_students.append(student_data)
                
                enrollment_data = enrollment.to_dict()
                enrollments_list.append(enrollment_data)
        
        enrolled_students = sorted(enrolled_students, key=lambda x: x['name'])
        return render_template('course_students.html', 
                            course=course.to_dict(), 
                            students=enrolled_students, 
                            enrollments=enrollments_list)

    # === API 路由（可选）===
    @app.route('/api/students')
    @login_required
    def api_students():
        """学生数据API"""
        students = service_manager.student_service.get_all_students()
        return jsonify([s.to_dict() for s in students])

    @app.route('/api/courses')
    @login_required
    def api_courses():
        """课程数据API"""
        courses = service_manager.course_service.get_all_courses()
        return jsonify([c.to_dict() for c in courses])

    @app.route('/api/attendance/today')
    @teacher_or_admin_required
    def api_today_attendance():
        """今日考勤API"""
        today_date = datetime.date.today().strftime('%Y-%m-%d')
        attendance_records = service_manager.attendance_service.attendance_repo.get_by_date(today_date)
        
        result = []
        for record in attendance_records:
            student = service_manager.student_service.get_student_by_id(record.student_id)
            if student:
                result.append({
                    'student_name': student.name,
                    'student_id': student.student_id,
                    'status': record.status,
                    'reason': record.reason
                })
        
        return jsonify(result)

    # === 错误处理路由 ===
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', error_message='页面未找到'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error.html', error_message='服务器内部错误'), 500

    # === 工具函数 ===
    def get_current_student_info():
        """获取当前登录学生的信息"""
        if session.get('role') != 'student':
            return None
        
        user_service = service_manager.user_service
        current_user = user_service.get_user_by_id(session['user_id'])
        if not current_user or not current_user.student_info_id:
            return None
        
        return service_manager.student_service.get_student_by_id(current_user.student_info_id)

    print("所有路由设置完成！")

# 便捷函数
def get_service(service_name):
    """获取服务实例的便捷函数"""
    return getattr(service_manager, service_name, None)

# 测试路由设置
if __name__ == '__main__':
    # 简单的测试
    from flask import Flask
    app = Flask(__name__)
    setup_routes(app, service_manager)
    print("路由设置测试完成！")
import datetime
import functools
import copy
import json # 导入json模块
import os   # 导入os模块用于检查文件是否存在

from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here' # 生产环境请务必更换为复杂随机的密钥

# --- JSON 文件存储配置 ---
DATA_FILE = 'app_data.json' # 定义存储数据的文件名

# 全局字典来存储所有数据，模拟数据库表
in_memory_data = {
    'users': [],
    'students': [],
    'courses': [],
    'enrollments': [],
    'attendance': [],
    'rewards_punishments': [],
    'parents': [],
    'notices': [],
    'schedules': []
}

# 用于模拟自增ID
next_id = {
    'users': 1,
    'students': 1,
    'courses': 1,
    'enrollments': 1,
    'attendance': 1,
    'rewards_punishments': 1,
    'parents': 1,
    'notices': 1,
    'schedules': 1
}

def load_data():
    """从JSON文件加载数据"""
    global in_memory_data, next_id
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                in_memory_data = loaded_data.get('in_memory_data', {})
                next_id = loaded_data.get('next_id', {})
            print(f"Data loaded successfully from {DATA_FILE}")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {DATA_FILE}. Initializing with empty data.")
            in_memory_data = {
                'users': [], 'students': [], 'courses': [], 'enrollments': [],
                'attendance': [], 'rewards_punishments': [], 'parents': [],
                'notices': [], 'schedules': []
            }
            next_id = {
                'users': 1, 'students': 1, 'courses': 1, 'enrollments': 1,
                'attendance': 1, 'rewards_punishments': 1, 'parents': 1,
                'notices': 1, 'schedules': 1
            }
        except Exception as e:
            print(f"An unexpected error occurred while loading data: {e}")
            # Fallback to empty data if loading fails
            in_memory_data = {
                'users': [], 'students': [], 'courses': [], 'enrollments': [],
                'attendance': [], 'rewards_punishments': [], 'parents': [],
                'notices': [], 'schedules': []
            }
            next_id = {
                'users': 1, 'students': 1, 'courses': 1, 'enrollments': 1,
                'attendance': 1, 'rewards_punishments': 1, 'parents': 1,
                'notices': 1, 'schedules': 1
            }
    else:
        print(f"Data file {DATA_FILE} not found. Initializing with empty data.")

def save_data():
    """将数据保存到JSON文件"""
    global in_memory_data, next_id
    data_to_save = {
        'in_memory_data': in_memory_data,
        'next_id': next_id
    }
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        print(f"Data saved successfully to {DATA_FILE}")
    except Exception as e:
        print(f"Error saving data to {DATA_FILE}: {e}")

def get_next_id(table_name):
    """获取并递增指定表的下一个可用ID"""
    global next_id # 声明使用全局变量
    _id = next_id.get(table_name, 1) # 使用.get()以防新表没有初始化ID
    next_id[table_name] = _id + 1
    return _id

def find_item_by_id(table_name, item_id):
    """在内存数据中根据ID查找单个项目"""
    for item in in_memory_data[table_name]:
        if item['id'] == item_id:
            return item
    return None

def find_items_by_attribute(table_name, attribute, value):
    """在内存数据中根据属性查找项目列表"""
    return [item for item in in_memory_data[table_name] if item.get(attribute) == value]

def delete_item_by_id(table_name, item_id):
    """从内存数据中删除指定ID的项目"""
    global in_memory_data # 声明使用全局变量
    original_len = len(in_memory_data[table_name])
    in_memory_data[table_name] = [item for item in in_memory_data[table_name] if item['id'] != item_id]
    return len(in_memory_data[table_name]) < original_len # True if item was found and deleted

def init_in_memory_data():
    """初始化内存数据，包括默认用户和一些示例数据"""
    print("Checking for initial data...")

    # 只有当 'users' 表为空时才添加默认用户
    if not in_memory_data['users']:
        print("Adding default users...")
        # Admin
        hashed_password = generate_password_hash('adminpass')
        in_memory_data['users'].append({
            'id': get_next_id('users'),
            'username': 'admin',
            'password': hashed_password,
            'role': 'admin',
            'student_info_id': None
        })
        print("Default admin user created: username='admin', password='adminpass'")
    
        # Teacher
        teacher_user_id = get_next_id('users')
        hashed_password = generate_password_hash('teacherpass')
        in_memory_data['users'].append({
            'id': teacher_user_id,
            'username': 'teacher',
            'password': hashed_password,
            'role': 'teacher',
            'student_info_id': None
        })
        print("Default teacher user created: username='teacher', password='teacherpass'")

        # Student (用户账户)
        student_user_id = get_next_id('users')
        hashed_password = generate_password_hash('studentpass')
        in_memory_data['users'].append({
            'id': student_user_id,
            'username': 'student',
            'password': hashed_password,
            'role': 'student',
            'student_info_id': None # 初始设置为None, 稍后关联
        })
        print("Default student user created: username='student', password='studentpass'")
        
        # 示例学生数据 (张三)
        student_zhangsan_id = get_next_id('students')
        in_memory_data['students'].append({
            'id': student_zhangsan_id,
            'name': '张三',
            'gender': '男',
            'age': 15,
            'student_id': 'S001',
            'contact_phone': '13800001111',
            'family_info': '父亲：张大山，母亲：李小花',
            'class_name': '三年二班',
            'homeroom_teacher': '李老师'
        })
        print("Default student '张三' created.")

        # 关联学生用户与学生信息
        for u in in_memory_data['users']:
            if u['username'] == 'student':
                u['student_info_id'] = student_zhangsan_id
                print(f"Student user '{u['username']}' linked to student info ID {student_zhangsan_id}")
                break

        # 示例课程数据
        course_math_id = get_next_id('courses')
        in_memory_data['courses'].append({
            'id': course_math_id,
            'name': '数学',
            'description': '基础数学课程',
            'credits': 3,
            'capacity': 50
        })
        print("Default course '数学' created.")
        
        course_english_id = get_next_id('courses')
        in_memory_data['courses'].append({
            'id': course_english_id,
            'name': '英语',
            'description': '英语听说读写',
            'credits': 4,
            'capacity': 40
        })
        print("Default course '英语' created.")

        course_history_id = get_next_id('courses')
        in_memory_data['courses'].append({
            'id': course_history_id,
            'name': '历史',
            'description': '中国历史',
            'credits': 2,
            'capacity': None
        })
        print("Default course '历史' created.")

        # 示例选课及成绩 (张三选修数学)
        in_memory_data['enrollments'].append({
            'id': get_next_id('enrollments'),
            'student_id': student_zhangsan_id,
            'course_id': course_math_id,
            'exam_score': 85,
            'performance_score': 90
        })
        print("Default enrollment for '张三' in '数学' created.")
        
        # 示例选课 (张三选修英语)
        in_memory_data['enrollments'].append({
            'id': get_next_id('enrollments'),
            'student_id': student_zhangsan_id,
            'course_id': course_english_id,
            'exam_score': None,
            'performance_score': None
        })
        print("Default enrollment for '张三' in '英语' created.")
        
        # 示例排课数据
        in_memory_data['schedules'].append({
            'id': get_next_id('schedules'),
            'course_id': course_math_id,
            'teacher_user_id': teacher_user_id,
            'day_of_week': 'Monday',
            'start_time': '09:00',
            'end_time': '10:30',
            'location': 'Room 101',
            'semester': '2023-2024 Fall'
        })
        print("Default schedule for '数学' created.")
        
        in_memory_data['schedules'].append({
            'id': get_next_id('schedules'),
            'course_id': course_english_id,
            'teacher_user_id': teacher_user_id,
            'day_of_week': 'Tuesday',
            'start_time': '10:00',
            'end_time': '11:30',
            'location': 'Room 203',
            'semester': '2023-2024 Fall'
        })
        print("Default schedule for '英语' created.")
        
        # 如果添加了默认数据，保存一次
        save_data()
    else:
        print("Existing data found. Skipping default data initialization.")


# 在应用启动时加载数据，然后检查是否需要初始化默认数据
with app.app_context():
    load_data()
    init_in_memory_data() # 仅在数据为空时添加默认数据

# --- Flask Request Context 处理 ---
# 使用 g 对象来标记数据是否被修改，并在请求结束时统一保存
@app.before_request
def before_request():
    g.data_modified = False

@app.after_request
def after_request(response):
    if g.data_modified:
        save_data()
    return response

# --- 权限控制装饰器 ---
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录。', 'warning')
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped_view

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('您没有权限访问此页面。', 'danger')
            return redirect(url_for('index'))
        return view(*args, **kwargs)
    return wrapped_view

def teacher_or_admin_required(view):
    @functools.wraps(view)
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
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录。', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'student':
            flash('您没有权限访问此页面。', 'danger')
            return redirect(url_for('index'))
        return view(*args, **kwargs)
    return wrapped_view

# --- 路由 ---

@app.route('/')
@login_required
def index():
    student_count = len(in_memory_data['students'])
    course_count = len(in_memory_data['courses'])
    
    # 今日考勤统计
    today_date = datetime.date.today().strftime('%Y-%m-%d')
    present_count = sum(1 for a in in_memory_data['attendance'] if a['date'] == today_date and a['status'] == 'present')
    absent_count = sum(1 for a in in_memory_data['attendance'] if a['date'] == today_date and a['status'] == 'absent')
    leave_count = sum(1 for a in in_memory_data['attendance'] if a['date'] == today_date and a['status'] == 'leave')

    # 获取最近的5条通知
    recent_notices = sorted(in_memory_data['notices'], key=lambda x: x['date'], reverse=True)[:5]
    
    return render_template('index.html', 
                           student_count=student_count, 
                           course_count=course_count,
                           present_count=present_count,
                           absent_count=absent_count,
                           leave_count=leave_count,
                           recent_notices=recent_notices)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = None
        for u in in_memory_data['users']:
            if u['username'] == username:
                user = u
                break

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f'欢迎回来, {user["username"]} ({user["role"]})!', 'success')
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

# --- 学生信息管理 ---
@app.route('/students')
@teacher_or_admin_required
def students():
    students = sorted(in_memory_data['students'], key=lambda x: x['student_id'])
    return render_template('students.html', students=students)

@app.route('/students/add', methods=['GET', 'POST'])
@teacher_or_admin_required
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        age = request.form['age']
        student_id = request.form['student_id']
        contact_phone = request.form['contact_phone']
        family_info = request.form['family_info']
        class_name = request.form['class_name']
        homeroom_teacher = request.form['homeroom_teacher']

        if not name or not gender or not age or not student_id:
            flash('姓名、性别、年龄和学号为必填项！', 'danger')
        else:
            # 检查学号唯一性
            if any(s['student_id'] == student_id for s in in_memory_data['students']):
                flash(f'学号 {student_id} 已存在，请检查。', 'danger')
            else:
                new_student = {
                    'id': get_next_id('students'),
                    'name': name,
                    'gender': gender,
                    'age': int(age),
                    'student_id': student_id,
                    'contact_phone': contact_phone,
                    'family_info': family_info,
                    'class_name': class_name,
                    'homeroom_teacher': homeroom_teacher
                }
                in_memory_data['students'].append(new_student)
                g.data_modified = True # 标记数据已修改
                flash('学生信息添加成功！', 'success')
                return redirect(url_for('students'))
    return render_template('add_edit_student.html', student={})

@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
@teacher_or_admin_required
def edit_student(id):
    student = find_item_by_id('students', id)

    if student is None:
        flash('学生未找到！', 'danger')
        return redirect(url_for('students'))

    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        age = request.form['age']
        student_id = request.form['student_id']
        contact_phone = request.form['contact_phone']
        family_info = request.form['family_info']
        class_name = request.form['class_name']
        homeroom_teacher = request.form['homeroom_teacher']

        if not name or not gender or not age or not student_id:
            flash('姓名、性别、年龄和学号为必填项！', 'danger')
        else:
            # 检查学号唯一性，排除当前学生
            if any(s['student_id'] == student_id and s['id'] != id for s in in_memory_data['students']):
                flash(f'学号 {student_id} 已存在，请检查。', 'danger')
            else:
                student.update({
                    'name': name,
                    'gender': gender,
                    'age': int(age),
                    'student_id': student_id,
                    'contact_phone': contact_phone,
                    'family_info': family_info,
                    'class_name': class_name,
                    'homeroom_teacher': homeroom_teacher
                })
                g.data_modified = True # 标记数据已修改
                flash('学生信息更新成功！', 'success')
                return redirect(url_for('students'))
    
    return render_template('add_edit_student.html', student=student)

@app.route('/students/delete/<int:id>', methods=['POST'])
@teacher_or_admin_required
def delete_student(id):
    global in_memory_data # 需要修改全局变量
    # 实现级联删除
    in_memory_data['enrollments'] = [e for e in in_memory_data['enrollments'] if e['student_id'] != id]
    in_memory_data['attendance'] = [a for a in in_memory_data['attendance'] if a['student_id'] != id]
    in_memory_data['rewards_punishments'] = [rp for rp in in_memory_data['rewards_punishments'] if rp['student_id'] != id]
    in_memory_data['parents'] = [p for p in in_memory_data['parents'] if p['student_id'] != id]

    if delete_item_by_id('students', id):
        g.data_modified = True # 标记数据已修改
        flash('学生信息删除成功！', 'success')
    else:
        flash('学生未找到！', 'danger')
    return redirect(url_for('students'))

# --- 课程信息管理 ---
# Helper to get enrolled count for a course
def get_enrolled_count(course_id):
    return sum(1 for e in in_memory_data['enrollments'] if e['course_id'] == course_id)

# Helper to check if a student is enrolled in a course
def is_student_enrolled_in_course(student_info_id, course_id):
    return any(e['student_id'] == student_info_id and e['course_id'] == course_id for e in in_memory_data['enrollments'])

@app.route('/courses')
@login_required # 所有登录用户都可以查看课程列表
def courses():
    all_courses = sorted(in_memory_data['courses'], key=lambda x: x['name'])
    
    processed_courses = []
    current_student_info_id = None

    if session.get('role') == 'student':
        current_user = find_item_by_id('users', session['user_id'])
        if current_user:
            current_student_info_id = current_user.get('student_info_id')

    for course in all_courses:
        course_data = copy.deepcopy(course) # Work on a copy to add dynamic fields
        course_data['enrolled_count'] = get_enrolled_count(course['id'])
        
        if current_student_info_id:
            course_data['is_enrolled_by_current_user'] = is_student_enrolled_in_course(current_student_info_id, course['id'])
        else:
            course_data['is_enrolled_by_current_user'] = False # Not a student or student info not linked

        processed_courses.append(course_data)

    return render_template('courses.html', courses=processed_courses)

@app.route('/courses/add', methods=['GET', 'POST'])
@teacher_or_admin_required
def add_course():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        credits = request.form['credits']
        capacity = request.form['capacity']

        if not name or not credits:
            flash('课程名称和学分为必填项！', 'danger')
        else:
            # 检查课程名称唯一性
            if any(c['name'] == name for c in in_memory_data['courses']):
                flash(f'课程名称 {name} 已存在，请检查。', 'danger')
            else:
                new_course = {
                    'id': get_next_id('courses'),
                    'name': name,
                    'description': description,
                    'credits': int(credits),
                    'capacity': int(capacity) if capacity else None # 如果容量为空，则设置为None (不限)
                }
                in_memory_data['courses'].append(new_course)
                g.data_modified = True # 标记数据已修改
                flash('课程添加成功！', 'success')
                return redirect(url_for('courses'))
    return render_template('add_edit_course.html', course={})

@app.route('/courses/edit/<int:id>', methods=['GET', 'POST'])
@teacher_or_admin_required
def edit_course(id):
    course = find_item_by_id('courses', id)

    if course is None:
        flash('课程未找到！', 'danger')
        return redirect(url_for('courses'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        credits = request.form['credits']
        capacity = request.form['capacity']

        if not name or not credits:
            flash('课程名称和学分为必填项！', 'danger')
        else:
            # 检查课程名称唯一性，排除当前课程
            if any(c['name'] == name and c['id'] != id for c in in_memory_data['courses']):
                flash(f'课程名称 {name} 已存在，请检查。', 'danger')
            else:
                course.update({
                    'name': name,
                    'description': description,
                    'credits': int(credits),
                    'capacity': int(capacity) if capacity else None
                })
                g.data_modified = True # 标记数据已修改
                flash('课程信息更新成功！', 'success')
                return redirect(url_for('courses'))
    
    return render_template('add_edit_course.html', course=course)

@app.route('/courses/delete/<int:id>', methods=['POST'])
@teacher_or_admin_required
def delete_course(id):
    global in_memory_data # 需要修改全局变量
    # 实现级联删除
    in_memory_data['enrollments'] = [e for e in in_memory_data['enrollments'] if e['course_id'] != id]
    in_memory_data['schedules'] = [s for s in in_memory_data['schedules'] if s['course_id'] != id] # 级联删除排课

    if delete_item_by_id('courses', id):
        g.data_modified = True # 标记数据已修改
        flash('课程删除成功！', 'success')
    else:
        flash('课程未找到！', 'danger')
    return redirect(url_for('courses'))

@app.route('/course/<int:id>/enroll', methods=['POST'])
@student_required
def enroll_course(id):
    course = find_item_by_id('courses', id)
    if not course:
        flash('课程未找到！', 'danger')
        return redirect(url_for('courses'))

    current_user = find_item_by_id('users', session['user_id'])
    if not current_user or not current_user.get('student_info_id'):
        flash('您的学生信息未关联，无法选课。', 'danger')
        return redirect(url_for('courses'))
    
    student_info_id = current_user['student_info_id']

    if is_student_enrolled_in_course(student_info_id, id):
        flash(f'您已选修课程 "{course["name"]}"。', 'info')
        return redirect(url_for('courses'))
    
    enrolled_count = get_enrolled_count(id)
    if course['capacity'] is not None and enrolled_count >= course['capacity']:
        flash(f'课程 "{course["name"]}" 已满，无法选课。', 'danger')
        return redirect(url_for('courses'))

    new_enrollment = {
        'id': get_next_id('enrollments'),
        'student_id': student_info_id,
        'course_id': id,
        'exam_score': None,
        'performance_score': None
    }
    in_memory_data['enrollments'].append(new_enrollment)
    g.data_modified = True # 标记数据已修改
    flash(f'成功选修课程 "{course["name"]}"！', 'success')
    return redirect(url_for('courses'))

@app.route('/course/<int:id>/unenroll', methods=['POST'])
@student_required
def unenroll_course(id):
    global in_memory_data # 需要修改全局变量
    course = find_item_by_id('courses', id)
    if not course:
        flash('课程未找到！', 'danger')
        return redirect(url_for('courses'))

    current_user = find_item_by_id('users', session['user_id'])
    if not current_user or not current_user.get('student_info_id'):
        flash('您的学生信息未关联，无法退课。', 'danger')
        return redirect(url_for('courses'))
    
    student_info_id = current_user['student_info_id']

    enrollment_found = False
    new_enrollments = []
    for e in in_memory_data['enrollments']:
        if e['student_id'] == student_info_id and e['course_id'] == id:
            enrollment_found = True
        else:
            new_enrollments.append(e)
    
    if enrollment_found:
        in_memory_data['enrollments'] = new_enrollments
        g.data_modified = True # 标记数据已修改
        flash(f'成功退选课程 "{course["name"]}"。', 'success')
    else:
        flash(f'您未选修课程 "{course["name"]}"。', 'info')

    return redirect(url_for('courses'))


# --- 学生签到功能 ---
@app.route('/student/checkin', methods=['POST'])
@student_required
def student_checkin():
    current_user_id = session['user_id']
    current_user = find_item_by_id('users', current_user_id)

    if not current_user or current_user.get('student_info_id') is None:
        flash('您的学生信息未关联，无法进行签到。请联系管理员。', 'danger')
        return redirect(url_for('index'))

    student_info_id = current_user['student_info_id']
    today_date = datetime.date.today().strftime('%Y-%m-%d')

    # 检查今天是否已经签到
    existing_attendance = [
        a for a in in_memory_data['attendance']
        if a['student_id'] == student_info_id and a['date'] == today_date
    ]

    if existing_attendance:
        flash(f'您今天 ({today_date}) 已经签到过了。', 'info')
    else:
        new_attendance = {
            'id': get_next_id('attendance'),
            'student_id': student_info_id,
            'date': today_date,
            'status': 'present',
            'reason': '学生自主签到' # 明确签到来源
        }
        in_memory_data['attendance'].append(new_attendance)
        g.data_modified = True # 标记数据已修改
        flash(f'签到成功！今天 ({today_date}) 的出勤状态已记录。', 'success')

    return redirect(url_for('index'))

@app.route('/course/<int:id>/students')
@teacher_or_admin_required
def view_course_students(id):
    course = find_item_by_id('courses', id)
    if not course:
        flash('课程未找到！', 'danger')
        return redirect(url_for('courses'))
    
    enrolled_students = []
    enrollments_list = []  # 创建一个enrollments列表用于传递给模板
    for e in in_memory_data['enrollments']:
        if e['course_id'] == id:
            student = find_item_by_id('students', e['student_id'])
            if student:
                student_data = copy.deepcopy(student)
                student_data['exam_score'] = e['exam_score']
                student_data['performance_score'] = e['performance_score']
                enrolled_students.append(student_data)
                # 同时保存enrollment信息
                enrollment_data = copy.deepcopy(e)
                enrollments_list.append(enrollment_data)
    
    enrolled_students = sorted(enrolled_students, key=lambda x: x['name'])
    return render_template('course_students.html', course=course, students=enrolled_students, enrollments=enrollments_list)


# --- 学生选课与成绩管理 (Enrollments) ---
# 此处的enrollments路由主要用于教师/管理员查看和管理某个学生的选课及成绩
@app.route('/students/<int:student_id>/enrollments')
@teacher_or_admin_required
def enrollments(student_id):
    student = find_item_by_id('students', student_id)
    if not student:
        flash('学生未找到！', 'danger')
        return redirect(url_for('students'))

    # 关联查询：手动组合数据
    enrollments_list = []
    for e in in_memory_data['enrollments']:
        if e['student_id'] == student_id:
            course = find_item_by_id('courses', e['course_id'])
            if course:
                enrollment_data = copy.deepcopy(e) # 避免直接修改原始内存数据
                enrollment_data['course_name'] = course['name']
                enrollment_data['credits'] = course['credits'] # 添加学分信息
                enrollments_list.append(enrollment_data)
    
    enrollments_list = sorted(enrollments_list, key=lambda x: x['course_name'])
    return render_template('enrollments.html', student=student, enrollments=enrollments_list)

@app.route('/students/<int:student_id>/enrollments/add', methods=['GET', 'POST'])
@teacher_or_admin_required
def add_enrollment(student_id):
    student = find_item_by_id('students', student_id)
    if not student:
        flash('学生未找到！', 'danger')
        return redirect(url_for('students'))
    
    courses = sorted(in_memory_data['courses'], key=lambda x: x['name'])

    if request.method == 'POST':
        course_id = int(request.form['course_id'])
        exam_score = request.form['exam_score']
        performance_score = request.form['performance_score']

        if not course_id:
            flash('请选择课程！', 'danger')
        else:
            # 检查唯一性 (student_id, course_id)
            if any(e['student_id'] == student_id and e['course_id'] == course_id for e in in_memory_data['enrollments']):
                flash('该学生已选修此课程！', 'danger')
            else:
                new_enrollment = {
                    'id': get_next_id('enrollments'),
                    'student_id': student_id,
                    'course_id': course_id,
                    'exam_score': int(exam_score) if exam_score else None,
                    'performance_score': int(performance_score) if performance_score else None
                }
                in_memory_data['enrollments'].append(new_enrollment)
                g.data_modified = True # 标记数据已修改
                flash('选课及成绩添加成功！', 'success')
                return redirect(url_for('enrollments', student_id=student_id))
    
    return render_template('add_edit_enrollment.html', student=student, courses=courses, enrollment={})

@app.route('/enrollments/edit/<int:enrollment_id>', methods=['GET', 'POST'])
@teacher_or_admin_required
def edit_enrollment(enrollment_id):
    enrollment = find_item_by_id('enrollments', enrollment_id)

    if not enrollment:
        flash('选课记录未找到！', 'danger')
        return redirect(url_for('students'))
    
    student_id = enrollment['student_id']
    course_id = enrollment['course_id']  # 获取课程ID
    student = find_item_by_id('students', student_id)
    courses = sorted(in_memory_data['courses'], key=lambda x: x['name'])

    if request.method == 'POST':
        new_course_id = int(request.form['course_id'])
        exam_score = request.form['exam_score']
        performance_score = request.form['performance_score']
        referrer = request.form.get('referrer', '')  # 获取referrer参数

        if not new_course_id:
            flash('请选择课程！', 'danger')
        else:
            # 检查唯一性 (student_id, course_id)，排除当前记录
            if any(e['student_id'] == student_id and e['course_id'] == new_course_id and e['id'] != enrollment_id for e in in_memory_data['enrollments']):
                flash('该学生已选修此课程！', 'danger')
            else:
                enrollment.update({
                    'course_id': new_course_id,
                    'exam_score': int(exam_score) if exam_score else None,
                    'performance_score': int(performance_score) if performance_score else None
                })
                g.data_modified = True # 标记数据已修改
                flash('选课及成绩更新成功！', 'success')
                
                # 根据referrer决定重定向
                if referrer:
                    return redirect(referrer)
                else:
                    # 默认重定向到学生选课列表
                    return redirect(url_for('enrollments', student_id=student_id))
    
    # GET请求时也传递referrer到模板
    referrer = request.args.get('referrer', '')
    return render_template('add_edit_enrollment.html', 
                         student=student, 
                         courses=courses, 
                         enrollment=enrollment,
                         referrer=referrer)
@app.route('/enrollments/delete/<int:enrollment_id>', methods=['POST'])
@teacher_or_admin_required
def delete_enrollment(enrollment_id):
    enrollment = find_item_by_id('enrollments', enrollment_id)
    if not enrollment:
        flash('选课记录未找到！', 'danger')
        return redirect(url_for('students'))

    student_id = enrollment['student_id']
    if delete_item_by_id('enrollments', enrollment_id):
        g.data_modified = True # 标记数据已修改
        flash('选课记录删除成功！', 'success')
    else:
        flash('选课记录未找到！', 'danger')
    return redirect(url_for('enrollments', student_id=student_id))

# --- 学生考勤管理 ---
@app.route('/attendance')
@teacher_or_admin_required
def attendance():
    attendance_records = []
    for a in in_memory_data['attendance']:
        student = find_item_by_id('students', a['student_id'])
        if student:
            record_data = copy.deepcopy(a)
            record_data['student_name'] = student['name']
            record_data['student_id_str'] = student['student_id'] # Use 'student_id_str' to avoid confusion with the int 'student_id'
            attendance_records.append(record_data)
    
    attendance_records = sorted(attendance_records, key=lambda x: (x['date'], x['student_name']), reverse=True)
    return render_template('attendance.html', attendance_records=attendance_records)

@app.route('/attendance/add', methods=['GET', 'POST'])
@teacher_or_admin_required
def add_attendance():
    students = sorted(in_memory_data['students'], key=lambda x: x['name'])

    if request.method == 'POST':
        student_id = int(request.form['student_id'])
        date = request.form['date']
        status = request.form['status']
        reason = request.form['reason']

        if not student_id or not date or not status:
            flash('学生、日期和状态为必填项！', 'danger')
        else:
            # 检查唯一性 (student_id, date)
            if any(a['student_id'] == student_id and a['date'] == date for a in in_memory_data['attendance']):
                flash(f'学生 {student_id} 在 {date} 的考勤记录已存在，请检查。', 'danger')
            else:
                new_attendance = {
                    'id': get_next_id('attendance'),
                    'student_id': student_id,
                    'date': date,
                    'status': status,
                    'reason': reason
                }
                in_memory_data['attendance'].append(new_attendance)
                g.data_modified = True # 标记数据已修改
                flash('考勤记录添加成功！', 'success')
                return redirect(url_for('attendance'))
    
    return render_template('add_edit_attendance.html', students=students, attendance_record={})

@app.route('/attendance/edit/<int:id>', methods=['GET', 'POST'])
@teacher_or_admin_required
def edit_attendance(id):
    attendance_record = find_item_by_id('attendance', id)

    if not attendance_record:
        flash('考勤记录未找到！', 'danger')
        return redirect(url_for('attendance'))
    
    students = sorted(in_memory_data['students'], key=lambda x: x['name'])

    if request.method == 'POST':
        new_student_id = int(request.form['student_id'])
        new_date = request.form['date']
        status = request.form['status']
        reason = request.form['reason']

        if not new_student_id or not new_date or not status:
            flash('学生、日期和状态为必填项！', 'danger')
        else:
            # 检查唯一性 (student_id, date)，排除当前记录
            if any(a['student_id'] == new_student_id and a['date'] == new_date and a['id'] != id for a in in_memory_data['attendance']):
                flash(f'学生 {new_student_id} 在 {new_date} 的考勤记录已存在，请检查。', 'danger')
            else:
                attendance_record.update({
                    'student_id': new_student_id,
                    'date': new_date,
                    'status': status,
                    'reason': reason
                })
                g.data_modified = True # 标记数据已修改
                flash('考勤记录更新成功！', 'success')
                return redirect(url_for('attendance'))
    
    return render_template('add_edit_attendance.html', students=students, attendance_record=attendance_record)

@app.route('/attendance/delete/<int:id>', methods=['POST'])
@teacher_or_admin_required
def delete_attendance(id):
    if delete_item_by_id('attendance', id):
        g.data_modified = True # 标记数据已修改
        flash('考勤记录删除成功！', 'success')
    else:
        flash('考勤记录未找到！', 'danger')
    return redirect(url_for('attendance'))

# --- 学生奖励与处分管理 ---
@app.route('/rewards_punishments')
@teacher_or_admin_required
def rewards_punishments():
    records = []
    for rp in in_memory_data['rewards_punishments']:
        student = find_item_by_id('students', rp['student_id'])
        if student:
            record_data = copy.deepcopy(rp)
            record_data['student_name'] = student['name']
            record_data['student_id_str'] = student['student_id']
            records.append(record_data)
    
    records = sorted(records, key=lambda x: (x['date'], x['student_name']), reverse=True)
    return render_template('rewards_punishments.html', records=records)

@app.route('/rewards_punishments/add', methods=['GET', 'POST'])
@teacher_or_admin_required
def add_reward_punishment():
    students = sorted(in_memory_data['students'], key=lambda x: x['name'])

    if request.method == 'POST':
        student_id = int(request.form['student_id'])
        type = request.form['type']
        description = request.form['description']
        date = request.form['date']

        if not student_id or not type or not description or not date:
            flash('学生、类型、描述和日期为必填项！', 'danger')
        else:
            new_record = {
                'id': get_next_id('rewards_punishments'),
                'student_id': student_id,
                'type': type,
                'description': description,
                'date': date
            }
            in_memory_data['rewards_punishments'].append(new_record)
            g.data_modified = True # 标记数据已修改
            flash('奖励/处分记录添加成功！', 'success')
            return redirect(url_for('rewards_punishments'))
    
    return render_template('add_edit_reward_punishment.html', students=students, record={})

@app.route('/rewards_punishments/edit/<int:id>', methods=['GET', 'POST'])
@teacher_or_admin_required
def edit_reward_punishment(id):
    record = find_item_by_id('rewards_punishments', id)

    if not record:
        flash('奖励/处分记录未找到！', 'danger')
        return redirect(url_for('rewards_punishments'))
    
    students = sorted(in_memory_data['students'], key=lambda x: x['name'])

    if request.method == 'POST':
        student_id = int(request.form['student_id'])
        type = request.form['type']
        description = request.form['description']
        date = request.form['date']

        if not student_id or not type or not description or not date:
            flash('学生、类型、描述和日期为必填项！', 'danger')
        else:
            record.update({
                'student_id': student_id,
                'type': type,
                'description': description,
                'date': date
            })
            g.data_modified = True # 标记数据已修改
            flash('奖励/处分记录更新成功！', 'success')
            return redirect(url_for('rewards_punishments'))
    
    return render_template('add_edit_reward_punishment.html', students=students, record=record)

@app.route('/rewards_punishments/delete/<int:id>', methods=['POST'])
@teacher_or_admin_required
def delete_reward_punishment(id):
    if delete_item_by_id('rewards_punishments', id):
        g.data_modified = True # 标记数据已修改
        flash('奖励/处分记录删除成功！', 'success')
    else:
        flash('奖励/处分记录未找到！', 'danger')
    return redirect(url_for('rewards_punishments'))

# --- 学生家长信息管理 ---
@app.route('/parents')
@teacher_or_admin_required
def parents():
    parents_list = []
    for p in in_memory_data['parents']:
        student = find_item_by_id('students', p['student_id'])
        if student:
            parent_data = copy.deepcopy(p)
            parent_data['student_name'] = student['name']
            parent_data['student_id_str'] = student['student_id']
            parents_list.append(parent_data)
    
    parents_list = sorted(parents_list, key=lambda x: (x['student_name'], x['relationship']))
    return render_template('parents.html', parents=parents_list)

@app.route('/parents/add', methods=['GET', 'POST'])
@teacher_or_admin_required
def add_parent():
    students = sorted(in_memory_data['students'], key=lambda x: x['name'])

    if request.method == 'POST':
        student_id = int(request.form['student_id'])
        name = request.form['name']
        relationship = request.form['relationship']
        contact_phone = request.form['contact_phone']
        email = request.form['email']

        if not student_id or not name:
            flash('学生和家长姓名为必填项！', 'danger')
        else:
            new_parent = {
                'id': get_next_id('parents'),
                'student_id': student_id,
                'name': name,
                'relationship': relationship,
                'contact_phone': contact_phone,
                'email': email
            }
            in_memory_data['parents'].append(new_parent)
            g.data_modified = True # 标记数据已修改
            flash('家长信息添加成功！', 'success')
            return redirect(url_for('parents'))
    
    return render_template('add_edit_parent.html', students=students, parent={})

@app.route('/parents/edit/<int:id>', methods=['GET', 'POST'])
@teacher_or_admin_required
def edit_parent(id):
    parent = find_item_by_id('parents', id)

    if not parent:
        flash('家长信息未找到！', 'danger')
        return redirect(url_for('parents'))
    
    students = sorted(in_memory_data['students'], key=lambda x: x['name'])

    if request.method == 'POST':
        student_id = int(request.form['student_id'])
        name = request.form['name']
        relationship = request.form['relationship']
        contact_phone = request.form['contact_phone']
        email = request.form['email']

        if not student_id or not name:
            flash('学生和家长姓名为必填项！', 'danger')
        else:
            parent.update({
                'student_id': student_id,
                'name': name,
                'relationship': relationship,
                'contact_phone': contact_phone,
                'email': email
            })
            g.data_modified = True # 标记数据已修改
            flash('家长信息更新成功！', 'success')
            return redirect(url_for('parents'))
    
    return render_template('add_edit_parent.html', students=students, parent=parent)

@app.route('/parents/delete/<int:id>', methods=['POST'])
@teacher_or_admin_required
def delete_parent(id):
    if delete_item_by_id('parents', id):
        g.data_modified = True # 标记数据已修改
        flash('家长信息删除成功！', 'success')
    else:
        flash('家长信息未找到！', 'danger')
    return redirect(url_for('parents'))

# --- 通知/联系记录管理 ---
@app.route('/notices')
@login_required
def notices():
    notices_list = sorted(in_memory_data['notices'], key=lambda x: x['date'], reverse=True)
    return render_template('notices.html', notices=notices_list)

@app.route('/notices/add', methods=['GET', 'POST'])
@teacher_or_admin_required
def add_notice():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        target = request.form['target']
        sender = session.get('username', 'Unknown')

        if not title or not content:
            flash('标题和内容为必填项！', 'danger')
        else:
            new_notice = {
                'id': get_next_id('notices'),
                'title': title,
                'content': content,
                'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'target': target,
                'sender': sender
            }
            in_memory_data['notices'].append(new_notice)
            g.data_modified = True # 标记数据已修改
            flash('通知发布成功！', 'success')
            return redirect(url_for('notices'))
    return render_template('add_edit_notice.html', notice={})

@app.route('/notices/edit/<int:id>', methods=['GET', 'POST'])
@teacher_or_admin_required
def edit_notice(id):
    notice = find_item_by_id('notices', id)

    if not notice:
        flash('通知未找到！', 'danger')
        return redirect(url_for('notices'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        target = request.form['target']

        if not title or not content:
            flash('标题和内容为必填项！', 'danger')
        else:
            notice.update({
                'title': title,
                'content': content,
                'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), # 更新日期
                'target': target
            })
            g.data_modified = True # 标记数据已修改
            flash('通知更新成功！', 'success')
            return redirect(url_for('notices'))
    
    return render_template('add_edit_notice.html', notice=notice)

@app.route('/notices/delete/<int:id>', methods=['POST'])
@teacher_or_admin_required
def delete_notice(id):
    if delete_item_by_id('notices', id):
        g.data_modified = True # 标记数据已修改
        flash('通知删除成功！', 'success')
    else:
        flash('通知未找到！', 'danger')
    return redirect(url_for('notices'))

# --- 系统管理员权限管理 (用户管理) ---
@app.route('/users')
@admin_required
def users():
    users_list = sorted(in_memory_data['users'], key=lambda x: x['username'])
    return render_template('users.html', users=users_list)

@app.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        student_info_id = request.form.get('student_info_id') # 获取学生信息ID，如果角色是学生

        if not username or not password or not role:
            flash('用户名、密码和角色为必填项！', 'danger')
        elif role == 'student' and not student_info_id:
            flash('学生角色必须关联一个学生信息！', 'danger')
        else:
            # 检查用户名唯一性
            if any(u['username'] == username for u in in_memory_data['users']):
                flash(f'用户名 {username} 已存在，请检查。', 'danger')
            else:
                hashed_password = generate_password_hash(password)
                new_user = {
                    'id': get_next_id('users'),
                    'username': username,
                    'password': hashed_password,
                    'role': role,
                    'student_info_id': int(student_info_id) if student_info_id and role == 'student' else None
                }
                in_memory_data['users'].append(new_user)
                g.data_modified = True # 标记数据已修改
                flash('用户添加成功！', 'success')
                return redirect(url_for('users'))
    
    # 传递所有学生信息，以便管理员在添加学生用户时进行关联
    students_for_selection = sorted(in_memory_data['students'], key=lambda x: x['name'])
    return render_template('add_edit_user.html', user={}, students_for_selection=students_for_selection)

@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    user = find_item_by_id('users', id)

    if not user:
        flash('用户未找到！', 'danger')
        return redirect(url_for('users'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        student_info_id = request.form.get('student_info_id')

        if not username or not role:
            flash('用户名和角色为必填项！', 'danger')
        elif role == 'student' and not student_info_id:
            flash('学生角色必须关联一个学生信息！', 'danger')
        else:
            # 检查用户名唯一性，排除当前用户
            if any(u['username'] == username and u['id'] != id for u in in_memory_data['users']):
                flash(f'用户名 {username} 已存在，请检查。', 'danger')
            else:
                user['username'] = username
                user['role'] = role
                if password: # 如果输入了新密码，则更新
                    user['password'] = generate_password_hash(password)
                user['student_info_id'] = int(student_info_id) if student_info_id and role == 'student' else None
                
                g.data_modified = True # 标记数据已修改
                flash('用户信息更新成功！', 'success')
                return redirect(url_for('users'))
    
    students_for_selection = sorted(in_memory_data['students'], key=lambda x: x['name'])
    return render_template('add_edit_user.html', user=user, students_for_selection=students_for_selection)

@app.route('/users/delete/<int:id>', methods=['POST'])
@admin_required
def delete_user(id):
    if id == session.get('user_id'):
        flash('不能删除当前登录的用户！', 'danger')
    else:
        if delete_item_by_id('users', id):
            g.data_modified = True # 标记数据已修改
            flash('用户删除成功！', 'success')
        else:
            flash('用户未找到！', 'danger')
    return redirect(url_for('users'))

# --- 成绩查询 (学生角色) ---
@app.route('/grades')
@login_required
def view_grades():
    if session['role'] != 'student':
        flash('您没有权限访问此页面。', 'danger')
        return redirect(url_for('index'))
    
    current_user_id = session['user_id']
    current_user = find_item_by_id('users', current_user_id) # 找到当前登录的用户对象

    # 确保用户存在且有 student_info_id 关联
    if not current_user or current_user.get('student_info_id') is None:
        flash('未找到您的学生信息，请联系管理员。', 'danger')
        return redirect(url_for('index'))

    student_id = current_user['student_info_id'] # 使用关联的 student_info_id
    student_info = find_item_by_id('students', student_id) # 获取学生信息

    if not student_info: # 再次检查，以防 student_info_id 指向了一个不存在的学生
        flash('未找到您的学生信息，请联系管理员。', 'danger')
        return redirect(url_for('index'))

    grades_list = []
    for e in in_memory_data['enrollments']:
        if e['student_id'] == student_id:
            course = find_item_by_id('courses', e['course_id'])
            if course:
                grade_data = {
                    'course_name': course['name'],
                    'credits': course['credits'], # 添加学分信息
                    'exam_score': e['exam_score'],
                    'performance_score': e['performance_score']
                }
                grades_list.append(grade_data)
    
    return render_template('grades.html', grades=grades_list, student_name=student_info['name'])

# --- 排课管理 ---
def check_schedule_conflict(new_schedule, current_schedule_id=None):
    """
    检查新排课或更新排课是否与现有排课冲突。
    冲突条件：
    1. 同一时间，同一地点有其他课程。
    2. 同一时间，同一教师有其他课程。
    """
    for existing_schedule in in_memory_data['schedules']:
        # 排除当前正在编辑的排课记录本身
        if current_schedule_id and existing_schedule['id'] == current_schedule_id:
            continue

        if existing_schedule['day_of_week'] == new_schedule['day_of_week']:
            # 检查时间是否有重叠
            # max(start1, start2) < min(end1, end2) 表示时间重叠
            if max(new_schedule['start_time'], existing_schedule['start_time']) < min(new_schedule['end_time'], existing_schedule['end_time']):
                # 地点冲突
                if existing_schedule['location'].lower() == new_schedule['location'].lower():
                    course = find_item_by_id('courses', existing_schedule['course_id'])
                    return f"时间冲突：{new_schedule['day_of_week']} {new_schedule['start_time']}-{new_schedule['end_time']}，教室 {new_schedule['location']} 已被课程 '{course['name']}' 占用。"
                # 教师冲突
                if existing_schedule['teacher_user_id'] == new_schedule['teacher_user_id']:
                    teacher = find_item_by_id('users', existing_schedule['teacher_user_id'])
                    course = find_item_by_id('courses', existing_schedule['course_id'])
                    return f"时间冲突：{new_schedule['day_of_week']} {new_schedule['start_time']}-{new_schedule['end_time']}，教师 '{teacher['username']}' 已被课程 '{course['name']}' 占用。"
    return None # 无冲突

@app.route('/schedules')
@teacher_or_admin_required
def schedules():
    schedules_list = []
    for s in in_memory_data['schedules']:
        schedule_data = copy.deepcopy(s)
        course = find_item_by_id('courses', s['course_id'])
        teacher = find_item_by_id('users', s['teacher_user_id'])
        
        schedule_data['course_name'] = course['name'] if course else '未知课程'
        schedule_data['teacher_name'] = teacher['username'] if teacher else '未知教师'
        schedules_list.append(schedule_data)
    
    # 按星期、开始时间排序
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    schedules_list.sort(key=lambda x: (day_order.index(x['day_of_week']), x['start_time']))

    return render_template('schedules.html', schedules=schedules_list)

@app.route('/schedules/add', methods=['GET', 'POST'])
@teacher_or_admin_required
def add_schedule():
    courses = sorted(in_memory_data['courses'], key=lambda x: x['name'])
    teachers = sorted([u for u in in_memory_data['users'] if u['role'] == 'teacher'], key=lambda x: x['username'])
    
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    if request.method == 'POST':
        course_id = int(request.form['course_id'])
        teacher_user_id = int(request.form['teacher_user_id'])
        day_of_week = request.form['day_of_week']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        location = request.form['location']
        semester = request.form.get('semester', '未知学期')

        if not all([course_id, teacher_user_id, day_of_week, start_time, end_time, location]):
            flash('所有字段均为必填项！', 'danger')
        elif start_time >= end_time:
            flash('开始时间必须早于结束时间！', 'danger')
        else:
            new_schedule_data = {
                'course_id': course_id,
                'teacher_user_id': teacher_user_id,
                'day_of_week': day_of_week,
                'start_time': start_time,
                'end_time': end_time,
                'location': location,
                'semester': semester
            }
            conflict_message = check_schedule_conflict(new_schedule_data)
            if conflict_message:
                flash(conflict_message, 'danger')
            else:
                new_schedule_data['id'] = get_next_id('schedules')
                in_memory_data['schedules'].append(new_schedule_data)
                g.data_modified = True # 标记数据已修改
                flash('排课添加成功！', 'success')
                return redirect(url_for('schedules'))
    
    return render_template('add_edit_schedule.html', 
                           schedule={}, 
                           courses=courses, 
                           teachers=teachers, 
                           days_of_week=days_of_week)

@app.route('/schedules/edit/<int:id>', methods=['GET', 'POST'])
@teacher_or_admin_required
def edit_schedule(id):
    schedule = find_item_by_id('schedules', id)
    if not schedule:
        flash('排课记录未找到！', 'danger')
        return redirect(url_for('schedules'))

    courses = sorted(in_memory_data['courses'], key=lambda x: x['name'])
    teachers = sorted([u for u in in_memory_data['users'] if u['role'] == 'teacher'], key=lambda x: x['username'])
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    if request.method == 'POST':
        course_id = int(request.form['course_id'])
        teacher_user_id = int(request.form['teacher_user_id'])
        day_of_week = request.form['day_of_week']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        location = request.form['location']
        semester = request.form.get('semester', '未知学期')

        if not all([course_id, teacher_user_id, day_of_week, start_time, end_time, location]):
            flash('所有字段均为必填项！', 'danger')
        elif start_time >= end_time:
            flash('开始时间必须早于结束时间！', 'danger')
        else:
            updated_schedule_data = {
                'course_id': course_id,
                'teacher_user_id': teacher_user_id,
                'day_of_week': day_of_week,
                'start_time': start_time,
                'end_time': end_time,
                'location': location,
                'semester': semester
            }
            conflict_message = check_schedule_conflict(updated_schedule_data, current_schedule_id=id)
            if conflict_message:
                flash(conflict_message, 'danger')
            else:
                schedule.update(updated_schedule_data)
                g.data_modified = True # 标记数据已修改
                flash('排课更新成功！', 'success')
                return redirect(url_for('schedules'))
    
    return render_template('add_edit_schedule.html', 
                           schedule=schedule, 
                           courses=courses, 
                           teachers=teachers, 
                           days_of_week=days_of_week)

@app.route('/schedules/delete/<int:id>', methods=['POST'])
@teacher_or_admin_required
def delete_schedule(id):
    if delete_item_by_id('schedules', id):
        g.data_modified = True # 标记数据已修改
        flash('排课删除成功！', 'success')
    else:
        flash('排课未找到！', 'danger')
    return redirect(url_for('schedules'))


# --- 管理员端统计分析与辅助决策 ---
@app.route('/statistics')
@login_required
def statistics():
    # 学生总数
    total_students = len(in_memory_data['students'])
    
    # 按性别统计学生
    students_by_gender_raw = {}
    for s in in_memory_data['students']:
        gender = s['gender']
        students_by_gender_raw[gender] = students_by_gender_raw.get(gender, 0) + 1
    students_by_gender = [{'gender': g, 'count': c} for g, c in students_by_gender_raw.items()]
    
    # 课程总数
    total_courses = len(in_memory_data['courses'])
    
    # 考勤概览 (过去7天)
    today = datetime.date.today()
    attendance_summary_dict = {}
    for i in range(7):
        date = (today - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        attendance_summary_dict[date] = {'date': date, 'present_count': 0, 'absent_count': 0, 'leave_count': 0}

    for a in in_memory_data['attendance']:
        if a['date'] in attendance_summary_dict:
            if a['status'] == 'present':
                attendance_summary_dict[a['date']]['present_count'] += 1
            elif a['status'] == 'absent':
                attendance_summary_dict[a['date']]['absent_count'] += 1
            elif a['status'] == 'leave':
                attendance_summary_dict[a['date']]['leave_count'] += 1
    
    attendance_summary = sorted(attendance_summary_dict.values(), key=lambda x: x['date'])

    # 平均考试成绩和表现成绩
    course_scores = {} # {course_id: {'exam_scores': [], 'performance_scores': []}}
    for e in in_memory_data['enrollments']:
        if e['course_id'] not in course_scores:
            course_scores[e['course_id']] = {'exam_scores': [], 'performance_scores': []}
        if e['exam_score'] is not None:
            course_scores[e['course_id']]['exam_scores'].append(e['exam_score'])
        if e['performance_score'] is not None:
            course_scores[e['course_id']]['performance_scores'].append(e['performance_score'])

    avg_scores = []
    for course_id, scores_data in course_scores.items():
        course = find_item_by_id('courses', course_id)
        if course:
            avg_exam = sum(scores_data['exam_scores']) / len(scores_data['exam_scores']) if scores_data['exam_scores'] else None
            avg_performance = sum(scores_data['performance_scores']) / len(scores_data['performance_scores']) if scores_data['performance_scores'] else None
            avg_scores.append({
                'course_name': course['name'],
                'avg_exam_score': round(avg_exam, 2) if avg_exam is not None else 'N/A',
                'avg_performance_score': round(avg_performance, 2) if avg_performance is not None else 'N/A'
            })
    avg_scores = sorted(avg_scores, key=lambda x: x['course_name'])

    # 奖励与处分概览
    rp_summary_dict = {}
    for rp in in_memory_data['rewards_punishments']:
        rp_type = rp['type']
        rp_summary_dict[rp_type] = rp_summary_dict.get(rp_type, 0) + 1
    rp_summary = [{'type': t, 'count': c} for t, c in rp_summary_dict.items()]
    
    return render_template('statistics.html', 
                           total_students=total_students,
                           students_by_gender=students_by_gender,
                           total_courses=total_courses,
                           attendance_summary=attendance_summary,
                           avg_scores=avg_scores,
                           rp_summary=rp_summary)

# --- 学生个人统计分析 ---
@app.route('/stu_statistics')
@student_required
def stu_statistics():
    """学生个人统计分析页面"""
    if session['role'] != 'student':
        flash('您没有权限访问此页面。', 'danger')
        return redirect(url_for('index'))
    
    current_user_id = session['user_id']
    current_user = find_item_by_id('users', current_user_id)
    
    if not current_user or current_user.get('student_info_id') is None:
        flash('未找到您的学生信息，请联系管理员。', 'danger')
        return redirect(url_for('index'))
    
    student_id = current_user['student_info_id']
    student_info = find_item_by_id('students', student_id)
    
    if not student_info:
        flash('未找到您的学生信息，请联系管理员。', 'danger')
        return redirect(url_for('index'))
    
    # 1. 获取学生成绩数据（用于趋势分析）
    grades_data = []
    for e in in_memory_data['enrollments']:
        if e['student_id'] == student_id and e['exam_score'] is not None:
            course = find_item_by_id('courses', e['course_id'])
            if course:
                total_score = (e['exam_score'] + e['performance_score']) / 2 if e['performance_score'] else e['exam_score']
                grades_data.append({
                    'course_name': course['name'],
                    'exam_score': e['exam_score'],
                    'performance_score': e['performance_score'],
                    'total_score': round(total_score, 2)
                })
    
    # 2. 获取班级平均成绩（用于对比分析）
    class_avg_scores = {}
    for course in in_memory_data['courses']:
        course_enrollments = [e for e in in_memory_data['enrollments'] if e['course_id'] == course['id'] and e['exam_score'] is not None]
        if course_enrollments:
            avg_exam = sum(e['exam_score'] for e in course_enrollments) / len(course_enrollments)
            perf_scores = [e['performance_score'] for e in course_enrollments if e['performance_score'] is not None]
            avg_perf = sum(perf_scores) / len(perf_scores) if perf_scores else None
            avg_total = round((avg_exam + avg_perf) / 2, 2) if avg_perf else round(avg_exam, 2)
            class_avg_scores[course['name']] = {
                'avg_exam': round(avg_exam, 2),
                'avg_perf': round(avg_perf, 2) if avg_perf else None,
                'avg_total': avg_total
            }
    
    # 3. 获取出勤数据（用于学习计划建议）
    attendance_records = [a for a in in_memory_data['attendance'] if a['student_id'] == student_id]
    present_count = sum(1 for a in attendance_records if a['status'] == 'present')
    absent_count = sum(1 for a in attendance_records if a['status'] == 'absent')
    leave_count = sum(1 for a in attendance_records if a['status'] == 'leave')
    total_attendance = len(attendance_records)
    attendance_rate = round((present_count / total_attendance) * 100, 2) if total_attendance > 0 else 0
    
    # 4. 获取奖励处分数据
    rewards = [rp for rp in in_memory_data['rewards_punishments'] if rp['student_id'] == student_id and rp['type'] == 'reward']
    punishments = [rp for rp in in_memory_data['rewards_punishments'] if rp['student_id'] == student_id and rp['type'] == 'punishment']
    
    # 5. 获取上课时间分布数据
    # 先获取学生选修的课程
    student_courses = []
    for e in in_memory_data['enrollments']:
        if e['student_id'] == student_id:
            course = find_item_by_id('courses', e['course_id'])
            if course:
                student_courses.append(course['id'])
    
    # 获取这些课程的排课信息
    schedule_distribution = {}
    for schedule in in_memory_data['schedules']:
        if schedule['course_id'] in student_courses:
            day = schedule['day_of_week']
            if day not in schedule_distribution:
                schedule_distribution[day] = []
            course = find_item_by_id('courses', schedule['course_id'])
            schedule_distribution[day].append({
                'start_time': schedule['start_time'],
                'end_time': schedule['end_time'],
                'course_name': course['name'] if course else '未知课程',
                'location': schedule['location']
            })
    
    # 6. 生成学习计划建议
    study_recommendations = generate_study_recommendations(grades_data, attendance_records, rewards, punishments)
    
     # 7. 为图表准备数据（确保数据结构正确）
    chart_data = {
        'course_names': [grade['course_name'] for grade in grades_data],
        'my_scores': [grade['total_score'] for grade in grades_data],
        'class_avg_scores': []
    }
    
    # 为每个课程获取班级平均分
    for grade in grades_data:
        course_name = grade['course_name']
        if course_name in class_avg_scores:
            chart_data['class_avg_scores'].append(class_avg_scores[course_name]['avg_total'])
        else:
            chart_data['class_avg_scores'].append(None)  # 如果没有平均分数据，用None填充
    
    return render_template('stu_statistics.html',
                         student=student_info,
                         grades_data=grades_data,
                         class_avg_scores=class_avg_scores,
                         attendance_rate=attendance_rate,
                         present_count=present_count,
                         absent_count=absent_count,
                         leave_count=leave_count,
                         rewards=rewards,
                         punishments=punishments,
                         schedule_distribution=schedule_distribution,
                         study_recommendations=study_recommendations,
                         chart_data=chart_data)
def generate_study_recommendations(grades_data, attendance_records, rewards, punishments):
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
    recent_attendance = sorted(attendance_records, key=lambda x: x['date'], reverse=True)[:10]
    recent_absences = [a for a in recent_attendance if a['status'] == 'absent']
    
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

@app.route('/student/courses')
@student_required
def student_courses():
    # 获取当前登录的学生用户信息
    current_user = find_item_by_id('users', session['user_id'])
    if not current_user or not current_user.get('student_info_id'):
        flash('您的学生信息未关联，无法查看课程。', 'danger')
        return redirect(url_for('index'))
    
    student_info_id = current_user['student_info_id']
    
    # 获取所有课程并添加选课状态
    all_courses = sorted(in_memory_data['courses'], key=lambda x: x['name'])
    processed_courses = []
    
    for course in all_courses:
        course_data = copy.deepcopy(course)
        course_data['enrolled_count'] = get_enrolled_count(course['id'])
        course_data['is_enrolled_by_current_user'] = is_student_enrolled_in_course(student_info_id, course['id'])
        
        processed_courses.append(course_data)
    
    return render_template('student_courses.html', courses=processed_courses)

if __name__ == '__main__':
    print(f"\n--- Data will be stored in '{DATA_FILE}'. It will persist across server restarts. ---")
    app.run(debug=True)

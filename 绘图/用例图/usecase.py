from graphviz import Digraph

# 创建有向图，设置横向布局
dot = Digraph('教育综合管理平台用例图', format='png', graph_attr={'rankdir': 'LR', 'fontname': 'SimHei'})
dot.attr('node', fontname='SimHei')  # 设置节点字体支持中文
dot.attr('edge', fontname='SimHei')  # 设置边字体支持中文

# --------------------------
# 1. 参与者 (Actors)
# --------------------------
dot.node('guest', '访客', shape='box', style='filled', fillcolor='#f0f0f0')
dot.node('student', '学生', shape='box', style='filled', fillcolor='#e6f7ff')
dot.node('teacher', '教师', shape='box', style='filled', fillcolor='#fff2e6')
dot.node('admin', '管理员', shape='box', style='filled', fillcolor='#ffe6e6')

# 参与者泛化关系（权限层次）
dot.edge('student', 'guest', label='泛化', arrowhead='empty')
dot.edge('teacher', 'student', label='泛化', arrowhead='empty')
dot.edge('admin', 'teacher', label='泛化', arrowhead='empty')

# --------------------------
# 2. 认证相关用例
# --------------------------
dot.node('login', '登录系统', shape='ellipse')
dot.node('logout', '退出系统', shape='ellipse')
dot.node('auth', '身份验证', shape='ellipse')
dot.node('clear_session', '清除会话', shape='ellipse')

# 包含关系
dot.edge('login', 'auth', label='包含', style='dashed')
dot.edge('logout', 'clear_session', label='包含', style='dashed')

# 参与者与认证用例关联
dot.edge('student', 'login')
dot.edge('student', 'logout')
dot.edge('teacher', 'login')
dot.edge('teacher', 'logout')
dot.edge('admin', 'login')
dot.edge('admin', 'logout')

# --------------------------
# 3. 学生用例
# --------------------------
# 核心用例
dot.node('view_personal_info', '查看个人信息', shape='ellipse')
dot.node('view_my_courses', '查看所选课程', shape='ellipse')
dot.node('view_grades', '查看成绩', shape='ellipse')
dot.node('view_attendance', '查看考勤', shape='ellipse')
dot.node('view_schedule', '查看课表', shape='ellipse')
dot.node('view_notices', '查看通知', shape='ellipse')
dot.node('select_course', '在线选课/取消选课', shape='ellipse')
dot.node('view_rewards', '查看奖惩记录', shape='ellipse')
dot.node('view_personal_stats', '查看个人统计', shape='ellipse')
dot.node('checkin', '学生签到', shape='ellipse')

# 扩展用例
dot.node('edit_contact', '修改联系方式', shape='ellipse')
dot.node('view_course_details', '查看课程详情', shape='ellipse')
dot.node('view_grade_details', '查看成绩详情', shape='ellipse')
dot.node('view_attendance_details', '查看考勤详情', shape='ellipse')
dot.node('view_schedule_details', '查看课程安排', shape='ellipse')
dot.node('view_notice_details', '查看通知详情', shape='ellipse')
dot.node('view_reward_details', '查看奖惩详情', shape='ellipse')
dot.node('view_study_advice', '查看学习建议', shape='ellipse')

# 学生与核心用例关联
dot.edge('student', 'view_personal_info')
dot.edge('student', 'view_my_courses')
dot.edge('student', 'view_grades')
dot.edge('student', 'view_attendance')
dot.edge('student', 'view_schedule')
dot.edge('student', 'view_notices')
dot.edge('student', 'select_course')
dot.edge('student', 'view_rewards')
dot.edge('student', 'view_personal_stats')
dot.edge('student', 'checkin')

# 学生用例扩展关系
dot.edge('edit_contact', 'view_personal_info', label='扩展', style='dashed', arrowhead='empty')
dot.edge('view_course_details', 'view_my_courses', label='扩展', style='dashed', arrowhead='empty')
dot.edge('view_grade_details', 'view_grades', label='扩展', style='dashed', arrowhead='empty')
dot.edge('view_attendance_details', 'view_attendance', label='扩展', style='dashed', arrowhead='empty')
dot.edge('view_schedule_details', 'view_schedule', label='扩展', style='dashed', arrowhead='empty')
dot.edge('view_notice_details', 'view_notices', label='扩展', style='dashed', arrowhead='empty')
dot.edge('view_reward_details', 'view_rewards', label='扩展', style='dashed', arrowhead='empty')
dot.edge('view_study_advice', 'view_personal_stats', label='扩展', style='dashed', arrowhead='empty')

# --------------------------
# 4. 教师用例
# --------------------------
# 核心用例
dot.node('manage_students', '管理学生', shape='ellipse')
dot.node('manage_courses', '管理课程', shape='ellipse')
dot.node('manage_enrollments', '管理选课', shape='ellipse')
dot.node('record_attendance', '记录考勤', shape='ellipse')
dot.node('manage_grades', '管理成绩', shape='ellipse')
dot.node('manage_rewards', '奖惩管理', shape='ellipse')
dot.node('view_class_info', '查看班级信息', shape='ellipse')
dot.node('manage_schedules', '排课管理', shape='ellipse')
dot.node('publish_notices', '发布通知', shape='ellipse')
dot.node('communicate_parents', '家长沟通', shape='ellipse')
dot.node('view_stats', '查看统计分析', shape='ellipse')

# 扩展用例 - 管理学生
dot.node('add_student', '添加学生', shape='ellipse')
dot.node('edit_student', '编辑学生', shape='ellipse')
dot.node('delete_student', '删除学生', shape='ellipse')
dot.node('search_student', '查询学生', shape='ellipse')

# 扩展用例 - 管理课程
dot.node('add_course', '添加课程', shape='ellipse')
dot.node('edit_course', '编辑课程', shape='ellipse')
dot.node('delete_course', '删除课程', shape='ellipse')
dot.node('search_course', '查询课程', shape='ellipse')

# 扩展用例 - 管理选课
dot.node('add_enrollment', '为学生添加课程', shape='ellipse')
dot.node('remove_enrollment', '为学生删除课程', shape='ellipse')
dot.node('input_enroll_grade', '录入成绩', shape='ellipse')

# 扩展用例 - 记录考勤
dot.node('add_attendance', '添加考勤记录', shape='ellipse')
dot.node('edit_attendance', '编辑考勤记录', shape='ellipse')
dot.node('delete_attendance', '删除考勤记录', shape='ellipse')
dot.node('search_attendance', '查询考勤记录', shape='ellipse')

# 扩展用例 - 管理成绩
dot.node('input_exam_score', '录入考试成绩', shape='ellipse')
dot.node('input_performance_score', '录入平时成绩', shape='ellipse')
dot.node('edit_score', '修改成绩', shape='ellipse')

# 扩展用例 - 奖惩管理
dot.node('add_reward', '添加奖励', shape='ellipse')
dot.node('add_punishment', '添加处分', shape='ellipse')
dot.node('edit_reward_record', '编辑奖惩记录', shape='ellipse')
dot.node('delete_reward_record', '删除奖惩记录', shape='ellipse')

# 扩展用例 - 排课管理
dot.node('add_schedule', '添加排课', shape='ellipse')
dot.node('edit_schedule', '编辑排课', shape='ellipse')
dot.node('delete_schedule', '删除排课', shape='ellipse')

# 扩展用例 - 发布通知
dot.node('add_notice', '添加通知', shape='ellipse')
dot.node('edit_notice', '编辑通知', shape='ellipse')
dot.node('delete_notice', '删除通知', shape='ellipse')

# 扩展用例 - 家长沟通
dot.node('send_parent_notice', '发送通知给家长', shape='ellipse')
dot.node('batch_send_parent', '群发通知给家长', shape='ellipse')

# 扩展用例 - 查看统计分析
dot.node('view_student_stats', '查看学生统计', shape='ellipse')
dot.node('view_course_stats', '查看课程统计', shape='ellipse')
dot.node('view_attendance_stats', '查看考勤统计', shape='ellipse')
dot.node('view_grade_stats', '查看成绩统计', shape='ellipse')
dot.node('view_reward_stats', '查看奖惩统计', shape='ellipse')

# 教师与核心用例关联
dot.edge('teacher', 'manage_students')
dot.edge('teacher', 'manage_courses')
dot.edge('teacher', 'manage_enrollments')
dot.edge('teacher', 'record_attendance')
dot.edge('teacher', 'manage_grades')
dot.edge('teacher', 'manage_rewards')
dot.edge('teacher', 'view_class_info')
dot.edge('teacher', 'manage_schedules')
dot.edge('teacher', 'publish_notices')
dot.edge('teacher', 'communicate_parents')
dot.edge('teacher', 'view_stats')

# 教师用例扩展关系
dot.edge('add_student', 'manage_students', label='扩展', style='dashed', arrowhead='empty')
dot.edge('edit_student', 'manage_students', label='扩展', style='dashed', arrowhead='empty')
dot.edge('delete_student', 'manage_students', label='扩展', style='dashed', arrowhead='empty')
dot.edge('search_student', 'manage_students', label='扩展', style='dashed', arrowhead='empty')

dot.edge('add_course', 'manage_courses', label='扩展', style='dashed', arrowhead='empty')
dot.edge('edit_course', 'manage_courses', label='扩展', style='dashed', arrowhead='empty')
dot.edge('delete_course', 'manage_courses', label='扩展', style='dashed', arrowhead='empty')
dot.edge('search_course', 'manage_courses', label='扩展', style='dashed', arrowhead='empty')

dot.edge('add_enrollment', 'manage_enrollments', label='扩展', style='dashed', arrowhead='empty')
dot.edge('remove_enrollment', 'manage_enrollments', label='扩展', style='dashed', arrowhead='empty')
dot.edge('input_enroll_grade', 'manage_enrollments', label='扩展', style='dashed', arrowhead='empty')

dot.edge('add_attendance', 'record_attendance', label='扩展', style='dashed', arrowhead='empty')
dot.edge('edit_attendance', 'record_attendance', label='扩展', style='dashed', arrowhead='empty')
dot.edge('delete_attendance', 'record_attendance', label='扩展', style='dashed', arrowhead='empty')
dot.edge('search_attendance', 'record_attendance', label='扩展', style='dashed', arrowhead='empty')

dot.edge('input_exam_score', 'manage_grades', label='扩展', style='dashed', arrowhead='empty')
dot.edge('input_performance_score', 'manage_grades', label='扩展', style='dashed', arrowhead='empty')
dot.edge('edit_score', 'manage_grades', label='扩展', style='dashed', arrowhead='empty')

dot.edge('add_reward', 'manage_rewards', label='扩展', style='dashed', arrowhead='empty')
dot.edge('add_punishment', 'manage_rewards', label='扩展', style='dashed', arrowhead='empty')
dot.edge('edit_reward_record', 'manage_rewards', label='扩展', style='dashed', arrowhead='empty')
dot.edge('delete_reward_record', 'manage_rewards', label='扩展', style='dashed', arrowhead='empty')

dot.edge('add_schedule', 'manage_schedules', label='扩展', style='dashed', arrowhead='empty')
dot.edge('edit_schedule', 'manage_schedules', label='扩展', style='dashed', arrowhead='empty')
dot.edge('delete_schedule', 'manage_schedules', label='扩展', style='dashed', arrowhead='empty')

dot.edge('add_notice', 'publish_notices', label='扩展', style='dashed', arrowhead='empty')
dot.edge('edit_notice', 'publish_notices', label='扩展', style='dashed', arrowhead='empty')
dot.edge('delete_notice', 'publish_notices', label='扩展', style='dashed', arrowhead='empty')

dot.edge('send_parent_notice', 'communicate_parents', label='扩展', style='dashed', arrowhead='empty')
dot.edge('batch_send_parent', 'communicate_parents', label='扩展', style='dashed', arrowhead='empty')

dot.edge('view_student_stats', 'view_stats', label='扩展', style='dashed', arrowhead='empty')
dot.edge('view_course_stats', 'view_stats', label='扩展', style='dashed', arrowhead='empty')
dot.edge('view_attendance_stats', 'view_stats', label='扩展', style='dashed', arrowhead='empty')
dot.edge('view_grade_stats', 'view_stats', label='扩展', style='dashed', arrowhead='empty')
dot.edge('view_reward_stats', 'view_stats', label='扩展', style='dashed', arrowhead='empty')

# --------------------------
# 5. 管理员特有用例
# --------------------------
dot.node('view_system_logs', '查看系统日志', shape='ellipse')
dot.node('backup_restore', '数据备份与恢复', shape='ellipse')
dot.node('manage_users', '管理用户', shape='ellipse')

# 管理员特有用例扩展
dot.node('create_user', '创建用户', shape='ellipse')
dot.node('edit_user', '编辑用户', shape='ellipse')
dot.node('delete_user', '删除用户', shape='ellipse')

# 管理员与特有用例关联
dot.edge('admin', 'view_system_logs')
dot.edge('admin', 'backup_restore')
dot.edge('admin', 'manage_users')

# 管理员用例扩展关系
dot.edge('create_user', 'manage_users', label='扩展', style='dashed', arrowhead='empty')
dot.edge('edit_user', 'manage_users', label='扩展', style='dashed', arrowhead='empty')
dot.edge('delete_user', 'manage_users', label='扩展', style='dashed', arrowhead='empty')

# --------------------------
# 生成图片
# --------------------------
dot.render('education_management_usecase', view=True)  # 生成并自动打开图片
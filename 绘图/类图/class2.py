from graphviz import Digraph

# 服务类与实体类关系图
dot_relation = Digraph('服务类与实体类关系图', format='png', 
                      graph_attr={'rankdir': 'LR', 'fontname': 'SimHei', 'splines': 'line'})
dot_relation.attr('node', fontname='SimHei')  # 去掉record形状，改用默认形状
dot_relation.attr('edge', fontname='SimHei')

# =============== 实体类节点 ===============
# 基础模型类（使用矩形框）
dot_relation.node('BaseModel', label='BaseModel\nid: int\ncreated_at: datetime\nupdated_at: datetime\n+to_dict()\n+from_dict()', shape='rectangle')

# 用户相关实体类
dot_relation.node('User', label='User\nusername: str\npassword: str\nrole: str\n+authenticate()\n+has_permission()', shape='rectangle')
dot_relation.node('Student', label='Student\nname: str\ngender: str\nage: int\nclass_name: str\n+get_attendance()\n+get_grades()', shape='rectangle')
dot_relation.node('Teacher', label='Teacher\nname: str\ndepartment: str\nsubject: str\n+manage_courses()\n+record_attendance()', shape='rectangle')
dot_relation.node('Admin', label='Admin\npermission_level: int\n+manage_system()\n+backup_data()', shape='rectangle')

# 课程相关实体类
dot_relation.node('Course', label='Course\nname: str\ncode: str\ncredits: float\n+get_enrollments()\n+get_schedule()', shape='rectangle')
dot_relation.node('Enrollment', label='Enrollment\nstudent_id: int\ncourse_id: int\nscores: float\n+calculate_total()', shape='rectangle')
dot_relation.node('Schedule', label='Schedule\ncourse_id: int\nday: str\ntime: str\n+check_conflict()', shape='rectangle')

# 其他业务实体类
dot_relation.node('Attendance', label='Attendance\nstudent_id: int\ndate: datetime\nstatus: str\n+update_status()', shape='rectangle')
dot_relation.node('RewardPunishment', label='RewardPunishment\nstudent_id: int\ntype: str\ndescription: str\n+get_type()', shape='rectangle')
dot_relation.node('Parent', label='Parent\nname: str\ncontact: str\nstudent_id: int\n+view_child_info()\n+receive_notice()', shape='rectangle')
dot_relation.node('Grade', label='Grade\nenrollment_id: int\ntype: str\nscore: float\n+get_details()', shape='rectangle')
dot_relation.node('Notice', label='Notice\ntitle: str\ncontent: str\nsender_id: int\n+send()\n+archive()', shape='rectangle')

# =============== 服务类节点 ===============
# 接口层（使用菱形框表示接口）
dot_relation.node('IBaseService', label='IBaseService\n+get_by_id()\n+get_all()\n+create()\n+update()\n+delete()', shape='diamond', style='filled', fillcolor='lightblue')

# 核心服务类（使用圆角矩形）
dot_relation.node('UserService', label='UserService\ndb: Database\n+authenticate_user()\n+get_user_by_role()', shape='box')
dot_relation.node('StudentService', label='StudentService\ndb: Database\n+get_student_courses()\n+get_student_attendance()', shape='box')
dot_relation.node('CourseService', label='CourseService\ndb: Database\n+get_course_teachers()\n+get_course_enrollments()', shape='box')

# 业务服务类
dot_relation.node('AttendanceService', label='AttendanceService\ndb: Database\n+record_daily_attendance()\n+get_attendance_stats()', shape='box')
dot_relation.node('NotificationService', label='NotificationService\nemail: EmailClient\n+send_notice()\n+send_parent_message()', shape='box')

# 系统服务类
dot_relation.node('SystemService', label='SystemService\nlogger: Logger\n+backup_database()\n+view_system_logs()', shape='box')

# =============== 关系连线 ===============
# 继承关系 (实体类)
dot_relation.edge('BaseModel', 'User', label='继承', arrowhead='empty')
dot_relation.edge('BaseModel', 'Course', label='继承', arrowhead='empty')
dot_relation.edge('BaseModel', 'Attendance', label='继承', arrowhead='empty')
dot_relation.edge('BaseModel', 'Notice', label='继承', arrowhead='empty')
dot_relation.edge('User', 'Student', label='继承', arrowhead='empty')
dot_relation.edge('User', 'Teacher', label='继承', arrowhead='empty')
dot_relation.edge('User', 'Admin', label='继承', arrowhead='empty')

# 实现关系 (服务类接口实现)
dot_relation.edge('IBaseService', 'UserService', label='实现', arrowhead='empty', style='dashed')
dot_relation.edge('IBaseService', 'StudentService', label='实现', arrowhead='empty', style='dashed')
dot_relation.edge('IBaseService', 'CourseService', label='实现', arrowhead='empty', style='dashed')

# 服务类与实体类的依赖关系
dot_relation.edge('UserService', 'User', label='操作', arrowhead='open', color='blue')
dot_relation.edge('UserService', 'Student', label='操作', arrowhead='open', color='blue')
dot_relation.edge('UserService', 'Teacher', label='操作', arrowhead='open', color='blue')
dot_relation.edge('UserService', 'Admin', label='操作', arrowhead='open', color='blue')

dot_relation.edge('StudentService', 'Student', label='操作', arrowhead='open', color='blue')
dot_relation.edge('StudentService', 'Enrollment', label='操作', arrowhead='open', color='blue')
dot_relation.edge('StudentService', 'Attendance', label='操作', arrowhead='open', color='blue')

dot_relation.edge('CourseService', 'Course', label='操作', arrowhead='open', color='blue')
dot_relation.edge('CourseService', 'Schedule', label='操作', arrowhead='open', color='blue')
dot_relation.edge('CourseService', 'Enrollment', label='操作', arrowhead='open', color='blue')

dot_relation.edge('AttendanceService', 'Attendance', label='操作', arrowhead='open', color='blue')
dot_relation.edge('NotificationService', 'Notice', label='操作', arrowhead='open', color='blue')
dot_relation.edge('NotificationService', 'Parent', label='操作', arrowhead='open', color='blue')

# 服务间依赖关系
dot_relation.edge('StudentService', 'AttendanceService', label='依赖', arrowhead='open', style='dashed')
dot_relation.edge('CourseService', 'NotificationService', label='依赖', arrowhead='open', style='dashed')
dot_relation.edge('NotificationService', 'SystemService', label='依赖', arrowhead='open', style='dashed')

# 生成图片
dot_relation.render('service_entity_relation_diagram', view=False)
print("关系图已生成：service_entity_relation_diagram.png")
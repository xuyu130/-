from graphviz import Digraph

# 实体层类图（树状直线连接）
dot_entity = Digraph('实体层类图（树状结构）', format='png', graph_attr={'rankdir': 'TB', 'fontname': 'SimHei', 'splines': 'line'})
dot_entity.attr('node', fontname='SimHei', shape='record')
dot_entity.attr('edge', fontname='SimHei')

# --------------- 第一层：基础类 ---------------
dot_entity.node('BaseModel', '{BaseModel|id: int\\ncreated_at: datetime\\nupdated_at: datetime|+to_dict()\\n+from_dict()}')

# --------------- 第二层：核心父类 ---------------
with dot_entity.subgraph() as s:
    s.attr(rank='same')  # 强制同一层级
    s.node('User', '{User|username: str\\npassword: str\\nrole: str|+authenticate()\\n+has_permission()}')
    s.node('Course', '{Course|name: str\\ncode: str\\ncredits: float|+get_enrollments()\\n+get_schedule()}')

# --------------- 第三层：用户子类 ---------------
with dot_entity.subgraph() as s:
    s.attr(rank='same')
    s.node('Student', '{Student|name: str\\ngender: str\\nage: int\\nclass_name: str|+get_attendance()\\n+get_grades()}')
    s.node('Teacher', '{Teacher|name: str\\ndepartment: str\\nsubject: str|+manage_courses()\\n+record_attendance()}')
    s.node('Admin', '{Admin|permission_level: int|+manage_system()\\n+backup_data()}')

# --------------- 第四层：业务实体类 ---------------
with dot_entity.subgraph() as s:
    s.attr(rank='same')
    s.node('Enrollment', '{Enrollment|student_id: int\\ncourse_id: int\\nscores: float|+calculate_total()}')
    s.node('Attendance', '{Attendance|student_id: int\\ndate: datetime\\nstatus: str|+update_status()}')
    s.node('RewardPunishment', '{RewardPunishment|student_id: int\\ntype: str\\ndescription: str|+get_type()}')
    s.node('Schedule', '{Schedule|course_id: int\\nday: str\\ntime: str|+check_conflict()}')
    s.node('Parent', '{Parent|name: str\\ncontact: str\\nstudent_id: int|+view_child_info()\\n+receive_notice()}')

# --------------- 第五层：子实体类 ---------------
with dot_entity.subgraph() as s:
    s.attr(rank='same')
    s.node('Grade', '{Grade|enrollment_id: int\\ntype: str\\nscore: float|+get_details()}')
    s.node('Notice', '{Notice|title: str\\ncontent: str\\nsender_id: int|+send()\\n+archive()}')

# ================== 树状连线关系 ==================
# 第一层 → 第二层
dot_entity.edge('BaseModel', 'User', label='继承', arrowhead='empty')
dot_entity.edge('BaseModel', 'Course', label='继承', arrowhead='empty')

# 第二层 → 第三层（User子类）
dot_entity.edge('User', 'Student', label='继承', arrowhead='empty')
dot_entity.edge('User', 'Teacher', label='继承', arrowhead='empty')
dot_entity.edge('User', 'Admin', label='继承', arrowhead='empty')

# 第二层 → 第四层（Course关联）
dot_entity.edge('Course', 'Schedule', label='组合', arrowhead='diamond', style='bold')
dot_entity.edge('Course', 'Enrollment', label='被选（1对多）', arrowhead='vee')

# 第三层 → 第四层（Student关联）
dot_entity.edge('Student', 'Enrollment', label='选课（1对多）', arrowhead='vee')
dot_entity.edge('Student', 'Attendance', label='考勤（1对多）', arrowhead='vee')
dot_entity.edge('Student', 'RewardPunishment', label='奖惩（1对多）', arrowhead='vee')
dot_entity.edge('Student', 'Parent', label='聚合', arrowhead='diamond', style='solid')

# 第四层 → 第五层（Enrollment关联）
dot_entity.edge('Enrollment', 'Grade', label='成绩（1对多）', arrowhead='vee')

# 生成图片
dot_entity.render('entity_tree_class_diagram', view=True)



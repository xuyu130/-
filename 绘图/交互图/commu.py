from graphviz import Digraph
import os

# 确保输出目录存在
os.makedirs('diagrams', exist_ok=True)

def generate_student_info_management_diagram():
    """1. 学生信息管理时序图"""
    dot = Digraph(name='student_info_management', format='png')
    dot.attr(rankdir='LR', size='14,10')
    dot.attr('node', shape='box', style='filled', color='lightblue')

    # 参与者
    participants = [
        'Admin/Teacher',   # 管理员/教师
        'Web界面', 
        'StudentService',  # 学生服务
        'Database'         # 数据库
    ]

    for p in participants:
        dot.node(p)

    # 消息序列
    messages = [
        ('Admin/Teacher', 'Web界面', '1. 访问学生信息管理页面'),
        ('Web界面', 'StudentService', '2. 请求学生列表数据'),
        ('StudentService', 'Database', '3. 查询所有学生记录'),
        ('Database', 'StudentService', '4. 返回学生数据'),
        ('StudentService', 'Web界面', '5. 返回格式化学生列表'),
        ('Web界面', 'Admin/Teacher', '6. 显示学生列表'),
        ('Admin/Teacher', 'Web界面', '7. 提交新增/编辑学生信息（姓名、性别等）'),
        ('Web界面', 'StudentService', '8. 验证并处理学生数据'),
        ('StudentService', 'Database', '9. 保存/更新学生记录'),
        ('Database', 'StudentService', '10. 确认操作结果'),
        ('StudentService', 'Web界面', '11. 返回处理结果'),
        ('Web界面', 'Admin/Teacher', '12. 显示操作成功信息'),
        ('Admin/Teacher', 'Web界面', '13. 选择删除学生'),
        ('Web界面', 'StudentService', '14. 请求删除学生及关联数据'),
        ('StudentService', 'Database', '15. 执行删除操作（级联删除）'),
        ('Database', 'StudentService', '16. 确认删除完成'),
        ('StudentService', 'Web界面', '17. 返回删除结果'),
        ('Web界面', 'Admin/Teacher', '18. 显示删除成功信息')
    ]

    # 添加消息和顺序线
    for i, (src, tgt, label) in enumerate(messages):
        dot.edge(src, tgt, label=label, fontsize='10')
        if i < len(messages)-1:
            with dot.subgraph() as s:
                s.attr(rank='same')
                s.node(f'seq_{i}', shape='point', width='0.1')
                s.node(f'seq_{i+1}', shape='point', width='0.1')
                s.edge(f'seq_{i}', f'seq_{i+1}', style='dashed', constraint='false')

    dot.render('diagrams/student_info_management', view=False)
    return dot


def generate_course_management_diagram():
    """2. 学生课程管理时序图"""
    dot = Digraph(name='course_management', format='png')
    dot.attr(rankdir='LR', size='14,10')
    dot.attr('node', shape='box', style='filled', color='lightgreen')

    # 参与者
    participants = [
        'Admin/Teacher/Student', # 管理员/教师/学生
        'Web界面',
        'CourseService',         # 课程服务
        'EnrollmentService',     # 选课服务
        'GradeService',          # 成绩服务
        'Database'               # 数据库
    ]

    for p in participants:
        dot.node(p)

    # 消息序列
    messages = [
        # 查看课程列表
        ('Admin/Teacher/Student', 'Web界面', '1. 访问课程管理页面'),
        ('Web界面', 'CourseService', '2. 请求课程列表'),
        ('CourseService', 'Database', '3. 查询课程数据'),
        ('Database', 'CourseService', '4. 返回课程信息'),
        ('CourseService', 'Web界面', '5. 返回格式化课程列表'),
        ('Web界面', 'Admin/Teacher/Student', '6. 显示课程列表'),
        
        # 选课操作
        ('Student', 'Web界面', '7. 选择课程进行选课'),
        ('Web界面', 'EnrollmentService', '8. 提交选课请求'),
        ('EnrollmentService', 'Database', '9. 检查课程容量和学生资格'),
        ('Database', 'EnrollmentService', '10. 返回检查结果'),
        ('EnrollmentService', 'Database', '11. 创建选课记录'),
        ('Database', 'EnrollmentService', '12. 确认选课成功'),
        ('EnrollmentService', 'Web界面', '13. 返回选课结果'),
        ('Web界面', 'Student', '14. 显示选课成功信息'),
        
        # 成绩管理
        ('Admin/Teacher', 'Web界面', '15. 访问成绩录入页面'),
        ('Web界面', 'GradeService', '16. 请求成绩录入表单'),
        ('GradeService', 'Database', '17. 获取学生和课程信息'),
        ('Database', 'GradeService', '18. 返回相关信息'),
        ('GradeService', 'Web界面', '19. 显示成绩录入表单'),
        ('Web界面', 'Admin/Teacher', '20. 显示成绩录入界面'),
        ('Admin/Teacher', 'Web界面', '21. 提交成绩信息'),
        ('Web界面', 'GradeService', '22. 处理成绩数据'),
        ('GradeService', 'Database', '23. 保存成绩记录'),
        ('Database', 'GradeService', '24. 确认保存成功'),
        ('GradeService', 'Web界面', '25. 返回保存结果'),
        ('Web界面', 'Admin/Teacher', '26. 显示成绩保存成功')
    ]

    for i, (src, tgt, label) in enumerate(messages):
        dot.edge(src, tgt, label=label, fontsize='10')
        if i < len(messages)-1:
            with dot.subgraph() as s:
                s.attr(rank='same')
                s.node(f'c_seq_{i}', shape='point', width='0.1')
                s.node(f'c_seq_{i+1}', shape='point', width='0.1')
                s.edge(f'c_seq_{i}', f'c_seq_{i+1}', style='dashed', constraint='false')

    dot.render('diagrams/course_management', view=False)
    return dot


def generate_attendance_management_diagram():
    """3. 学生考勤管理时序图"""
    dot = Digraph(name='attendance_management', format='png')
    dot.attr(rankdir='LR', size='14,10')
    dot.attr('node', shape='box', style='filled', color='lightyellow')

    # 参与者
    participants = [
        'Teacher',              # 教师
        'Web界面',
        'AttendanceService',    # 考勤服务
        'Database'              # 数据库
    ]

    for p in participants:
        dot.node(p)

    # 消息序列
    messages = [
        ('Teacher', 'Web界面', '1. 访问考勤管理页面'),
        ('Web界面', 'AttendanceService', '2. 请求考勤记录列表'),
        ('AttendanceService', 'Database', '3. 查询考勤数据'),
        ('Database', 'AttendanceService', '4. 返回考勤记录'),
        ('AttendanceService', 'Web界面', '5. 返回格式化考勤列表'),
        ('Web界面', 'Teacher', '6. 显示考勤记录'),
        ('Teacher', 'Web界面', '7. 选择学生进行考勤登记'),
        ('Web界面', 'AttendanceService', '8. 提交考勤信息'),
        ('AttendanceService', 'Database', '9. 保存考勤记录'),
        ('Database', 'AttendanceService', '10. 确认保存成功'),
        ('AttendanceService', 'Web界面', '11. 返回操作结果'),
        ('Web界面', 'Teacher', '12. 显示考勤登记成功'),
        ('Teacher', 'Web界面', '13. 查询特定时间段考勤统计'),
        ('Web界面', 'AttendanceService', '14. 请求考勤统计信息'),
        ('AttendanceService', 'Database', '15. 聚合查询考勤数据'),
        ('Database', 'AttendanceService', '16. 返回统计结果'),
        ('AttendanceService', 'Web界面', '17. 返回格式化统计信息'),
        ('Web界面', 'Teacher', '18. 显示考勤统计图表')
    ]

    for i, (src, tgt, label) in enumerate(messages):
        dot.edge(src, tgt, label=label, fontsize='10')
        if i < len(messages)-1:
            with dot.subgraph() as s:
                s.attr(rank='same')
                s.node(f'a_seq_{i}', shape='point', width='0.1')
                s.node(f'a_seq_{i+1}', shape='point', width='0.1')
                s.edge(f'a_seq_{i}', f'a_seq_{i+1}', style='dashed', constraint='false')

    dot.render('diagrams/attendance_management', view=False)
    return dot


def generate_reward_punishment_diagram():
    """4. 学生奖励与处分管理时序图"""
    dot = Digraph(name='reward_punishment', format='png')
    dot.attr(rankdir='LR', size='14,10')
    dot.attr('node', shape='box', style='filled', color='lightpink')

    # 参与者
    participants = [
        'Teacher/Admin',             # 教师/管理员
        'Web界面',
        'RewardPunishmentService',   # 奖惩服务
        'Database'                   # 数据库
    ]

    for p in participants:
        dot.node(p)

    # 消息序列
    messages = [
        ('Teacher/Admin', 'Web界面', '1. 访问奖惩管理页面'),
        ('Web界面', 'RewardPunishmentService', '2. 请求奖惩记录列表'),
        ('RewardPunishmentService', 'Database', '3. 查询奖惩数据'),
        ('Database', 'RewardPunishmentService', '4. 返回奖惩记录'),
        ('RewardPunishmentService', 'Web界面', '5. 返回格式化奖惩列表'),
        ('Web界面', 'Teacher/Admin', '6. 显示奖惩记录'),
        ('Teacher/Admin', 'Web界面', '7. 选择添加奖励或处分'),
        ('Web界面', 'RewardPunishmentService', '8. 提交奖惩信息'),
        ('RewardPunishmentService', 'Database', '9. 保存奖惩记录'),
        ('Database', 'RewardPunishmentService', '10. 确认保存成功'),
        ('RewardPunishmentService', 'Web界面', '11. 返回操作结果'),
        ('Web界面', 'Teacher/Admin', '12. 显示奖惩记录添加成功'),
        ('Teacher/Admin', 'Web界面', '13. 查询学生奖惩统计'),
        ('Web界面', 'RewardPunishmentService', '14. 请求学生奖惩统计'),
        ('RewardPunishmentService', 'Database', '15. 聚合查询奖惩数据'),
        ('Database', 'RewardPunishmentService', '16. 返回统计结果'),
        ('RewardPunishmentService', 'Web界面', '17. 返回格式化统计信息'),
        ('Web界面', 'Teacher/Admin', '18. 显示学生奖惩统计')
    ]

    for i, (src, tgt, label) in enumerate(messages):
        dot.edge(src, tgt, label=label, fontsize='10')
        if i < len(messages)-1:
            with dot.subgraph() as s:
                s.attr(rank='same')
                s.node(f'rp_seq_{i}', shape='point', width='0.1')
                s.node(f'rp_seq_{i+1}', shape='point', width='0.1')
                s.edge(f'rp_seq_{i}', f'rp_seq_{i+1}', style='dashed', constraint='false')

    dot.render('diagrams/reward_punishment', view=False)
    return dot


def generate_parent_contact_diagram():
    """5. 学生家长联系管理时序图"""
    dot = Digraph(name='parent_contact', format='png')
    dot.attr(rankdir='LR', size='14,10')
    dot.attr('node', shape='box', style='filled', color='lightcyan')

    # 参与者
    participants = [
        'Admin/Teacher',   # 管理员/教师
        'Web界面', 
        'ParentService',   # 家长服务
        'NotificationService', # 通知服务
        'Database',        # 数据库
        '第三方服务(短信/邮件)'
    ]

    for p in participants:
        dot.node(p)

    # 消息序列
    messages = [
        ('Admin/Teacher', 'Web界面', '1. 访问家长管理页面'),
        ('Web界面', 'ParentService', '2. 请求家长信息(按学生筛选)'),
        ('ParentService', 'Database', '3. 查询家长数据'),
        ('Database', 'ParentService', '4. 返回家长信息'),
        ('ParentService', 'Web界面', '5. 返回家长列表'),
        ('Web界面', 'Admin/Teacher', '6. 显示家长信息'),
        
        # 添加/编辑家长信息
        ('Admin/Teacher', 'Web界面', '7. 提交家长信息(姓名/联系方式等)'),
        ('Web界面', 'ParentService', '8. 处理家长数据'),
        ('ParentService', 'Database', '9. 保存家长记录'),
        ('Database', 'ParentService', '10. 确认记录保存'),
        ('ParentService', 'Web界面', '11. 返回处理结果'),
        ('Web界面', 'Admin/Teacher', '12. 显示操作成功信息'),
        
        # 发送通知
        ('Admin/Teacher', 'Web界面', '13. 选择家长发送通知(内容/方式)'),
        ('Web界面', 'NotificationService', '14. 提交通知请求'),
        ('NotificationService', 'Database', '15. 保存通知记录'),
        ('Database', 'NotificationService', '16. 确认记录保存'),
        ('NotificationService', '第三方服务(短信/邮件)', '17. 转发通知内容'),
        ('第三方服务(短信/邮件)', 'NotificationService', '18. 返回发送结果'),
        ('NotificationService', 'Web界面', '19. 返回通知处理结果'),
        ('Web界面', 'Admin/Teacher', '20. 显示通知发送结果')
    ]

    for i, (src, tgt, label) in enumerate(messages):
        dot.edge(src, tgt, label=label, fontsize='10')
        if i < len(messages)-1:
            with dot.subgraph() as s:
                s.attr(rank='same')
                s.node(f'pc_seq_{i}', shape='point', width='0.1')
                s.node(f'pc_seq_{i+1}', shape='point', width='0.1')
                s.edge(f'pc_seq_{i}', f'pc_seq_{i+1}', style='dashed', constraint='false')

    dot.render('diagrams/parent_contact', view=False)
    return dot


def generate_admin_permission_diagram():
    """6. 系统管理员权限管理时序图"""
    dot = Digraph(name='admin_permission', format='png')
    dot.attr(rankdir='LR', size='14,10')
    dot.attr('node', shape='box', style='filled', color='lightgrey')

    # 参与者
    participants = [
        'Admin',           # 系统管理员
        'Web界面', 
        'UserService',     # 用户服务
        'StatisticsService', # 统计服务
        'Database'         # 数据库
    ]

    for p in participants:
        dot.node(p)

    # 消息序列
    messages = [
        ('Admin', 'Web界面', '1. 访问管理员控制台'),
        ('Web界面', 'UserService', '2. 请求系统用户列表'),
        ('UserService', 'Database', '3. 查询用户数据'),
        ('Database', 'UserService', '4. 返回用户信息'),
        ('UserService', 'Web界面', '5. 返回用户列表'),
        ('Web界面', 'Admin', '6. 显示用户管理页面'),
        
        # 用户管理
        ('Admin', 'Web界面', '7. 新增/编辑/删除用户(设置角色权限)'),
        ('Web界面', 'UserService', '8. 处理用户数据'),
        ('UserService', 'Database', '9. 保存/更新/删除用户记录'),
        ('Database', 'UserService', '10. 确认操作结果'),
        ('UserService', 'Web界面', '11. 返回处理结果'),
        ('Web界面', 'Admin', '12. 显示用户操作结果'),
        
        # 统计分析
        ('Admin', 'Web界面', '13. 访问统计分析页面'),
        ('Web界面', 'StatisticsService', '14. 请求系统统计数据'),
        ('StatisticsService', 'Database', '15. 聚合查询各类数据'),
        ('Database', 'StatisticsService', '16. 返回统计结果'),
        ('StatisticsService', 'Web界面', '17. 返回分析报告'),
        ('Web界面', 'Admin', '18. 显示统计图表和分析结果')
    ]

    for i, (src, tgt, label) in enumerate(messages):
        dot.edge(src, tgt, label=label, fontsize='10')
        if i < len(messages)-1:
            with dot.subgraph() as s:
                s.attr(rank='same')
                s.node(f'ap_seq_{i}', shape='point', width='0.1')
                s.node(f'ap_seq_{i+1}', shape='point', width='0.1')
                s.edge(f'ap_seq_{i}', f'ap_seq_{i+1}', style='dashed', constraint='false')

    dot.render('diagrams/admin_permission', view=False)
    return dot


def generate_complete_sequence_diagram():
    """生成完整的系统顺序图（概览）"""
    dot = Digraph(name='complete_system', format='png')
    dot.attr(rankdir='LR', size='16,12')
    dot.attr('node', shape='box', style='filled')

    # 系统组件
    components = [
        ('User', 'lightblue'),           # 用户
        ('Web界面', 'lightgreen'),       # Web界面
        ('AuthService', 'lightyellow'),   # 认证服务
        ('StudentService', 'lightpink'), # 学生服务
        ('CourseService', 'lightcyan'),  # 课程服务
        ('AttendanceService', 'lightgrey'), # 考勤服务
        ('RewardPunishmentService', 'lightcoral'), # 奖惩服务
        ('ParentService', 'lightsteelblue'), # 家长服务
        ('NotificationService', 'lightsalmon'), # 通知服务
        ('StatisticsService', 'lightseagreen'), # 统计服务
        ('Database', 'lightgoldenrodyellow') # 数据库
    ]

    for name, color in components:
        dot.node(name, fillcolor=color)

    # 主要交互流程
    flows = [
        ('User', 'Web界面', '1. 登录系统'),
        ('Web界面', 'AuthService', '2. 验证身份'),
        ('AuthService', 'Database', '3. 查询用户信息'),
        ('Database', 'AuthService', '4. 返回用户数据'),
        ('AuthService', 'Web界面', '5. 返回验证结果'),
        ('Web界面', 'User', '6. 显示主界面'),
        
        ('User', 'Web界面', '7. 访问学生信息'),
        ('Web界面', 'StudentService', '8. 请求学生数据'),
        ('StudentService', 'Database', '9. 查询学生信息'),
        ('Database', 'StudentService', '10. 返回学生数据'),
        ('StudentService', 'Web界面', '11. 返回学生列表'),
        ('Web界面', 'User', '12. 显示学生信息'),
        
        ('User', 'Web界面', '13. 访问课程管理'),
        ('Web界面', 'CourseService', '14. 请求课程数据'),
        ('CourseService', 'Database', '15. 查询课程信息'),
        ('Database', 'CourseService', '16. 返回课程数据'),
        ('CourseService', 'Web界面', '17. 返回课程列表'),
        ('Web界面', 'User', '18. 显示课程信息'),
        
        ('User', 'Web界面', '19. 查看统计分析'),
        ('Web界面', 'StatisticsService', '20. 请求统计数据'),
        ('StatisticsService', 'Database', '21. 聚合查询数据'),
        ('Database', 'StatisticsService', '22. 返回统计结果'),
        ('StatisticsService', 'Web界面', '23. 返回分析报告'),
        ('Web界面', 'User', '24. 显示统计图表')
    ]

    for i, (src, tgt, label) in enumerate(flows):
        dot.edge(src, tgt, label=label, fontsize='9')
        if i < len(flows)-1:
            with dot.subgraph() as s:
                s.attr(rank='same')
                s.node(f'cs_seq_{i}', shape='point', width='0.1')
                s.node(f'cs_seq_{i+1}', shape='point', width='0.1')
                s.edge(f'cs_seq_{i}', f'cs_seq_{i+1}', style='dashed', constraint='false')

    dot.render('diagrams/complete_system', view=False)
    return dot


if __name__ == "__main__":
    # 生成所有功能的交互图
    generate_student_info_management_diagram()
    generate_course_management_diagram()
    generate_attendance_management_diagram()
    generate_reward_punishment_diagram()
    generate_parent_contact_diagram()
    generate_admin_permission_diagram()
    generate_complete_sequence_diagram()

    print("7个功能模块的交互图已生成，分别为：")
    print("1. 学生信息管理：diagrams/student_info_management.png")
    print("2. 学生课程管理：diagrams/course_management.png")
    print("3. 学生考勤管理：diagrams/attendance_management.png")
    print("4. 学生奖励与处分管理：diagrams/reward_punishment.png")
    print("5. 学生家长联系管理：diagrams/parent_contact.png")
    print("6. 系统管理员权限管理：diagrams/admin_permission.png")
    print("7. 完整系统顺序图：diagrams/complete_system.png")
from graphviz import Digraph

# 统计层类图（树状结构）
dot_stats = Digraph('统计层类图（树状结构）', format='png', 
                    graph_attr={'rankdir': 'TB', 'fontname': 'SimHei', 'splines': 'line'})
dot_stats.attr('node', fontname='SimHei', shape='record')
dot_stats.attr('edge', fontname='SimHei')

# --------------- 第一层：核心管理类 ---------------
dot_stats.node('StatisticsManager', '{StatisticsManager|db: Database|+get_overall_stats()\\n+get_student_stats()\\n+get_course_stats()}')

# --------------- 第二层：统计数据类 ---------------
with dot_stats.subgraph() as s:
    s.attr(rank='same')
    s.node('OverallStats', '{OverallStats|total_students: int\\ntotal_teachers: int\\ntotal_courses: int|+__init__()}')
    s.node('StudentStats', '{StudentStats|gender_dist: dict\\nattendance_rate: float\\navg_grade: float|+calculate_attendance_rate()\\n+calculate_avg_grade()}')
    s.node('CourseStats', '{CourseStats|enrollment_count: dict\\npass_rate: float|+calculate_pass_rate()\\n+get_popular_courses()}')

# --------------- 第三层：报表生成类 ---------------
dot_stats.node('ReportGenerator', '{ReportGenerator|format: str|+generate_pdf_report()\\n+generate_excel_report()\\n+export_to_csv()}')

# --------------- 第四层：依赖服务/实体类 ---------------
with dot_stats.subgraph() as s:
    s.attr(rank='same')
    s.node('StudentService', '{StudentService||...}')
    s.node('CourseService', '{CourseService||...}')
    s.node('Attendance', '{Attendance||...}')
    s.node('Grade', '{Grade||...}')

# ================== 树状连线关系 ==================
# 第一层 → 第二层（聚合关系）
dot_stats.edge('StatisticsManager', 'OverallStats', label='聚合', arrowhead='diamond', style='solid')
dot_stats.edge('StatisticsManager', 'StudentStats', label='聚合', arrowhead='diamond', style='solid')
dot_stats.edge('StatisticsManager', 'CourseStats', label='聚合', arrowhead='diamond', style='solid')

# 第一层 → 第三层（依赖关系）
dot_stats.edge('StatisticsManager', 'ReportGenerator', label='生成报表', arrowhead='open', style='dashed')

# 第二层 → 第四层（依赖关系）
dot_stats.edge('StudentStats', 'Attendance', label='依赖', arrowhead='open', style='dashed')
dot_stats.edge('CourseStats', 'Grade', label='依赖', arrowhead='open', style='dashed')

# 第一层 → 第四层（服务依赖）
dot_stats.edge('StatisticsManager', 'StudentService', label='依赖', arrowhead='open', style='dashed')
dot_stats.edge('StatisticsManager', 'CourseService', label='依赖', arrowhead='open', style='dashed')

# 生成图片（关闭自动打开避免报错）
dot_stats.render('stats_tree_class_diagram', view=False)
print("统计层树状类图已生成：stats_tree_class_diagram.png")
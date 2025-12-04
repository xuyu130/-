from graphviz import Digraph

# 工具支撑层类图
dot_tool = Digraph('工具支撑层类图', format='png', graph_attr={'rankdir': 'TB', 'fontname': 'SimHei'})
dot_tool.attr('node', fontname='SimHei', shape='record')
dot_tool.attr('edge', fontname='SimHei')

# 基础工具类
dot_tool.node('BaseRepository', '{BaseRepository|data_file: str\\ndata: Dict\\ntable_name: str|+__init__()\\n+_load_data()\\n+save_data()\\n+get_next_id()\\n+_ensure_table_exists()\\n+get_all()\\n+get_by_id()\\n+find()\\n+find_one()\\n+create()\\n+update()\\n+delete()\\n+count()\\n+_model_to_dict()\\n+_dict_to_model()}')
dot_tool.node('BaseService', '{BaseService|repo_manager|+__init__()\\n+_validate_required_fields()}')

# 数据转换与验证类
dot_tool.node('DataConverter', '{DataConverter||+model_to_dict()\\n+dict_to_model()}')
dot_tool.node('Validator', '{Validator||+validate_student_data()\\n+validate_course_data()\\n+validate_user_data()}')

# 查询相关类
dot_tool.node('QueryCondition', '{QueryCondition|field: str\\nvalue: Any\\noperator: str|+__init__()\\n+matches()}')
dot_tool.node('QueryBuilder', '{QueryBuilder|conditions: list|+__init__()\\n+where()\\n+build()}')

# 分页与统计类
dot_tool.node('Pagination', '{Pagination|items: List\\npage: int\\nper_page: int\\ntotal: int\\npages: int|+__init__()\\n+has_prev\\n+has_next\\n+get_slice()}')
dot_tool.node('Statistics', '{Statistics||}')

# 结果封装与异常处理类
dot_tool.node('Result', '{Result|success: bool\\ndata: Any\\nmessage: str\\nerror: Any|+__init__()\\n+to_dict()\\n+success()\\n+error()}')
dot_tool.node('BusinessException', '{BusinessException|message: str\\ncode: str|+__init__()}')
dot_tool.node('ValidationException', '{ValidationException||+__init__()}')
dot_tool.node('NotFoundException', '{NotFoundException||+__init__()}')
dot_tool.node('DuplicateException', '{DuplicateException||+__init__()}')

# 类间关系
# 继承关系
dot_tool.edge('BaseRepository', 'UserRepository', label='继承', arrowhead='empty')
dot_tool.edge('BaseRepository', 'StudentRepository', label='继承', arrowhead='empty')
dot_tool.edge('BaseRepository', 'CourseRepository', label='继承', arrowhead='empty')
dot_tool.edge('BusinessException', 'ValidationException', label='继承', arrowhead='empty')
dot_tool.edge('BusinessException', 'NotFoundException', label='继承', arrowhead='empty')
dot_tool.edge('BusinessException', 'DuplicateException', label='继承', arrowhead='empty')
dot_tool.edge('BaseService', 'UserService', label='继承', arrowhead='empty')

# 组合/依赖关系
dot_tool.edge('QueryBuilder', 'QueryCondition', label='组合', arrowhead='diamond')
dot_tool.edge('DataConverter', 'User', label='依赖', arrowhead='open', style='dashed')
dot_tool.edge('DataConverter', 'Student', label='依赖', arrowhead='open', style='dashed')
dot_tool.edge('Validator', 'User', label='依赖', arrowhead='open', style='dashed')
dot_tool.edge('Validator', 'Student', label='依赖', arrowhead='open', style='dashed')
dot_tool.edge('Validator', 'Course', label='依赖', arrowhead='open', style='dashed')

# 生成图片
dot_tool.render('tool_layer_class_diagram', view=False)
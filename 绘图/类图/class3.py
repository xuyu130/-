from graphviz import Digraph

# 工具层类图（树状直线连接）
dot_tool = Digraph('工具层类图（树状结构）', format='png', graph_attr={'rankdir': 'TB', 'fontname': 'SimHei', 'splines': 'line'})
dot_tool.attr('node', fontname='SimHei', shape='record')
dot_tool.attr('edge', fontname='SimHei')

# --------------- 第一层：基础工具类 ---------------
dot_tool.node('BaseTool', '{BaseTool||+init_config()\\n+get_instance()}')

# --------------- 第二层：核心工具类 ---------------
with dot_tool.subgraph() as s:
    s.attr(rank='same')
    s.node('Validator', '{Validator||+validate_user()\\n+validate_student()\\n+validate_course()}')
    s.node('DataConverter', '{DataConverter||+model_to_dict()\\n+dict_to_model()}')
    s.node('Logger', '{Logger|level: str|+info()\\n+warning()\\n+error()}')

# --------------- 第三层：查询工具类 ---------------
with dot_tool.subgraph() as s:
    s.attr(rank='same')
    s.node('QueryCondition', '{QueryCondition|field: str\\nvalue: Any|+__init__()}')
    s.node('Pagination', '{Pagination|page: int\\nsize: int|+get_offset()\\n+get_pages()}')

# --------------- 第四层：组合工具类 ---------------
with dot_tool.subgraph() as s:
    s.attr(rank='same')
    s.node('QueryBuilder', '{QueryBuilder|conditions: list|+where()\\n+and_()\\n+build()}')
    s.node('Config', '{Config|data: dict|+get()\\n+set()\\n+load()}')

# ================== 树状连线关系 ==================
# 第一层 → 第二层
dot_tool.edge('BaseTool', 'Validator', label='继承', arrowhead='empty')
dot_tool.edge('BaseTool', 'DataConverter', label='继承', arrowhead='empty')
dot_tool.edge('BaseTool', 'Logger', label='继承', arrowhead='empty')

# 第二层 → 第三层（依赖）
dot_tool.edge('DataConverter', 'QueryCondition', label='依赖', arrowhead='open', style='dashed')
dot_tool.edge('Validator', 'Pagination', label='依赖', arrowhead='open', style='dashed')

# 第三层 → 第四层（组合）
dot_tool.edge('QueryCondition', 'QueryBuilder', label='组合', arrowhead='diamond', style='bold')
dot_tool.edge('Logger', 'Config', label='依赖', arrowhead='open', style='dashed')

# 生成图片
dot_tool.render('tool_tree_class_diagram', view=True)
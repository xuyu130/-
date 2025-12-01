# app_factory.py
import datetime
import functools
from flask import Flask, g, session, flash, redirect, url_for
from werkzeug.security import generate_password_hash

from models import DataInitializer, Validator, BusinessException
from repositories import repo_manager
from services import service_manager

class AppFactory:
    """Flask应用工厂类"""
    
    def __init__(self):
        self.app = None
        self.repo_manager = repo_manager
        self.service_manager = service_manager
    
    def create_app(self, config=None):
        """创建Flask应用实例"""
        self.app = Flask(__name__)
        
        # 基础配置
        self.app.secret_key = 'your_super_secret_key_here'
        self.app.config['DATA_FILE'] = 'app_data.json'
        
        # 加载自定义配置
        if config:
            self.app.config.update(config)
        
        # 初始化组件
        self._setup_components()
        
        # 设置请求处理
        self._setup_request_handlers()
        
        # 设置路由
        self._setup_routes()
        
        # 初始化数据
        self._init_default_data()
        
        return self.app
    
    def _setup_components(self):
        """设置应用组件"""
        # 这里可以添加其他组件的初始化代码
        pass
    
    def _setup_request_handlers(self):
        """设置请求处理器"""
        
        @self.app.before_request
        def before_request():
            """请求前处理"""
            g.data_modified = False
            g.service_manager = self.service_manager
            g.repo_manager = self.repo_manager
        
        # @self.app.after_request
        # def after_request(response):
        #     """请求后处理 - 确保数据正确保存"""
        #     if hasattr(g, 'data_modified') and g.data_modified:
        #         print("检测到数据修改，正在保存...")  # 调试信息
        #         try:
        #             # 保存所有仓储的数据
        #             self.repo_manager.save_all()
        #             print("数据保存成功")  # 调试信息
        #         except Exception as e:
        #             print(f"数据保存失败: {e}")  # 调试信息
        #     return response
        
        
        @self.app.errorhandler(BusinessException)
        def handle_business_exception(error):
            """处理业务异常"""
            flash(str(error), 'danger')
            return redirect(url_for('index'))
        
        @self.app.errorhandler(404)
        def not_found(error):
            """处理404错误"""
            flash('页面未找到', 'warning')
            return redirect(url_for('index'))
        
        @self.app.errorhandler(500)
        def internal_error(error):
            """处理500错误"""
            flash('服务器内部错误', 'danger')
            return redirect(url_for('index'))
    
    def _setup_routes(self):
        """设置应用路由"""
        
        # 导入路由函数
        from routes import setup_routes
        setup_routes(self.app, self.service_manager)
    
    def _init_default_data(self):
        """初始化默认数据"""
        # 使用仓储管理器初始化数据
        self.repo_manager.init_default_data()
    
    def _create_permission_decorators(self):
        """创建权限装饰器"""
        
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
        
        # 将装饰器添加到应用上下文
        self.app.login_required = login_required
        self.app.admin_required = admin_required
        self.app.teacher_or_admin_required = teacher_or_admin_required
        self.app.student_required = student_required
    
    def get_service(self, service_name):
        """获取服务实例"""
        return getattr(self.service_manager, service_name, None)
    
    def get_repository(self, repo_name):
        """获取仓储实例"""
        return getattr(self.repo_manager, repo_name, None)

class DevelopmentConfig:
    """开发环境配置"""
    DEBUG = True
    TESTING = False
    DATA_FILE = 'app_data_dev.json'

class ProductionConfig:
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    DATA_FILE = 'app_data.json'

class TestingConfig:
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    DATA_FILE = 'app_data_test.json'

class ConfigManager:
    """配置管理器"""
    
    @staticmethod
    def get_config(environment='development'):
        """根据环境获取配置"""
        configs = {
            'development': DevelopmentConfig,
            'production': ProductionConfig,
            'testing': TestingConfig
        }
        
        config_class = configs.get(environment, DevelopmentConfig)
        return {key: value for key, value in config_class.__dict__.items() 
                if not key.startswith('_')}

class AppInitializer:
    """应用初始化器"""
    
    @staticmethod
    def init_app(app, service_manager):
        """初始化应用"""
        # 确保数据目录存在
        import os
        if not os.path.exists('data'):
            os.makedirs('data')
        
        # 初始化默认数据（如果不存在）
        try:
            user_service = service_manager.user_service
            student_service = service_manager.student_service
            course_service = service_manager.course_service
            
            # 检查是否需要创建默认数据
            if user_service.user_repo.count() == 0:
                AppInitializer._create_default_data(service_manager)
                print("默认数据初始化完成")
            else:
                print("使用现有数据")
                
        except Exception as e:
            print(f"初始化应用时发生错误: {e}")
    
    @staticmethod
    def _create_default_data(service_manager):
        """创建默认数据"""
        user_service = service_manager.user_service
        student_service = service_manager.student_service
        course_service = service_manager.course_service
        enrollment_service = service_manager.enrollment_service
        schedule_service = service_manager.schedule_service
        
        # 创建默认学生
        student_data = {
            'name': '张三',
            'gender': '男',
            'age': 15,
            'student_id': 'S001',
            'contact_phone': '13800001111',
            'family_info': '父亲：张大山，母亲：李小花',
            'class_name': '三年二班',
            'homeroom_teacher': '李老师'
        }
        success, student, message = student_service.create_student(student_data)
        
        if success:
            # 创建默认用户
            users_data = [
                {
                    'username': 'admin',
                    'password': 'adminpass',
                    'role': 'admin',
                    'student_info_id': None
                },
                {
                    'username': 'teacher',
                    'password': 'teacherpass',
                    'role': 'teacher',
                    'student_info_id': None
                },
                {
                    'username': 'student',
                    'password': 'studentpass',
                    'role': 'student',
                    'student_info_id': student.id
                }
            ]
            
            for user_data in users_data:
                user_service.create_user(user_data)
            
            # 创建默认课程
            courses_data = [
                {
                    'name': '数学',
                    'description': '基础数学课程',
                    'credits': 3,
                    'capacity': 50
                },
                {
                    'name': '英语',
                    'description': '英语听说读写',
                    'credits': 4,
                    'capacity': 40
                },
                {
                    'name': '历史',
                    'description': '中国历史',
                    'credits': 2,
                    'capacity': None
                }
            ]
            
            created_courses = []
            for course_data in courses_data:
                success, course, message = course_service.create_course(course_data)
                if success:
                    created_courses.append(course)
            
            # 创建默认选课记录
            if created_courses and student:
                enrollment_service.enroll_student(student.id, created_courses[0].id)
                
                # 更新成绩
                enrollments = enrollment_service.get_student_enrollments(student.id)
                if enrollments:
                    enrollment_service.update_scores(
                        enrollments[0].id, 
                        exam_score=85, 
                        performance_score=90
                    )
            
            # 创建默认排课
            teacher_user = user_service.user_repo.get_by_username('teacher')
            if teacher_user and created_courses:
                schedule_data = {
                    'course_id': created_courses[0].id,
                    'teacher_user_id': teacher_user.id,
                    'day_of_week': 'Monday',
                    'start_time': '09:00',
                    'end_time': '10:30',
                    'location': 'Room 101',
                    'semester': '2023-2024 Fall'
                }
                schedule_service.create_schedule(**schedule_data)

class ContextProcessor:
    """上下文处理器"""
    
    @staticmethod
    def inject_services():
        """注入服务到模板上下文"""
        def context_processor():
            from services import service_manager
            return {
                'service_manager': service_manager,
                'current_year': datetime.datetime.now().year
            }
        return context_processor
    
    @staticmethod
    def inject_user_info():
        """注入用户信息到模板上下文"""
        def context_processor():
            user_info = {
                'is_authenticated': False,
                'username': None,
                'role': None,
                'user_id': None
            }
            
            if 'user_id' in session:
                user_info.update({
                    'is_authenticated': True,
                    'username': session.get('username'),
                    'role': session.get('role'),
                    'user_id': session.get('user_id')
                })
            
            return {'current_user': user_info}
        return context_processor

class AppRunner:
    """应用运行器"""
    
    def __init__(self, environment='development'):
        self.environment = environment
        self.app = None
    
    def create_app(self):
        """创建应用实例"""
        # 获取配置
        config = ConfigManager.get_config(self.environment)
        
        # 创建应用工厂
        factory = AppFactory()
        
        # 创建应用
        self.app = factory.create_app(config)
        
        # 初始化应用
        AppInitializer.init_app(self.app, service_manager)
        
        # 添加上下文处理器
        self.app.context_processor(ContextProcessor.inject_services())
        self.app.context_processor(ContextProcessor.inject_user_info())
        
        return self.app
    
    def run(self, host='127.0.0.1', port=5000, debug=None):
        """运行应用"""
        if self.app is None:
            self.create_app()
        
        if debug is None:
            debug = (self.environment == 'development')
        
        print(f"启动学生管理系统...")
        print(f"环境: {self.environment}")
        print(f"地址: http://{host}:{port}")
        print(f"调试模式: {debug}")
        
        self.app.run(host=host, port=port, debug=debug)

def create_app(environment='development'):
    """创建应用的工厂函数"""
    runner = AppRunner(environment)
    return runner.create_app()

def run_app(environment='development', host='127.0.0.1', port=5000):
    """运行应用的便捷函数"""
    runner = AppRunner(environment)
    app = runner.create_app()
    runner.run(host, port)

# 便捷的全局访问点
def get_service(service_name):
    """获取服务实例"""
    return service_manager.get_service(service_name)

def get_repository(repo_name):
    """获取仓储实例"""
    return repo_manager.get_repository(repo_name)

# 测试用的应用创建
if __name__ == '__main__':
    # 开发环境运行
    runner = AppRunner('development')
    app = runner.create_app()
    runner.run(debug=True)
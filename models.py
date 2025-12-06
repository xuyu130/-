# models.py
import datetime
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any

@dataclass
class User:
    id: int
    username: str
    password: str
    role: str
    student_info_id: Optional[int] = None
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Student:
    id: int
    name: str
    gender: str
    age: int
    student_id: str
    contact_phone: str = ""
    family_info: str = ""
    class_name: str = ""
    homeroom_teacher: str = ""
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Course:
    id: int
    name: str
    description: str
    credits: int
    capacity: Optional[int] = None
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Enrollment:
    id: int
    student_id: int
    course_id: int
    exam_score: Optional[float] = None
    performance_score: Optional[float] = None
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Attendance:
    id: int
    student_id: int
    date: str
    status: str
    reason: str
    
    def to_dict(self):
        return asdict(self)

@dataclass
class LeaveRequest:
    id: int
    student_id: int
    start_date: str
    end_date: str
    reason: str
    status: str = 'pending'
    approver_id: Optional[int] = None
    created_at: str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_at: str = ''
    
    def to_dict(self):
        return asdict(self)

@dataclass
class RewardPunishment:
    id: int
    student_id: int
    type: str
    description: str
    date: str
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Parent:
    id: int
    student_id: int
    parent_name: str
    relationship: str
    contact_phone: str
    email: str = ""
    address: str = ""
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Notice:
    id: int
    title: str
    content: str
    target: str
    sender: str
    date: str
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Schedule:
    id: int
    course_id: int
    teacher_user_id: int
    day_of_week: str
    start_time: str
    end_time: str
    location: str
    semester: str
    
    def to_dict(self):
        return asdict(self)

@dataclass
class EnrollmentStatus:
    """选课状态模型类"""
    id: int = 1
    enrollment_open: bool = False
    
    def to_dict(self):
        return asdict(self)

# 数据初始化类
class DataInitializer:
    @staticmethod
    def create_default_data():
        """创建默认数据对象"""
        from werkzeug.security import generate_password_hash
        
        # 默认用户
        users = [
            User(
                id=1,
                username='admin',
                password=generate_password_hash('adminpass'),
                role='admin',
                student_info_id=None
            ),
            User(
                id=2,
                username='teacher',
                password=generate_password_hash('teacherpass'),
                role='teacher',
                student_info_id=None
            ),
            User(
                id=3,
                username='student',
                password=generate_password_hash('studentpass'),
                role='student',
                student_info_id=1  # 关联到张三
            )
        ]
        
        # 默认学生
        students = [
            Student(
                id=1,
                name='张三',
                gender='男',
                age=15,
                student_id='S001',
                contact_phone='13800001111',
                family_info='父亲：张大山，母亲：李小花',
                class_name='三年二班',
                homeroom_teacher='李老师'
            )
        ]
        
        # 默认课程
        courses = [
            Course(
                id=1,
                name='数学',
                description='基础数学课程',
                credits=3,
                capacity=50
            ),
            Course(
                id=2,
                name='英语',
                description='英语听说读写',
                credits=4,
                capacity=40
            ),
            Course(
                id=3,
                name='历史',
                description='中国历史',
                credits=2,
                capacity=None
            )
        ]
        
        # 默认选课记录
        enrollments = [
            Enrollment(
                id=1,
                student_id=1,  # 张三
                course_id=1,   # 数学
                exam_score=85,
                performance_score=90
            ),
            Enrollment(
                id=2,
                student_id=1,  # 张三
                course_id=2,   # 英语
                exam_score=None,
                performance_score=None
            )
        ]
        
        # 默认排课
        schedules = [
            Schedule(
                id=1,
                course_id=1,  # 数学
                teacher_user_id=2,  # 教师用户
                day_of_week='Monday',
                start_time='09:00',
                end_time='10:30',
                location='Room 101',
                semester='2023-2024 Fall'
            ),
            Schedule(
                id=2,
                course_id=2,  # 英语
                teacher_user_id=2,  # 教师用户
                day_of_week='Tuesday',
                start_time='10:00',
                end_time='11:30',
                location='Room 203',
                semester='2023-2024 Fall'
            )
        ]
             
        # 其他空表
        attendance = []
        rewardpunishments= []
        parents = []
        notices = []
        
        return {
            'users': users,
            'students': students,
            'courses': courses,
            'enrollments': enrollments,
            'attendance': attendance,
            'rewardpunishments': rewardpunishments,
            'parents': parents,
            'notices': notices,
            'schedules': schedules
        }
    

# 数据转换工具类
class DataConverter:
    @staticmethod
    def model_to_dict(obj):
        """将模型对象转换为字典"""
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif isinstance(obj, list):
            return [DataConverter.model_to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: DataConverter.model_to_dict(value) for key, value in obj.items()}
        else:
            return obj
    
    @staticmethod
    def dict_to_model(data_dict, model_class):
        """将字典转换为模型对象"""
        if isinstance(data_dict, list):
            return [DataConverter.dict_to_model(item, model_class) for item in data_dict]
        elif isinstance(data_dict, dict):
            return model_class(**data_dict)
        else:
            return data_dict

# 数据验证类
class Validator:
    @staticmethod
    def validate_student_data(data):
        """验证学生数据"""
        required_fields = ['name', 'gender', 'age', 'student_id']
        for field in required_fields:
            if not data.get(field):
                return False, f'{field}为必填项'
        
        if not isinstance(data.get('age'), int) or data['age'] <= 0:
            return False, '年龄必须为正整数'
        
        return True, '验证通过'
    
    @staticmethod
    def validate_course_data(data):
        """验证课程数据"""
        required_fields = ['name', 'credits']
        for field in required_fields:
            if not data.get(field):
                return False, f'{field}为必填项'
        
        if not isinstance(data.get('credits'), int) or data['credits'] <= 0:
            return False, '学分必须为正整数'
        
        return True, '验证通过'
    
    @staticmethod
    def validate_user_data(data):
        """验证用户数据"""
        required_fields = ['username', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return False, f'{field}为必填项'
        
        if data.get('role') == 'student' and not data.get('student_info_id'):
            return False, '学生角色必须关联学生信息'
        
        return True, '验证通过'

# 查询条件类
class QueryCondition:
    def __init__(self, field=None, value=None, operator='eq'):
        self.field = field
        self.value = value
        self.operator = operator  # eq, ne, gt, lt, contains等
    
    def matches(self, item_dict):
        """检查字典是否满足查询条件"""
        if not self.field or self.value is None:
            return True
        
        item_value = item_dict.get(self.field)
        
        if self.operator == 'eq':
            return item_value == self.value
        elif self.operator == 'ne':
            return item_value != self.value
        elif self.operator == 'gt':
            return item_value > self.value
        elif self.operator == 'lt':
            return item_value < self.value
        elif self.operator == 'contains':
            return self.value.lower() in str(item_value).lower()
        
        return False

class QueryBuilder:
    def __init__(self):
        self.conditions = []
    
    def where(self, field, value, operator='eq'):
        self.conditions.append(QueryCondition(field, value, operator))
        return self
    
    def build(self):
        return self.conditions

# 分页类
class Pagination:
    def __init__(self, items, page, per_page, total):
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = (total + per_page - 1) // per_page
    
    @property
    def has_prev(self):
        return self.page > 1
    
    @property
    def has_next(self):
        return self.page < self.pages
    
    def get_slice(self):
        start = (self.page - 1) * self.per_page
        end = start + self.per_page
        return self.items[start:end]

# 统计数据结构
class Statistics:
    @dataclass
    class GenderStats:
        gender: str
        count: int
    
    @dataclass
    class AttendanceStats:
        date: str
        present_count: int
        absent_count: int
        leave_count: int
    
    @dataclass
    class CourseStats:
        course_name: str
        avg_exam_score: float
        avg_performance_score: float
    
    @dataclass
    class RewardPunishmentStats:
        type: str
        count: int

# 响应结果封装
class Result:
    def __init__(self, success=True, data=None, message='', error=None):
        self.success = success
        self.data = data
        self.message = message
        self.error = error
    
    def to_dict(self):
        return {
            'success': self.success,
            'data': self.data,
            'message': self.message,
            'error': self.error
        }
    
    @classmethod
    def success(cls, data=None, message=''):
        return cls(True, data, message)
    
    @classmethod
    def error(cls, message='', error=None):
        return cls(False, None, message, error)

# 业务异常类
class BusinessException(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.message = message
        self.code = code

class ValidationException(BusinessException):
    def __init__(self, message):
        super().__init__(message, 'VALIDATION_ERROR')

class NotFoundException(BusinessException):
    def __init__(self, message):
        super().__init__(message, 'NOT_FOUND')

class DuplicateException(BusinessException):
    def __init__(self, message):
        super().__init__(message, 'DUPLICATE_ENTRY')
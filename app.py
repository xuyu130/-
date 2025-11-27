
# app.py - 面向对象重构版本

from flask import Flask, render_template, request, redirect, url_for, flash, g, session
from functools import wraps
import functools
import json
import os
from datetime import datetime
from abc import ABC, abstractmethod

# ==================== 配置类 ====================
class Config:
    """应用配置类"""
    SECRET_KEY = 'your-secret-key-here'
    DATA_FILE = 'app_data.json'
    DEFAULT_DATA = {
        'users': [],
        'students': [],
        'courses': [],
        'enrollments': [],
        'schedules': [],
        'attendance': [],
        'rewards_punishments': [],
        'parents': []
    }

# ==================== 数据模型基类 ====================
class BaseModel(ABC):
    """数据模型基类"""
    
    def __init__(self, id=None):
        self.id = id
    
    @abstractmethod
    def to_dict(self):
        """转换为字典"""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        """从字典创建对象"""
        pass
    
    def update(self, data):
        """更新对象属性"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

# ==================== 用户模型 ====================
class User(BaseModel):
    """用户模型"""
    
    ROLE_ADMIN = 'admin'
    ROLE_TEACHER = 'teacher'
    ROLE_STUDENT = 'student'
    
    def __init__(self, id=None, username=None, password=None, role=None, name=None):
        super().__init__(id)
        self.username = username
        self.password = password
        self.role = role
        self.name = name
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'role': self.role,
            'name': self.name
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            username=data.get('username'),
            password=data.get('password'),
            role=data.get('role'),
            name=data.get('name')
        )
    
    def is_admin(self):
        return self.role == self.ROLE_ADMIN
    
    def is_teacher(self):
        return self.role == self.ROLE_TEACHER
    
    def is_student(self):
        return self.role == self.ROLE_STUDENT
    
    def check_password(self, password):
        return self.password == password

# ==================== 学生模型 ====================
class Student(BaseModel):
    """学生模型"""
    
    def __init__(self, id=None, user_id=None, student_number=None, name=None, 
                 gender=None, birth_date=None, class_name=None, enrollment_date=None,
                 contact_phone=None, email=None, address=None):
        super().__init__(id)
        self.user_id = user_id
        self.student_number = student_number
        self.name = name
        self.gender = gender
        self.birth_date = birth_date
        self.class_name = class_name
        self.enrollment_date = enrollment_date
        self.contact_phone = contact_phone
        self.email = email
        self.address = address
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'student_number': self.student_number,
            'name': self.name,
            'gender': self.gender,
            'birth_date': self.birth_date,
            'class_name': self.class_name,
            'enrollment_date': self.enrollment_date,
            'contact_phone': self.contact_phone,
            'email': self.email,
            'address': self.address
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            student_number=data.get('student_number'),
            name=data.get('name'),
            gender=data.get('gender'),
            birth_date=data.get('birth_date'),
            class_name=data.get('class_name'),
            enrollment_date=data.get('enrollment_date'),
            contact_phone=data.get('contact_phone'),
            email=data.get('email'),
            address=data.get('address')
        )

# ==================== 课程模型 ====================
class Course(BaseModel):
    """课程模型"""
    
    def __init__(self, id=None, name=None, description=None, credits=None, capacity=None):
        super().__init__(id)
        self.name = name
        self.description = description
        self.credits = credits
        self.capacity = capacity
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'credits': self.credits,
            'capacity': self.capacity
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description'),
            credits=data.get('credits'),
            capacity=data.get('capacity')
        )

# ==================== 选课记录模型 ====================
class Enrollment(BaseModel):
    """选课记录模型"""
    
    def __init__(self, id=None, student_id=None, course_id=None, 
                 exam_score=None, performance_score=None):
        super().__init__(id)
        self.student_id = student_id
        self.course_id = course_id
        self.exam_score = exam_score
        self.performance_score = performance_score
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'exam_score': self.exam_score,
            'performance_score': self.performance_score
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            student_id=data.get('student_id'),
            course_id=data.get('course_id'),
            exam_score=data.get('exam_score'),
            performance_score=data.get('performance_score')
        )
    
    def get_total_score(self):
        """计算总分"""
        if self.exam_score is not None and self.performance_score is not None:
            return self.exam_score * 0.7 + self.performance_score * 0.3
        return None

# ==================== 课程安排模型 ====================
class Schedule(BaseModel):
    """课程安排模型"""
    
    DAYS_OF_WEEK = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    
    def __init__(self, id=None, course_id=None, teacher_user_id=None, 
                 day_of_week=None, start_time=None, end_time=None,
                 location=None, semester=None):
        super().__init__(id)
        self.course_id = course_id
        self.teacher_user_id = teacher_user_id
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.semester = semester
    
    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'teacher_user_id': self.teacher_user_id,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'location': self.location,
            'semester': self.semester
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            course_id=data.get('course_id'),
            teacher_user_id=data.get('teacher_user_id'),
            day_of_week=data.get('day_of_week'),
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            location=data.get('location'),
            semester=data.get('semester')
        )
    
    def has_time_conflict(self, other):
        """检查与另一个课程安排是否有时间冲突"""
        if self.day_of_week != other.day_of_week:
            return False
        if self.semester != other.semester:
            return False
        # 检查时间重叠
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)

# ==================== 考勤记录模型 ====================
class Attendance(BaseModel):
    """考勤记录模型"""
    
    STATUS_PRESENT = '出勤'
    STATUS_ABSENT = '缺勤'
    STATUS_LATE = '迟到'
    STATUS_LEAVE = '请假'
    
    def __init__(self, id=None, student_id=None, schedule_id=None, 
                 date=None, status=None, remark=None):
        super().__init__(id)
        self.student_id = student_id
        self.schedule_id = schedule_id
        self.date = date
        self.status = status
        self.remark = remark
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'schedule_id': self.schedule_id,
            'date': self.date,
            'status': self.status,
            'remark': self.remark
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            student_id=data.get('student_id'),
            schedule_id=data.get('schedule_id'),
            date=data.get('date'),
            status=data.get('status'),
            remark=data.get('remark')
        )

# ==================== 奖惩记录模型 ====================
class RewardPunishment(BaseModel):
    """奖惩记录模型"""
    
    TYPE_REWARD = '奖励'
    TYPE_PUNISHMENT = '处分'
    
    def __init__(self, id=None, student_id=None, type=None, 
                 description=None, date=None):
        super().__init__(id)
        self.student_id = student_id
        self.type = type
        self.description = description
        self.date = date
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'type': self.type,
            'description': self.description,
            'date': self.date
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            student_id=data.get('student_id'),
            type=data.get('type'),
            description=data.get('description'),
            date=data.get('date')
        )

# ==================== 家长信息模型 ====================
class Parent(BaseModel):
    """家长信息模型"""
    
    def __init__(self, id=None, student_id=None, parent_name=None, 
                 relationship=None, contact_phone=None, email=None):
        super().__init__(id)
        self.student_id = student_id
        self.parent_name = parent_name
        self.relationship = relationship
        self.contact_phone = contact_phone
        self.email = email
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'parent_name': self.parent_name,
            'relationship': self.relationship,
            'contact_phone': self.contact_phone,
            'email': self.email
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            student_id=data.get('student_id'),
            parent_name=data.get('parent_name'),
            relationship=data.get('relationship'),
            contact_phone=data.get('contact_phone'),
            email=data.get('email')
        )

# ==================== 数据仓库基类 ====================
class BaseRepository(ABC):
    """数据仓库基类"""
    
    def __init__(self, data_manager, collection_name, model_class):
        self.data_manager = data_manager
        self.collection_name = collection_name
        self.model_class = model_class
    
    def get_all(self):
        """获取所有记录"""
        items = self.data_manager.get_collection(self.collection_name)
        return [self.model_class.from_dict(item) for item in items]
    
    def get_by_id(self, id):
        """根据ID获取记录"""
        items = self.data_manager.get_collection(self.collection_name)
        for item in items:
            if item.get('id') == id:
                return self.model_class.from_dict(item)
        return None
    
    def add(self, model):
        """添加记录"""
        if model.id is None:
            model.id = self.data_manager.get_next_id(self.collection_name)
        self.data_manager.add_item(self.collection_name, model.to_dict())
        return model
    
    def update(self, model):
        """更新记录"""
        self.data_manager.update_item(self.collection_name, model.id, model.to_dict())
        return model
    
    def delete(self, id):
        """删除记录"""
        self.data_manager.delete_item(self.collection_name, id)
    
    def find_by(self, **kwargs):
        """根据条件查找记录"""
        items = self.data_manager.get_collection(self.collection_name)
        results = []
        for item in items:
            match = True
            for key, value in kwargs.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                results.append(self.model_class.from_dict(item))
        return results
    
    def find_one_by(self, **kwargs):
        """根据条件查找单条记录"""
        results = self.find_by(**kwargs)
        return results[0] if results else None

# ==================== 具体数据仓库 ====================
class UserRepository(BaseRepository):
    """用户数据仓库"""
    
    def __init__(self, data_manager):
        super().__init__(data_manager, 'users', User)
    
    def get_by_username(self, username):
        """根据用户名获取用户"""
        return self.find_one_by(username=username)
    
    def get_teachers(self):
        """获取所有教师"""
        return self.find_by(role=User.ROLE_TEACHER)
    
    def username_exists(self, username, exclude_id=None):
        """检查用户名是否存在"""
        users = self.find_by(username=username)
        if exclude_id:
            users = [u for u in users if u.id != exclude_id]
        return len(users) > 0


class StudentRepository(BaseRepository):
    """学生数据仓库"""
    
    def __init__(self, data_manager):
        super().__init__(data_manager, 'students', Student)
    
    def get_by_user_id(self, user_id):
        """根据用户ID获取学生信息"""
        return self.find_one_by(user_id=user_id)
    
    def get_by_student_number(self, student_number):
        """根据学号获取学生"""
        return self.find_one_by(student_number=student_number)
    
    def student_number_exists(self, student_number, exclude_id=None):
        """检查学号是否存在"""
        students = self.find_by(student_number=student_number)
        if exclude_id:
            students = [s for s in students if s.id != exclude_id]
        return len(students) > 0


class CourseRepository(BaseRepository):
    """课程数据仓库"""
    
    def __init__(self, data_manager):
        super().__init__(data_manager, 'courses', Course)
    
    def name_exists(self, name, exclude_id=None):
        """检查课程名称是否存在"""
        courses = self.find_by(name=name)
        if exclude_id:
            courses = [c for c in courses if c.id != exclude_id]
        return len(courses) > 0


class EnrollmentRepository(BaseRepository):
    """选课记录数据仓库"""
    
    def __init__(self, data_manager):
        super().__init__(data_manager, 'enrollments', Enrollment)
    
    def get_by_student(self, student_id):
        """获取学生的所有选课记录"""
        return self.find_by(student_id=student_id)
    
    def get_by_course(self, course_id):
        """获取课程的所有选课记录"""
        return self.find_by(course_id=course_id)
    
    def get_enrollment(self, student_id, course_id):
        """获取特定学生的特定课程选课记录"""
        return self.find_one_by(student_id=student_id, course_id=course_id)
    
    def is_enrolled(self, student_id, course_id):
        """检查学生是否已选某课程"""
        return self.get_enrollment(student_id, course_id) is not None
    
    def get_course_enrollment_count(self, course_id):
        """获取课程选课人数"""
        return len(self.get_by_course(course_id))
    
    def delete_by_student(self, student_id):
        """删除学生的所有选课记录"""
        enrollments = self.get_by_student(student_id)
        for enrollment in enrollments:
            self.delete(enrollment.id)
    
    def delete_by_course(self, course_id):
        """删除课程的所有选课记录"""
        enrollments = self.get_by_course(course_id)
        for enrollment in enrollments:
            self.delete(enrollment.id)


class ScheduleRepository(BaseRepository):
    """课程安排数据仓库"""
    
    def __init__(self, data_manager):
        super().__init__(data_manager, 'schedules', Schedule)
    
    def get_by_course(self, course_id):
        """获取课程的所有安排"""
        return self.find_by(course_id=course_id)
    
    def get_by_teacher(self, teacher_user_id):
        """获取教师的所有课程安排"""
        return self.find_by(teacher_user_id=teacher_user_id)
    
    def get_by_semester(self, semester):
        """获取学期的所有课程安排"""
        return self.find_by(semester=semester)
    
    def check_conflict(self, schedule, exclude_id=None):
        """检查课程安排冲突"""
        all_schedules = self.get_all()
        for existing in all_schedules:
            if exclude_id and existing.id == exclude_id:
                continue
            if schedule.has_time_conflict(existing):
                # 检查是否是同一教师或同一教室
                if (schedule.teacher_user_id == existing.teacher_user_id or 
                    schedule.location == existing.location):
                    return existing
        return None
    
    def delete_by_course(self, course_id):
        """删除课程的所有安排"""
        schedules = self.get_by_course(course_id)
        for schedule in schedules:
            self.delete(schedule.id)


class AttendanceRepository(BaseRepository):
    """考勤记录数据仓库"""
    
    def __init__(self, data_manager):
        super().__init__(data_manager, 'attendance', Attendance)
    
    def get_by_student(self, student_id):
        """获取学生的所有考勤记录"""
        return self.find_by(student_id=student_id)
    
    def get_by_schedule(self, schedule_id):
        """获取课程安排的所有考勤记录"""
        return self.find_by(schedule_id=schedule_id)
    
    def get_by_date(self, date):
        """获取某日期的所有考勤记录"""
        return self.find_by(date=date)
    
    def delete_by_student(self, student_id):
        """删除学生的所有考勤记录"""
        records = self.get_by_student(student_id)
        for record in records:
            self.delete(record.id)
    
    def delete_by_schedule(self, schedule_id):
        """删除课程安排的所有考勤记录"""
        records = self.get_by_schedule(schedule_id)
        for record in records:
            self.delete(record.id)


class RewardPunishmentRepository(BaseRepository):
    """奖惩记录数据仓库"""
    
    def __init__(self, data_manager):
        super().__init__(data_manager, 'rewards_punishments', RewardPunishment)
    
    def get_by_student(self, student_id):
        """获取学生的所有奖惩记录"""
        return self.find_by(student_id=student_id)
    
    def get_rewards(self, student_id=None):
        """获取奖励记录"""
        if student_id:
            return [r for r in self.get_by_student(student_id) 
                   if r.type == RewardPunishment.TYPE_REWARD]
        return self.find_by(type=RewardPunishment.TYPE_REWARD)
    
    def get_punishments(self, student_id=None):
        """获取处分记录"""
        if student_id:
            return [r for r in self.get_by_student(student_id) 
                   if r.type == RewardPunishment.TYPE_PUNISHMENT]
        return self.find_by(type=RewardPunishment.TYPE_PUNISHMENT)
    
    def delete_by_student(self, student_id):
        """删除学生的所有奖惩记录"""
        records = self.get_by_student(student_id)
        for record in records:
            self.delete(record.id)


class ParentRepository(BaseRepository):
    """家长信息数据仓库"""
    
    def __init__(self, data_manager):
        super().__init__(data_manager, 'parents', Parent)
    
    def get_by_student(self, student_id):
        """获取学生的所有家长信息"""
        return self.find_by(student_id=student_id)
    
    def relationship_exists(self, student_id, relationship, exclude_id=None):
        """检查学生的某种关系是否已存在"""
        parents = [p for p in self.get_by_student(student_id) 
                  if p.relationship == relationship]
        if exclude_id:
            parents = [p for p in parents if p.id != exclude_id]
        return len(parents) > 0
    
    def delete_by_student(self, student_id):
        """删除学生的所有家长信息"""
        parents = self.get_by_student(student_id)
        for parent in parents:
            self.delete(parent.id)

# ==================== 数据管理器 ====================
class DataManager:
    """数据管理器 - 负责数据的持久化和内存管理"""
    
    def __init__(self, data_file):
        self.data_file = data_file
        self.data = None
        self.modified = False
    
    def load(self):
        """从文件加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.data = Config.DEFAULT_DATA.copy()
        else:
            self.data = Config.DEFAULT_DATA.copy()
        
        # 确保所有集合都存在
        for key in Config.DEFAULT_DATA.keys():
            if key not in self.data:
                self.data[key] = []
        
        return self.data
    
    def save(self):
        """保存数据到文件"""
        if self.data is not None:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            self.modified = False
    
    def get_collection(self, name):
        """获取集合"""
        if self.data is None:
            self.load()
        return self.data.get(name, [])
    
    def get_next_id(self, collection_name):
        """获取下一个ID"""
        collection = self.get_collection(collection_name)
        if not collection:
            return 1
        return max(item.get('id', 0) for item in collection) + 1
    
    def add_item(self, collection_name, item):
        """添加项目到集合"""
        if self.data is None:
            self.load()
        self.data[collection_name].append(item)
        self.modified = True
    
    def update_item(self, collection_name, id, item):
        """更新集合中的项目"""
        if self.data is None:
            self.load()
        collection = self.data[collection_name]
        for i, existing in enumerate(collection):
            if existing.get('id') == id:
                collection[i] = item
                self.modified = True
                return True
        return False
    
    def delete_item(self, collection_name, id):
        """从集合中删除项目"""
        if self.data is None:
            self.load()
        self.data[collection_name] = [
            item for item in self.data[collection_name] 
            if item.get('id') != id
        ]
        self.modified = True
    
    def mark_modified(self):
        """标记数据已修改"""
        self.modified = True
    
    def is_modified(self):
        """检查数据是否已修改"""
        return self.modified

# ==================== 服务层基类 ====================
class BaseService(ABC):
    """服务层基类"""
    
    def __init__(self, repository):
        self.repository = repository

# ==================== 认证服务 ====================
class AuthService(BaseService):
    """认证服务"""
    
    def __init__(self, user_repository, student_repository):
        self.user_repo = user_repository
        self.student_repo = student_repository
    
    def login(self, username, password):
        """用户登录"""
        user = self.user_repo.get_by_username(username)
        if user and user.check_password(password):
            return user
        return None
    
    def register(self, username, password, role, name):
        """用户注册"""
        if self.user_repo.username_exists(username):
            return None, "用户名已存在"
        
        user = User(
            username=username,
            password=password,
            role=role,
            name=name
        )
        user = self.user_repo.add(user)
        return user, None
    
    def get_current_user(self, session):
        """获取当前登录用户"""
        user_id = session.get('user_id')
        if user_id:
            return self.user_repo.get_by_id(user_id)
        return None
    
    def get_current_student_info(self, session):
        """获取当前登录用户的学生信息"""
        user = self.get_current_user(session)
        if user and user.is_student():
            return self.student_repo.get_by_user_id(user.id)
        return None

# ==================== 学生服务 ====================
class StudentService(BaseService):
    """学生服务"""
    
    def __init__(self, student_repository, user_repository, enrollment_repository,
                 attendance_repository, reward_punishment_repository, parent_repository):
        self.student_repo = student_repository
        self.user_repo = user_repository
        self.enrollment_repo = enrollment_repository
        self.attendance_repo = attendance_repository
        self.rp_repo = reward_punishment_repository
        self.parent_repo = parent_repository
    
    def get_all_students(self):
        """获取所有学生"""
        return self.student_repo.get_all()
    
    def get_student_by_id(self, id):
        """根据ID获取学生"""
        return self.student_repo.get_by_id(id)
    
    def create_student(self, student_data, user_data=None):
        """创建学生"""
        # 检查学号唯一性
        if self.student_repo.student_number_exists(student_data.get('student_number')):
            return None, "学号已存在"
        
        # 如果需要同时创建用户
        user_id = student_data.get('user_id')
        if user_data and not user_id:
            if self.user_repo.username_exists(user_data.get('username')):
                return None, "用户名已存在"
            user = User(
                username=user_data.get('username'),
                password=user_data.get('password', '123456'),
                role=User.ROLE_STUDENT,
                name=student_data.get('name')
            )
            user = self.user_repo.add(user)
            user_id = user.id
        
        student = Student(
            user_id=user_id,
            student_number=student_data.get('student_number'),
            name=student_data.get('name'),
            gender=student_data.get('gender'),
            birth_date=student_data.get('birth_date'),
            class_name=student_data.get('class_name'),
            enrollment_date=student_data.get('enrollment_date'),
            contact_phone=student_data.get('contact_phone'),
            email=student_data.get('email'),
            address=student_data.get('address')
        )
        student = self.student_repo.add(student)
        return student, None
    
    def update_student(self, id, student_data):
        """更新学生信息"""
        student = self.student_repo.get_by_id(id)
        if not student:
            return None, "学生不存在"
        
        # 检查学号唯一性（排除当前学生）
        if self.student_repo.student_number_exists(
            student_data.get('student_number'), exclude_id=id):
            return None, "学号已存在"
        
        student.update(student_data)
        student = self.student_repo.update(student)
        return student, None
    
    def delete_student(self, id):
        """删除学生（级联删除相关记录）"""
        student = self.student_repo.get_by_id(id)
        if not student:
            return False, "学生不存在"
        
        # 级联删除
        self.enrollment_repo.delete_by_student(id)
        self.attendance_repo.delete_by_student(id)
        self.rp_repo.delete_by_student(id)
        self.parent_repo.delete_by_student(id)
        
        # 删除关联的用户账号
        if student.user_id:
            self.user_repo.delete(student.user_id)
        
        self.student_repo.delete(id)
        return True, None
    
    def get_student_with_details(self, id):
        """获取学生详细信息（包含关联数据）"""
        student = self.student_repo.get_by_id(id)
        if not student:
            return None
        
        return {
            'student': student,
            'enrollments': self.enrollment_repo.get_by_student(id),
            'attendance': self.attendance_repo.get_by_student(id),
            'rewards_punishments': self.rp_repo.get_by_student(id),
            'parents': self.parent_repo.get_by_student(id)
        }

# ==================== 课程服务 ====================
class CourseService(BaseService):
    """课程服务"""
    
    def __init__(self, course_repository, enrollment_repository, schedule_repository):
        self.course_repo = course_repository
        self.enrollment_repo = enrollment_repository
        self.schedule_repo = schedule_repository
    
    def get_all_courses(self):
        """获取所有课程"""
        return self.course_repo.get_all()
    
    def get_course_by_id(self, id):
        """根据ID获取课程"""
        return self.course_repo.get_by_id(id)
    
    def create_course(self, course_data):
        """创建课程"""
        if self.course_repo.name_exists(course_data.get('name')):
            return None, "课程名称已存在"
        
        course = Course(
            name=course_data.get('name'),
            description=course_data.get('description'),
            credits=int(course_data.get('credits')),
            capacity=int(course_data.get('capacity')) if course_data.get('capacity') else None
        )
        course = self.course_repo.add(course)
        return course, None
    
    def update_course(self, id, course_data):
        """更新课程"""
        course = self.course_repo.get_by_id(id)
        if not course:
            return None, "课程不存在"
        
        if self.course_repo.name_exists(course_data.get('name'), exclude_id=id):
            return None, "课程名称已存在"
        
        course.name = course_data.get('name')
        course.description = course_data.get('description')
        course.credits = int(course_data.get('credits'))
        course.capacity = int(course_data.get('capacity')) if course_data.get('capacity') else None
        
        course = self.course_repo.update(course)
        return course, None
    
    def delete_course(self, id):
        """删除课程（级联删除相关记录）"""
        course = self.course_repo.get_by_id(id)
        if not course:
            return False, "课程不存在"
        
        # 级联删除
        self.enrollment_repo.delete_by_course(id)
        self.schedule_repo.delete_by_course(id)
        
        self.course_repo.delete(id)
        return True, None
    
    def get_course_enrollment_count(self, course_id):
        """获取课程选课人数"""
        return self.enrollment_repo.get_course_enrollment_count(course_id)
    
    def is_course_full(self, course_id):
        """检查课程是否已满"""
        course = self.course_repo.get_by_id(course_id)
        if not course or course.capacity is None:
            return False
        return self.get_course_enrollment_count(course_id) >= course.capacity

# ==================== 选课服务 ====================
class EnrollmentService(BaseService):
    """选课服务"""
    
    def __init__(self, enrollment_repository, course_repository, student_repository):
        self.enrollment_repo = enrollment_repository
        self.course_repo = course_repository
        self.student_repo = student_repository
    
    def enroll_course(self, student_id, course_id):
        """选课"""
        # 检查学生是否存在
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return None, "学生不存在"
        
        # 检查课程是否存在
        course = self.course_repo.get_by_id(course_id)
        if not course:
            return None, "课程不存在"
        
        # 检查是否已选
        if self.enrollment_repo.is_enrolled(student_id, course_id):
            return None, "已经选修该课程"
        
        # 检查课程容量
        if course.capacity:
            current_count = self.enrollment_repo.get_course_enrollment_count(course_id)
            if current_count >= course.capacity:
                return None, "课程已满"
        
        enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id
        )
        enrollment = self.enrollment_repo.add(enrollment)
        return enrollment, None
    
    def unenroll_course(self, student_id, course_id):
        """退课"""
        enrollment = self.enrollment_repo.get_enrollment(student_id, course_id)
        if not enrollment:
            return False, "未选修该课程"
        
        self.enrollment_repo.delete(enrollment.id)
        return True, None
    
    def update_scores(self, enrollment_id, exam_score, performance_score):
        """更新成绩"""
        enrollment = self.enrollment_repo.get_by_id(enrollment_id)
        if not enrollment:
            return None, "选课记录不存在"
        
        enrollment.exam_score = float(exam_score) if exam_score else None
        enrollment.performance_score = float(performance_score) if performance_score else None
        
        enrollment = self.enrollment_repo.update(enrollment)
        return enrollment, None
    
    def get_student_enrollments(self, student_id):
        """获取学生的选课列表"""
        return self.enrollment_repo.get_by_student(student_id)
    
    def get_course_enrollments(self, course_id):
        """获取课程的选课学生列表"""
        return self.enrollment_repo.get_by_course(course_id)

# ==================== 排课服务 ====================
class ScheduleService(BaseService):
    """排课服务"""
    
    def __init__(self, schedule_repository, course_repository, user_repository,
                 attendance_repository):
        self.schedule_repo = schedule_repository
        self.course_repo = course_repository
        self.user_repo = user_repository
        self.attendance_repo = attendance_repository
    
    def get_all_schedules(self):
        """获取所有课程安排"""
        return self.schedule_repo.get_all()
    
    def get_schedule_by_id(self, id):
        """根据ID获取课程安排"""
        return self.schedule_repo.get_by_id(id)
    
    def create_schedule(self, schedule_data):
        """创建课程安排"""
        # 验证时间
        if schedule_data.get('start_time') >= schedule_data.get('end_time'):
            return None, "开始时间必须早于结束时间"
        
        schedule = Schedule(
            course_id=int(schedule_data.get('course_id')),
            teacher_user_id=int(schedule_data.get('teacher_user_id')),
            day_of_week=schedule_data.get('day_of_week'),
            start_time=schedule_data.get('start_time'),
            end_time=schedule_data.get('end_time'),
            location=schedule_data.get('location'),
            semester=schedule_data.get('semester')
        )
        
        # 检查课程是否存在
        course = self.course_repo.get_by_id(schedule.course_id)
        if not course:
            return None, "课程不存在"
        
        # 检查教师是否存在
        teacher = self.user_repo.get_by_id(schedule.teacher_user_id)
        if not teacher or not teacher.is_teacher():
            return None, "教师不存在或角色不正确"
        
        # 检查时间冲突
        conflict = self.schedule_repo.check_conflict(schedule)
        if conflict:
            return None, f"时间冲突：与{conflict.day_of_week} {conflict.start_time}-{conflict.end_time}的课程冲突"
        
        schedule = self.schedule_repo.add(schedule)
        return schedule, None
    
    def update_schedule(self, id, schedule_data):
        """更新课程安排"""
        schedule = self.schedule_repo.get_by_id(id)
        if not schedule:
            return None, "课程安排不存在"
        
        # 验证时间
        if schedule_data.get('start_time') >= schedule_data.get('end_time'):
            return None, "开始时间必须早于结束时间"
        
        # 检查教师是否存在
        teacher_id = int(schedule_data.get('teacher_user_id'))
        teacher = self.user_repo.get_by_id(teacher_id)
        if not teacher or not teacher.is_teacher():
            return None, "教师不存在或角色不正确"
        
        # 更新属性
        schedule.course_id = int(schedule_data.get('course_id'))
        schedule.teacher_user_id = teacher_id
        schedule.day_of_week = schedule_data.get('day_of_week')
        schedule.start_time = schedule_data.get('start_time')
        schedule.end_time = schedule_data.get('end_time')
        schedule.location = schedule_data.get('location')
        schedule.semester = schedule_data.get('semester')
        
        # 检查时间冲突（排除自身）
        conflict = self.schedule_repo.check_conflict(schedule, exclude_id=id)
        if conflict:
            return None, f"时间冲突：与{conflict.day_of_week} {conflict.start_time}-{conflict.end_time}的课程冲突"
        
        schedule = self.schedule_repo.update(schedule)
        return schedule, None
    
    def delete_schedule(self, id):
        """删除课程安排（级联删除考勤记录）"""
        schedule = self.schedule_repo.get_by_id(id)
        if not schedule:
            return False, "课程安排不存在"
        
        # 级联删除考勤记录
        self.attendance_repo.delete_by_schedule(id)
        
        self.schedule_repo.delete(id)
        return True, None


# ==================== 考勤服务 ====================
class AttendanceService(BaseService):
    """考勤服务"""
    
    def __init__(self, attendance_repository, student_repository, schedule_repository):
        self.attendance_repo = attendance_repository
        self.student_repo = student_repository
        self.schedule_repo = schedule_repository
    
    def record_attendance(self, attendance_data):
        """记录考勤"""
        student_id = int(attendance_data.get('student_id'))
        schedule_id = int(attendance_data.get('schedule_id'))
        
        # 检查学生是否存在
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return None, "学生不存在"
        
        # 检查课程安排是否存在
        schedule = self.schedule_repo.get_by_id(schedule_id)
        if not schedule:
            return None, "课程安排不存在"
        
        # 检查是否已记录
        existing = self.attendance_repo.find_one_by(
            student_id=student_id,
            schedule_id=schedule_id,
            date=attendance_data.get('date')
        )
        if existing:
            return None, "该课程的考勤已记录"
        
        attendance = Attendance(
            student_id=student_id,
            schedule_id=schedule_id,
            date=attendance_data.get('date'),
            status=attendance_data.get('status'),
            remark=attendance_data.get('remark')
        )
        attendance = self.attendance_repo.add(attendance)
        return attendance, None
    
    def update_attendance(self, id, attendance_data):
        """更新考勤记录"""
        attendance = self.attendance_repo.get_by_id(id)
        if not attendance:
            return None, "考勤记录不存在"
        
        attendance.status = attendance_data.get('status')
        attendance.remark = attendance_data.get('remark')
        
        attendance = self.attendance_repo.update(attendance)
        return attendance, None
    
    def get_student_attendance(self, student_id, date=None):
        """获取学生考勤记录（可按日期筛选）"""
        records = self.attendance_repo.get_by_student(student_id)
        if date:
            records = [r for r in records if r.date == date]
        return records
    
    def get_schedule_attendance(self, schedule_id):
        """获取课程安排的考勤记录"""
        return self.attendance_repo.get_by_schedule(schedule_id)


# ==================== 奖惩服务 ====================
class RewardPunishmentService(BaseService):
    """奖惩服务"""
    
    def __init__(self, rp_repository, student_repository):
        self.rp_repo = rp_repository
        self.student_repo = student_repository
    
    def create_record(self, rp_data):
        """创建奖惩记录"""
        student_id = int(rp_data.get('student_id'))
        
        # 检查学生是否存在
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return None, "学生不存在"
        
        record = RewardPunishment(
            student_id=student_id,
            type=rp_data.get('type'),
            description=rp_data.get('description'),
            date=rp_data.get('date')
        )
        record = self.rp_repo.add(record)
        return record, None
    
    def update_record(self, id, rp_data):
        """更新奖惩记录"""
        record = self.rp_repo.get_by_id(id)
        if not record:
            return None, "奖惩记录不存在"
        
        record.type = rp_data.get('type')
        record.description = rp_data.get('description')
        record.date = rp_data.get('date')
        
        record = self.rp_repo.update(record)
        return record, None
    
    def delete_record(self, id):
        """删除奖惩记录"""
        record = self.rp_repo.get_by_id(id)
        if not record:
            return False, "奖惩记录不存在"
        
        self.rp_repo.delete(id)
        return True, None


# ==================== 家长服务 ====================
class ParentService(BaseService):
    """家长服务"""
    
    def __init__(self, parent_repository, student_repository):
        self.parent_repo = parent_repository
        self.student_repo = student_repository
    
    def add_parent(self, parent_data):
        """添加家长信息"""
        student_id = int(parent_data.get('student_id'))
        
        # 检查学生是否存在
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return None, "学生不存在"
        
        # 检查关系是否已存在
        if self.parent_repo.relationship_exists(
            student_id, parent_data.get('relationship')):
            return None, "该学生的此关系家长已存在"
        
        parent = Parent(
            student_id=student_id,
            parent_name=parent_data.get('parent_name'),
            relationship=parent_data.get('relationship'),
            contact_phone=parent_data.get('contact_phone'),
            email=parent_data.get('email')
        )
        parent = self.parent_repo.add(parent)
        return parent, None
    
    def update_parent(self, id, parent_data):
        """更新家长信息"""
        parent = self.parent_repo.get_by_id(id)
        if not parent:
            return None, "家长信息不存在"
        
        # 检查关系是否已存在（排除自身）
        if self.parent_repo.relationship_exists(
            parent.student_id, parent_data.get('relationship'), exclude_id=id):
            return None, "该学生的此关系家长已存在"
        
        parent.parent_name = parent_data.get('parent_name')
        parent.relationship = parent_data.get('relationship')
        parent.contact_phone = parent_data.get('contact_phone')
        parent.email = parent_data.get('email')
        
        parent = self.parent_repo.update(parent)
        return parent, None
    
    def delete_parent(self, id):
        """删除家长信息"""
        parent = self.parent_repo.get_by_id(id)
        if not parent:
            return False, "家长信息不存在"
        
        self.parent_repo.delete(id)
        return True, None


# ==================== Flask 应用初始化 ====================
class StudentManagementApp:
    """学生管理系统应用"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config.from_object(Config)
        
        # 初始化数据管理器
        self.data_manager = DataManager(self.app.config['DATA_FILE'])
        self.data_manager.load()
        
        # 初始化仓库
        self.user_repo = UserRepository(self.data_manager)
        self.student_repo = StudentRepository(self.data_manager)
        self.course_repo = CourseRepository(self.data_manager)
        self.enrollment_repo = EnrollmentRepository(self.data_manager)
        self.schedule_repo = ScheduleRepository(self.data_manager)
        self.attendance_repo = AttendanceRepository(self.data_manager)
        self.rp_repo = RewardPunishmentRepository(self.data_manager)
        self.parent_repo = ParentRepository(self.data_manager)
        
        # 初始化服务
        self.auth_service = AuthService(self.user_repo, self.student_repo)
        self.student_service = StudentService(
            self.student_repo, self.user_repo, self.enrollment_repo,
            self.attendance_repo, self.rp_repo, self.parent_repo
        )
        self.course_service = CourseService(
            self.course_repo, self.enrollment_repo, self.schedule_repo
        )
        self.enrollment_service = EnrollmentService(
            self.enrollment_repo, self.course_repo, self.student_repo
        )
        self.schedule_service = ScheduleService(
            self.schedule_repo, self.course_repo, self.user_repo, self.attendance_repo
        )
        self.attendance_service = AttendanceService(
            self.attendance_repo, self.student_repo, self.schedule_repo
        )
        self.rp_service = RewardPunishmentService(
            self.rp_repo, self.student_repo
        )
        self.parent_service = ParentService(
            self.parent_repo, self.student_repo
        )
        
        # 初始化默认数据
        self.init_default_data()
        
        # 注册请求钩子
        self.register_hooks()
        
        # 注册路由
        self.register_routes()
    
    def init_default_data(self):
        """初始化默认数据"""
        if not self.user_repo.get_all():
            # 添加默认管理员
            admin = User(
                username='admin',
                password='admin123',  # 实际应用中应使用加密存储
                role=User.ROLE_ADMIN,
                name='系统管理员'
            )
            self.user_repo.add(admin)
            
            # 添加默认教师
            teacher = User(
                username='teacher',
                password='teacher123',
                role=User.ROLE_TEACHER,
                name='李老师'
            )
            self.user_repo.add(teacher)
            
            # 添加默认学生用户
            student_user = User(
                username='student',
                password='student123',
                role=User.ROLE_STUDENT,
                name='张三'
            )
            student_user = self.user_repo.add(student_user)
            
            # 添加默认学生信息
            self.student_service.create_student({
                'student_number': 'S001',
                'name': '张三',
                'gender': '男',
                'class_name': '三年二班',
                'user_id': student_user.id
            })
            
            # 添加默认课程
            self.course_service.create_course({
                'name': '数学',
                'description': '基础数学课程',
                'credits': 3,
                'capacity': 50
            })
            
            self.data_manager.save()
            print("默认数据初始化完成")
    
    def register_hooks(self):
        """注册请求钩子"""
        @self.app.before_request
        def before_request():
            # 每次请求前标记数据未修改
            self.data_manager.modified = False
        
        @self.app.after_request
        def after_request(response):
            # 请求结束后如果数据被修改则保存
            if self.data_manager.modified:
                self.data_manager.save()
            return response
    
    def register_routes(self):
        """注册路由"""
        app = self.app
        
        # 登录装饰器
        def login_required(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                if 'user_id' not in session:
                    flash('请先登录', 'warning')
                    return redirect(url_for('login', next=request.url))
                return f(*args, **kwargs)
            return decorated_function
        
        # 角色检查装饰器
        def role_required(roles):
            def decorator(f):
                @functools.wraps(f)
                def decorated_function(*args, **kwargs):
                    user = self.auth_service.get_current_user(session)
                    if not user or user.role not in roles:
                        flash('没有访问权限', 'danger')
                        return redirect(url_for('index'))
                    return f(*args, **kwargs)
                return decorated_function
            return decorator
        
        # 首页/登录页
        @app.route('/')
        def index():
            if 'user_id' in session:
                user = self.auth_service.get_current_user(session)
                student_count = len(self.student_service.get_all_students())
                course_count = len(self.course_service.get_all_courses())
                return render_template('index.html', 
                                      user=user,
                                      student_count=student_count,
                                      course_count=course_count)
            return redirect(url_for('login'))
        
        @app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                user = self.auth_service.login(username, password)
                if user:
                    session['user_id'] = user.id
                    session['role'] = user.role
                    flash('登录成功', 'success')
                    return redirect(url_for('index'))
                flash('用户名或密码错误', 'danger')
            return render_template('login.html')
        
        @app.route('/logout')
        def logout():
            session.pop('user_id', None)
            session.pop('role', None)
            flash('已成功退出登录', 'info')
            return redirect(url_for('login'))
        
        # 学生管理路由
        @app.route('/students')
        @login_required
        def students():
            user = self.auth_service.get_current_user(session)
            students = self.student_service.get_all_students()
            return render_template('students.html', 
                                  user=user, 
                                  students=students)
        
        @app.route('/students/add', methods=['POST'])
        @login_required
        @role_required(['admin', 'teacher'])
        def add_student():
            student_data = {
                'name': request.form.get('name'),
                'gender': request.form.get('gender'),
                'student_number': request.form.get('student_id'),
                'age': request.form.get('age'),
                'class_name': request.form.get('class_name'),
                'contact_phone': request.form.get('contact_phone'),
                'family_info': request.form.get('family_info'),
                'homeroom_teacher': request.form.get('homeroom_teacher')
            }
            
            student, error = self.student_service.create_student(student_data)
            if error:
                flash(error, 'danger')
            else:
                flash('学生添加成功', 'success')
            return redirect(url_for('students'))
        
        # 其他路由省略...（课程、选课、考勤等）
    
    def run(self, **kwargs):
        """运行应用"""
        self.app.run(** kwargs)


# 启动应用
if __name__ == '__main__':
    app = StudentManagementApp()
    app.run(debug=True)
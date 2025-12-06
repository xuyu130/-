# repositories.py
import json
import os
import threading
from typing import List, Dict, Any, Optional, Type, TypeVar, Generic
from models import *

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """基础仓储类，提供通用CRUD操作"""
    
    def __init__(self, data_file: str = 'app_data.json'):
        self.data_file = data_file
        self.data = self._load_data()
        self.table_name = self.__class__.__name__.replace('Repository', '').lower() + 's'
        self._lock = threading.Lock()

        # When users manually edit the JSON, keep next_id consistent with existing records.
        self._ensure_table_exists()
        self._sync_next_id()
    
    def _load_data(self) -> Dict[str, Any]:
        """从JSON文件加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                print(f"Error loading data from {self.data_file}: {e}")
                return {'in_memory_data': {}, 'next_id': {}}
        return {'in_memory_data': {}, 'next_id': {}}

    def _sync_next_id(self):
        """Ensure next_id is at least max existing id + 1 after manual edits."""
        in_memory = self.data.get('in_memory_data', {})
        table_data = in_memory.get(self.table_name, [])
        max_id = max((item.get('id', 0) for item in table_data), default=0)

        current_next = self.data.get('next_id', {}).get(self.table_name, 1)
        # If manual additions use higher IDs, bump next_id forward.
        if max_id >= current_next:
            self.data.setdefault('next_id', {})[self.table_name] = max_id + 1
    
    def save_data(self):
        """保存数据到JSON文件 - 简洁版本"""
        with self._lock:
            try:
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=4)
                
                # 验证保存
                if os.path.exists(self.data_file):
                    file_size = os.path.getsize(self.data_file)
                    print(f"✅ 数据已保存到 {self.data_file} ({file_size} bytes)")
                    return True
                else:
                    print(f"❌ 保存失败: {self.data_file} 不存在")
                    return False
                
            except Exception as e:
                print(f"❌ 保存数据时发生错误: {e}")
                
                return False
    
    def get_next_id(self) -> int:
        """获取下一个ID"""
        with self._lock:
            next_id = self.data['next_id'].get(self.table_name, 1)
            self.data['next_id'][self.table_name] = next_id + 1
            return next_id
    
    def _ensure_table_exists(self):
        """确保数据表存在"""
        if 'in_memory_data' not in self.data:
            self.data['in_memory_data'] = {}
        if 'next_id' not in self.data:
            self.data['next_id'] = {}
        if self.table_name not in self.data['in_memory_data']:
            self.data['in_memory_data'][self.table_name] = []
    
    def get_all(self) -> List[T]:
        """获取所有记录"""
        self._ensure_table_exists()
        items = []
        for item_dict in self.data['in_memory_data'][self.table_name]:
            try:
                items.append(self._dict_to_model(item_dict))
            except Exception as e:
                print(f"Error converting dict to model: {e}")
        return items
    
    def get_by_id(self, item_id: int) -> Optional[T]:
        """根据ID获取记录"""
        self._ensure_table_exists()
        for item_dict in self.data['in_memory_data'][self.table_name]:
            if item_dict.get('id') == item_id:
                return self._dict_to_model(item_dict)
        return None
    
    def find(self, **filters) -> List[T]:
        """根据条件查找记录"""
        self._ensure_table_exists()
        results = []
        for item_dict in self.data['in_memory_data'][self.table_name]:
            match = True
            for key, value in filters.items():
                if item_dict.get(key) != value:
                    match = False
                    break
            if match:
                results.append(self._dict_to_model(item_dict))
        return results
    
    def find_one(self, **filters) -> Optional[T]:
        """根据条件查找单个记录"""
        results = self.find(**filters)
        return results[0] if results else None
    
    def create(self, item: T) -> T:
        """创建新记录"""
        with self._lock:
            self._ensure_table_exists()
            item_dict = self._model_to_dict(item)
            self.data['in_memory_data'][self.table_name].append(item_dict)
            return item
    
    def update(self, item_id: int, **kwargs) -> Optional[T]:
        """更新记录"""
        with self._lock:
            self._ensure_table_exists()
            for item_dict in self.data['in_memory_data'][self.table_name]:
                if item_dict.get('id') == item_id:
                    item_dict.update(kwargs)
                    return self._dict_to_model(item_dict)
            return None
    
    def delete(self, item_id: int) -> bool:
        """删除记录"""
        with self._lock:
            self._ensure_table_exists()
            original_len = len(self.data['in_memory_data'][self.table_name])
            self.data['in_memory_data'][self.table_name] = [
                item for item in self.data['in_memory_data'][self.table_name] 
                if item.get('id') != item_id
            ]
            return len(self.data['in_memory_data'][self.table_name]) < original_len
    
    def count(self) -> int:
        """获取记录数量"""
        self._ensure_table_exists()
        return len(self.data['in_memory_data'][self.table_name])
    
    def _model_to_dict(self, item: T) -> Dict[str, Any]:
        """模型对象转字典"""
        if hasattr(item, 'to_dict'):
            return item.to_dict()
        return item.__dict__
    
    def _dict_to_model(self, item_dict: Dict[str, Any]) -> T:
        """字典转模型对象"""
        # 这个方法需要在子类中重写
        raise NotImplementedError("Subclasses must implement _dict_to_model")

class UserRepository(BaseRepository[User]):
    """用户仓储类"""
    
    def _dict_to_model(self, item_dict: Dict[str, Any]) -> User:
        return User(**item_dict)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.find_one(username=username)
    
    def get_users_by_role(self, role: str) -> List[User]:
        """根据角色获取用户列表"""
        return self.find(role=role)
    
    def get_student_users(self) -> List[User]:
        """获取所有学生用户"""
        return self.find(role='student')
    
    def get_teacher_users(self) -> List[User]:
        """获取所有教师用户"""
        return self.find(role='teacher')

class StudentRepository(BaseRepository[Student]):
    """学生仓储类"""
    
    def _dict_to_model(self, item_dict: Dict[str, Any]) -> Student:
        return Student(**item_dict)
    
    def get_by_student_id(self, student_id: str) -> Optional[Student]:
        """根据学号获取学生"""
        return self.find_one(student_id=student_id)
    
    def get_by_class(self, class_name: str) -> List[Student]:
        """根据班级获取学生列表"""
        return self.find(class_name=class_name)
    
    def get_by_gender(self, gender: str) -> List[Student]:
        """根据性别获取学生列表"""
        return self.find(gender=gender)
    
    def search(self, keyword: str) -> List[Student]:
        """搜索学生（姓名或学号）"""
        self._ensure_table_exists()
        results = []
        for item_dict in self.data['in_memory_data'][self.table_name]:
            if (keyword.lower() in item_dict.get('name', '').lower() or 
                keyword.lower() in item_dict.get('student_id', '').lower()):
                results.append(self._dict_to_model(item_dict))
        return results

class CourseRepository(BaseRepository[Course]):
    """课程仓储类"""
    
    def _dict_to_model(self, item_dict: Dict[str, Any]) -> Course:
        return Course(**item_dict)
    
    def get_by_name(self, name: str) -> Optional[Course]:
        """根据课程名称获取课程"""
        return self.find_one(name=name)
    
    def get_available_courses(self) -> List[Course]:
        """获取所有可用课程（有容量或无限容量）"""
        courses = self.get_all()
        return [course for course in courses if course.capacity is None or course.capacity > 0]
    
    def search(self, keyword: str) -> List[Course]:
        """搜索课程（名称或描述）"""
        self._ensure_table_exists()
        results = []
        for item_dict in self.data['in_memory_data'][self.table_name]:
            if (keyword.lower() in item_dict.get('name', '').lower() or 
                keyword.lower() in item_dict.get('description', '').lower()):
                results.append(self._dict_to_model(item_dict))
        return results

class EnrollmentRepository(BaseRepository[Enrollment]):
    """选课记录仓储类"""
    
    def _dict_to_model(self, item_dict: Dict[str, Any]) -> Enrollment:
        return Enrollment(**item_dict)
    
    def get_by_student_id(self, student_id: int) -> List[Enrollment]:
        """根据学生ID获取选课记录"""
        return self.find(student_id=student_id)
    
    def get_by_course_id(self, course_id: int) -> List[Enrollment]:
        """根据课程ID获取选课记录"""
        return self.find(course_id=course_id)
    
    def get_enrollment(self, student_id: int, course_id: int) -> Optional[Enrollment]:
        """获取特定学生和课程的选课记录"""
        return self.find_one(student_id=student_id, course_id=course_id)
    
    def get_students_in_course(self, course_id: int) -> List[int]:
        """获取选修某课程的所有学生ID"""
        enrollments = self.get_by_course_id(course_id)
        return [enrollment.student_id for enrollment in enrollments]
    
    def get_courses_for_student(self, student_id: int) -> List[int]:
        """获取学生选修的所有课程ID"""
        enrollments = self.get_by_student_id(student_id)
        return [enrollment.course_id for enrollment in enrollments]
    
    def get_enrollment_count(self, course_id: int) -> int:
        """获取课程的选课人数"""
        return len(self.get_by_course_id(course_id))
    
    def delete_by_student_id(self, student_id: int):
        """删除学生的所有选课记录"""
        self._ensure_table_exists()
        self.data['in_memory_data'][self.table_name] = [
            item for item in self.data['in_memory_data'][self.table_name] 
            if item.get('student_id') != student_id
        ]
    
    def delete_by_course_id(self, course_id: int):
        """删除课程的所有选课记录"""
        self._ensure_table_exists()
        self.data['in_memory_data'][self.table_name] = [
            item for item in self.data['in_memory_data'][self.table_name] 
            if item.get('course_id') != course_id
        ]

class AttendanceRepository(BaseRepository[Attendance]):
    """考勤记录仓储类"""
    
    def _dict_to_model(self, item_dict: Dict[str, Any]) -> Attendance:
        return Attendance(**item_dict)
    
    def get_by_student_id(self, student_id: int) -> List[Attendance]:
        """根据学生ID获取考勤记录"""
        return self.find(student_id=student_id)
    
    def get_by_date(self, date: str) -> List[Attendance]:
        """根据日期获取考勤记录"""
        return self.find(date=date)
    
    def get_by_student_and_date(self, student_id: int, date: str) -> Optional[Attendance]:
        """获取学生特定日期的考勤记录"""
        return self.find_one(student_id=student_id, date=date)
    
    def get_attendance_stats(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取考勤统计"""
        attendances = self.get_all()
        stats = {
            'total': 0,
            'present': 0,
            'absent': 0,
            'leave': 0
        }
        
        for attendance in attendances:
            if start_date <= attendance.date <= end_date:
                stats['total'] += 1
                if attendance.status == 'present':
                    stats['present'] += 1
                elif attendance.status == 'absent':
                    stats['absent'] += 1
                elif attendance.status == 'leave':
                    stats['leave'] += 1
        
        return stats
    
    def delete_by_student_id(self, student_id: int):
        """删除学生的所有考勤记录"""
        self._ensure_table_exists()
        self.data['in_memory_data'][self.table_name] = [
            item for item in self.data['in_memory_data'][self.table_name] 
            if item.get('student_id') != student_id
        ]

# ... existing code ...
class RewardPunishmentRepository(BaseRepository[RewardPunishment]):
    """奖励处分仓储类"""    
    
    def _dict_to_model(self, item_dict: Dict[str, Any]) -> RewardPunishment:
        return RewardPunishment(**item_dict)
    
    def get_by_student_id(self, student_id: int) -> List[RewardPunishment]:
        """根据学生ID获取奖励处分记录"""
        return self.find(student_id=student_id)
    
    def get_by_type(self, rp_type: str) -> List[RewardPunishment]:
        """根据类型获取奖励处分记录"""
        return self.find(type=rp_type)
    
    def get_by_student_id_and_type(self, student_id: int, rp_type: str) -> List[RewardPunishment]:
        """根据学生ID和类型获取奖励处分记录"""
        return self.find(student_id=student_id, type=rp_type)
    
    
    def get_rewards(self) -> List[RewardPunishment]:
        """获取所有奖励记录"""
        return self.find(type='reward')
    
    def get_punishments(self) -> List[RewardPunishment]:
        """获取所有处分记录"""
        return self.find(type='punishment')
    
    def get_stats_by_student(self, student_id: int) -> Dict[str, int]:
        """获取学生的奖励处分统计"""
        records = self.get_by_student_id(student_id)
        stats = {'rewards': 0, 'punishments': 0}
        for record in records:
            if record.type == 'reward':
                stats['rewards'] += 1
            elif record.type == 'punishment':
                stats['punishments'] += 1
        return stats
    
    def delete_by_student_id(self, student_id: int):
        """删除学生的所有奖励处分记录"""
        self._ensure_table_exists()
        self.data['in_memory_data'][self.table_name] = [
            item for item in self.data['in_memory_data'][self.table_name] 
            if item.get('student_id') != student_id
        ]

# ... existing code ...

class ParentRepository(BaseRepository[Parent]):
    """家长信息仓储类"""
    
    def _dict_to_model(self, item_dict: Dict[str, Any]) -> Parent:
        return Parent(**item_dict)
    
    def get_by_student_id(self, student_id: int) -> List[Parent]:
        """根据学生ID获取家长信息"""
        return self.find(student_id=student_id)
    
    def get_by_relationship(self, student_id: int, relationship: str) -> Optional[Parent]:
        """根据学生ID和关系获取家长信息"""
        return self.find_one(student_id=student_id, relationship=relationship)
    
    def get_parents_by_phone(self, phone: str) -> List[Parent]:
        """根据手机号获取家长信息"""
        return self.find(contact_phone=phone)
    
    def delete_by_student_id(self, student_id: int):
        """删除学生的所有家长信息"""
        self._ensure_table_exists()
        self.data['in_memory_data'][self.table_name] = [
            item for item in self.data['in_memory_data'][self.table_name] 
            if item.get('student_id') != student_id
        ]

class NoticeRepository(BaseRepository[Notice]):
    """通知仓储类"""
    
    def _dict_to_model(self, item_dict: Dict[str, Any]) -> Notice:
        return Notice(**item_dict)
    
    def get_recent_notices(self, limit: int = 5) -> List[Notice]:
        """获取最近的通知"""
        notices = sorted(self.get_all(), key=lambda x: x.date, reverse=True)
        return notices[:limit]
    
    def get_by_target(self, target: str) -> List[Notice]:
        """根据目标受众获取通知"""
        return self.find(target=target)
    
    def search(self, keyword: str) -> List[Notice]:
        """搜索通知（标题或内容）"""
        self._ensure_table_exists()
        results = []
        for item_dict in self.data['in_memory_data'][self.table_name]:
            if (keyword.lower() in item_dict.get('title', '').lower() or 
                keyword.lower() in item_dict.get('content', '').lower()):
                results.append(self._dict_to_model(item_dict))
        return results

class ScheduleRepository(BaseRepository[Schedule]):
    """排课仓储类"""
    
    def _dict_to_model(self, item_dict: Dict[str, Any]) -> Schedule:
        return Schedule(**item_dict)
    
    def get_by_course_id(self, course_id: int) -> List[Schedule]:
        """根据课程ID获取排课"""
        return self.find(course_id=course_id)
    
    def get_by_teacher_id(self, teacher_id: int) -> List[Schedule]:
        """根据教师ID获取排课"""
        return self.find(teacher_user_id=teacher_id)
    
    def get_by_day(self, day_of_week: str) -> List[Schedule]:
        """根据星期几获取排课"""
        return self.find(day_of_week=day_of_week)
    
    def get_conflicting_schedules(self, day_of_week: str, start_time: str, end_time: str, 
                                 location: str, teacher_id: int, exclude_id: int = None) -> List[Schedule]:
        """获取冲突的排课"""
        schedules = self.get_all()
        conflicting = []
        
        for schedule in schedules:
            if exclude_id and schedule.id == exclude_id:
                continue
                
            if schedule.day_of_week == day_of_week:
                # 检查时间冲突
                if (max(start_time, schedule.start_time) < min(end_time, schedule.end_time)):
                    # 检查地点冲突或教师冲突
                    if (schedule.location.lower() == location.lower() or 
                        schedule.teacher_user_id == teacher_id):
                        conflicting.append(schedule)
        
        return conflicting
    
    def delete_by_course_id(self, course_id: int):
        """删除课程的所有排课"""
        self._ensure_table_exists()
        self.data['in_memory_data'][self.table_name] = [
            item for item in self.data['in_memory_data'][self.table_name] 
            if item.get('course_id') != course_id
        ]

class LeaveRequestRepository(BaseRepository[LeaveRequest]):
    """请假申请仓储"""

    def _dict_to_model(self, item_dict: Dict[str, Any]) -> LeaveRequest:
        return LeaveRequest(**item_dict)

    def get_by_student(self, student_id: int) -> List[LeaveRequest]:
        return self.find(student_id=student_id)

    def get_by_status(self, status: str) -> List[LeaveRequest]:
        return self.find(status=status)

@dataclass
class EnrollmentStatusRepository(BaseRepository[EnrollmentStatus]):
    """选课状态仓储类"""
    
    def __init__(self, data_file: str = 'app_data.json'):
        super().__init__(data_file)
        self.table_name = 'enrollment_status'
        
    def _dict_to_model(self, item_dict: Dict[str, Any]) -> EnrollmentStatus:
        return EnrollmentStatus(**item_dict)
    
    def get_enrollment_status(self) -> EnrollmentStatus:
        """获取选课状态配置"""
        status = self.find_one(id=1)
        if not status:
            # 如果不存在，则创建默认配置
            status = EnrollmentStatus()
            self.create(status)
            self.save_data()
        return status
    
    def update_enrollment_status(self, enrollment_open: bool) -> EnrollmentStatus:
        """更新选课状态"""
        status = self.get_enrollment_status()
        if status:
            updated_status = self.update(status.id, enrollment_open=enrollment_open)
            self.save_data()
            return updated_status
        else:
            # 如果不存在，则创建新的配置
            status = EnrollmentStatus(enrollment_open=enrollment_open)
            created_status = self.create(status)
            self.save_data()
            return created_status

class RepositoryManager:
    """仓储管理器，统一管理所有仓储实例"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_repositories()
        return cls._instance
    
    def _init_repositories(self):
        """初始化所有仓储实例"""
        self.user_repo = UserRepository()
        self.student_repo = StudentRepository()
        self.course_repo = CourseRepository()
        self.enrollment_repo = EnrollmentRepository()
        self.attendance_repo = AttendanceRepository()
        self.reward_punishment_repo = RewardPunishmentRepository()
        self.parent_repo = ParentRepository()
        self.notice_repo = NoticeRepository()
        self.schedule_repo = ScheduleRepository()
        self.enrollment_status_repo = EnrollmentStatusRepository()  # 添加这一行
        self.leave_request_repo = LeaveRequestRepository()
    
    def save_all(self):
        """保存所有仓储数据"""
        # 获取所有仓储属性
        repos = [getattr(self, attr) for attr in dir(self) if attr.endswith('_repo')]
        
        # 保存每个仓储的数据
        for repo in repos:
            if hasattr(repo, 'save_data'):
                repo.save_data()
    
    def init_default_data(self):
        """初始化默认数据"""
        from models import DataInitializer
        
        # 检查是否需要初始化默认数据
        if self.user_repo.count() == 0:
            default_data = DataInitializer.create_default_data()
            
            # 保存所有默认数据
            for table_name, items in default_data.items():
                repo = getattr(self, f"{table_name[:-1]}_repo", None)
                if repo:
                    for item in items:
                        repo.create(item)
            
            self.save_all()
            print("Default data initialized successfully.")
        else:
            print("Existing data found. Skipping default data initialization.")



# 全局仓储管理器实例
repo_manager = RepositoryManager()
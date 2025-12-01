# services.py
import datetime
from typing import List, Dict, Any, Optional, Tuple
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
from repositories import repo_manager

class BaseService:
    """基础服务类"""
    
    def __init__(self):
        self.repo_manager = repo_manager
    
    def _validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, str]:
        """验证必填字段"""
        for field in required_fields:
            if not data.get(field):
                return False, f'{field}为必填项'
        return True, '验证通过'

class UserService(BaseService):
    """用户服务类"""
    
    def __init__(self):
        super().__init__()
        self.user_repo = self.repo_manager.user_repo
        self.student_repo = self.repo_manager.student_repo
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """用户认证"""
        user = self.user_repo.get_by_username(username)
        if user and check_password_hash(user.password, password):
            return user
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return self.user_repo.get_by_id(user_id)
    
    def get_all_users(self) -> List[User]:
        """获取所有用户"""
        return self.user_repo.get_all()
    
    class UserService(BaseService):
        """用户服务类 - 修复版本"""
    
    def create_user(self, user_data: Dict[str, Any]) -> Tuple[bool, Optional[User], str]:
        """创建用户 - 修复学生验证"""
        print(f"🔧 开始创建用户: {user_data.get('username')}")
        
        # 验证必填字段
        required_fields = ['username', 'password', 'role']
        is_valid, message = self._validate_required_fields(user_data, required_fields)
        if not is_valid:
            return False, None, message
        
        # 验证用户名唯一性
        existing_user = self.user_repo.get_by_username(user_data['username'])
        if existing_user:
            return False, None, f'用户名 {user_data["username"]} 已存在'
        
        # 验证学生角色必须关联学生信息
        if user_data['role'] == 'student':
            if not user_data.get('student_info_id'):
                return False, None, '学生角色必须关联一个学生信息'
            
            # 验证学生信息存在性
            try:
                student_id = int(user_data['student_info_id'])
                student = self.student_repo.get_by_id(student_id)
                if not student:
                    return False, None, f'关联的学生信息不存在 (ID: {student_id})'
                print(f"✅ 学生验证通过: {student.name} (ID: {student.id})")
            except (ValueError, TypeError) as e:
                return False, None, f'学生ID格式错误: {user_data["student_info_id"]}'
        
        try:
            # 创建用户
            user_id = self.user_repo.get_next_id()
            hashed_password = generate_password_hash(user_data['password'])
            
            # 处理学生信息ID
            student_info_id = None
            if user_data.get('student_info_id'):
                student_info_id = int(user_data['student_info_id'])
            
            user = User(
                id=user_id,
                username=user_data['username'],
                password=hashed_password,
                role=user_data['role'],
                student_info_id=student_info_id
            )
            
            created_user = self.user_repo.create(user)
            
            # 立即保存数据
            self.user_repo.save_data()
            print(f"💾 用户数据已保存: {created_user.username}")
            
            return True, created_user, '用户创建成功'
            
        except Exception as e:
            print(f"❌ 创建用户时发生错误: {e}")
            return False, None, f'创建用户时发生错误: {str(e)}'
    
    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Tuple[bool, Optional[User], str]:
        """更新用户信息 - 修复版本"""
        print(f"🔧 开始更新用户 (ID: {user_id}): {user_data.get('username')}")
        
        # 检查用户是否存在
        existing_user = self.user_repo.get_by_id(user_id)
        if not existing_user:
            return False, None, '用户不存在'
        
        # 验证用户名唯一性（排除当前用户）
        conflicting_user = self.user_repo.get_by_username(user_data['username'])
        if conflicting_user and conflicting_user.id != user_id:
            return False, None, f'用户名 {user_data["username"]} 已存在'
        
        # 验证学生角色必须关联学生信息
        if user_data['role'] == 'student':
            if not user_data.get('student_info_id'):
                return False, None, '学生角色必须关联一个学生信息'
            
            # 验证学生信息存在性
            try:
                student_id = int(user_data['student_info_id'])
                student = self.student_repo.get_by_id(student_id)
                if not student:
                    return False, None, f'关联的学生信息不存在 (ID: {student_id})'
                print(f"✅ 学生验证通过: {student.name} (ID: {student.id})")
            except (ValueError, TypeError) as e:
                return False, None, f'学生ID格式错误: {user_data["student_info_id"]}'
        
        try:
            # 准备更新数据
            update_data = {
                'username': user_data['username'],
                'role': user_data['role'],
                'student_info_id': int(user_data['student_info_id']) if user_data.get('student_info_id') else None
            }
            
            # 如果提供了新密码，则更新密码
            if user_data.get('password'):
                update_data['password'] = generate_password_hash(user_data['password'])
            
            updated_user = self.user_repo.update(user_id, **update_data)
            
            if updated_user:
                # 立即保存数据
                self.user_repo.save_data()
                print(f"💾 用户数据已更新: {updated_user.username}")
                return True, updated_user, '用户信息更新成功'
            else:
                return False, None, '更新用户失败'
                
        except Exception as e:
            print(f"❌ 更新用户时发生错误: {e}")
            return False, None, f'更新用户时发生错误: {str(e)}'
    
    def delete_user(self, user_id: int, current_user_id: int) -> Tuple[bool, str]:
        """删除用户"""
        if user_id == current_user_id:
            return False, '不能删除当前登录的用户'
        
        existing_user = self.user_repo.get_by_id(user_id)
        if not existing_user:
            return False, '用户不存在'
        
        try:
            success = self.user_repo.delete(user_id)
            if success:
                # 立即保存数据
                self.user_repo.save_data()
                print(f"💾 用户删除完成 (ID: {user_id})")
                return True, '用户删除成功'
            else:
                return False, '删除用户失败'
                
        except Exception as e:
            print(f"❌ 删除用户时发生错误: {e}")
            return False, f'删除用户时发生错误: {str(e)}'
    
    def _validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, str]:
        """验证必填字段"""
        for field in required_fields:
            if not data.get(field):
                return False, f'{field}为必填项'
        return True, '验证通过'
    
    def get_student_users(self) -> List[User]:
        """获取所有学生用户"""
        return self.user_repo.get_student_users()
    
    def get_teacher_users(self) -> List[User]:
        """获取所有教师用户"""
        return self.user_repo.get_teacher_users()

class StudentService(BaseService):
    """学生服务类"""
    
    def __init__(self):
        super().__init__()
        self.student_repo = self.repo_manager.student_repo
        self.enrollment_repo = self.repo_manager.enrollment_repo
        self.attendance_repo = self.repo_manager.attendance_repo
        self.reward_punishment_repo = self.repo_manager.reward_punishment_repo
        self.parent_repo = self.repo_manager.parent_repo
    
    def get_all_students(self) -> List[Student]:
        """获取所有学生"""
        return self.student_repo.get_all()
    
    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        """根据ID获取学生"""
        return self.student_repo.get_by_id(student_id)
    
    def get_student_by_student_id(self, student_id_str: str) -> Optional[Student]:
        """根据学号获取学生"""
        return self.student_repo.get_by_student_id(student_id_str)
    
    def create_student(self, student_data: Dict[str, Any]) -> Tuple[bool, Optional[Student], str]:
        """创建学生"""
        # 验证必填字段
        required_fields = ['name', 'gender', 'age', 'student_id']
        is_valid, message = self._validate_required_fields(student_data, required_fields)
        if not is_valid:
            return False, None, message
        
        # 验证年龄
        try:
            age = int(student_data['age'])
            if age <= 0:
                return False, None, '年龄必须为正整数'
        except ValueError:
            return False, None, '年龄必须为数字'
        
        # 验证学号唯一性
        if self.student_repo.get_by_student_id(student_data['student_id']):
            return False, None, f'学号 {student_data["student_id"]} 已存在'
        
        try:
            # 创建学生
            student_id = self.student_repo.get_next_id()
            student = Student(
                id=student_id,
                name=student_data['name'],
                gender=student_data['gender'],
                age=age,
                student_id=student_data['student_id'],
                contact_phone=student_data.get('contact_phone', ''),
                family_info=student_data.get('family_info', ''),
                class_name=student_data.get('class_name', ''),
                homeroom_teacher=student_data.get('homeroom_teacher', '')
            )
            
            created_student = self.student_repo.create(student)
            self.student_repo.save_data()
            return True, created_student, '学生创建成功'
            
        except Exception as e:
            return False, None, f'创建学生时发生错误: {str(e)}'
    
    def update_student(self, student_id: int, student_data: Dict[str, Any]) -> Tuple[bool, Optional[Student], str]:
        """更新学生"""
        existing_student = self.student_repo.get_by_id(student_id)
        if not existing_student:
            return False, None, '学生不存在'
        
        # 验证年龄
        try:
            age = int(student_data['age'])
            if age <= 0:
                return False, None, '年龄必须为正整数'
        except ValueError:
            return False, None, '年龄必须为数字'
        
        # 验证学号唯一性（排除当前学生）
        conflicting_student = self.student_repo.get_by_student_id(student_data['student_id'])
        if conflicting_student and conflicting_student.id != student_id:
            return False, None, f'学号 {student_data["student_id"]} 已存在'
        
        try:
            update_data = {
                'name': student_data['name'],
                'gender': student_data['gender'],
                'age': age,
                'student_id': student_data['student_id'],
                'contact_phone': student_data.get('contact_phone', ''),
                'family_info': student_data.get('family_info', ''),
                'class_name': student_data.get('class_name', ''),
                'homeroom_teacher': student_data.get('homeroom_teacher', '')
            }
            
            updated_student = self.student_repo.update(student_id, **update_data)
            if updated_student:
                self.student_repo.save_data()
                return True, updated_student, '学生更新成功'
            else:
                return False, None, '更新学生失败'
                
        except Exception as e:
            return False, None, f'更新学生时发生错误: {str(e)}'
    
    def delete_student(self, student_id: int) -> Tuple[bool, str]:
        """删除学生（级联删除相关数据）"""
        existing_student = self.student_repo.get_by_id(student_id)
        if not existing_student:
            return False, '学生不存在'
        
        try:
            # 级联删除相关数据
            self.enrollment_repo.delete_by_student_id(student_id)
            self.attendance_repo.delete_by_student_id(student_id)
            self.reward_punishment_repo.delete_by_student_id(student_id)
            self.parent_repo.delete_by_student_id(student_id)
            
            # 删除学生
            success = self.student_repo.delete(student_id)
            if success:
                self.student_repo.save_data()
                return True, '学生删除成功'
            else:
                return False, '删除学生失败'
                
        except Exception as e:
            return False, f'删除学生时发生错误: {str(e)}'
    
    def search_students(self, keyword: str) -> List[Student]:
        """搜索学生"""
        return self.student_repo.search(keyword)
    
    def get_students_by_class(self, class_name: str) -> List[Student]:
        """根据班级获取学生"""
        return self.student_repo.get_by_class(class_name)

class CourseService(BaseService):
    """课程服务类"""
    
    def __init__(self):
        super().__init__()
        self.course_repo = self.repo_manager.course_repo
        self.enrollment_repo = self.repo_manager.enrollment_repo
        self.schedule_repo = self.repo_manager.schedule_repo
    
    def get_all_courses(self) -> List[Course]:
        """获取所有课程"""
        return self.course_repo.get_all()
    
    def get_course_by_id(self, course_id: int) -> Optional[Course]:
        """根据ID获取课程"""
        return self.course_repo.get_by_id(course_id)
    
    def create_course(self, course_data: Dict[str, Any]) -> Tuple[bool, Optional[Course], str]:
        """创建课程"""
        # 验证必填字段
        required_fields = ['name', 'credits']
        is_valid, message = self._validate_required_fields(course_data, required_fields)
        if not is_valid:
            return False, None, message
        
        # 验证学分
        try:
            credits = int(course_data['credits'])
            if credits <= 0:
                return False, None, '学分必须为正整数'
        except ValueError:
            return False, None, '学分必须为数字'
        
        # 验证课程名称唯一性
        if self.course_repo.get_by_name(course_data['name']):
            return False, None, f'课程名称 {course_data["name"]} 已存在'
        
        try:
            # 创建课程
            course_id = self.course_repo.get_next_id()
            course = Course(
                id=course_id,
                name=course_data['name'],
                description=course_data.get('description', ''),
                credits=credits,
                capacity=int(course_data['capacity']) if course_data.get('capacity') else None
            )
            
            created_course = self.course_repo.create(course)
            self.course_repo.save_data()
            return True, created_course, '课程创建成功'
            
        except Exception as e:
            return False, None, f'创建课程时发生错误: {str(e)}'
    
    def update_course(self, course_id: int, course_data: Dict[str, Any]) -> Tuple[bool, Optional[Course], str]:
        """更新课程"""
        existing_course = self.course_repo.get_by_id(course_id)
        if not existing_course:
            return False, None, '课程不存在'
        
        # 验证学分
        try:
            credits = int(course_data['credits'])
            if credits <= 0:
                return False, None, '学分必须为正整数'
        except ValueError:
            return False, None, '学分必须为数字'
        
        # 验证课程名称唯一性（排除当前课程）
        conflicting_course = self.course_repo.get_by_name(course_data['name'])
        if conflicting_course and conflicting_course.id != course_id:
            return False, None, f'课程名称 {course_data["name"]} 已存在'
        
        try:
            update_data = {
                'name': course_data['name'],
                'description': course_data.get('description', ''),
                'credits': credits,
                'capacity': int(course_data['capacity']) if course_data.get('capacity') else None
            }
            
            updated_course = self.course_repo.update(course_id, **update_data)
            if updated_course:
                self.course_repo.save_data()
                return True, updated_course, '课程更新成功'
            else:
                return False, None, '更新课程失败'
                
        except Exception as e:
            return False, None, f'更新课程时发生错误: {str(e)}'
    
    def delete_course(self, course_id: int) -> Tuple[bool, str]:
        """删除课程（级联删除相关数据）"""
        existing_course = self.course_repo.get_by_id(course_id)
        if not existing_course:
            return False, '课程不存在'
        
        try:
            # 级联删除相关数据
            self.enrollment_repo.delete_by_course_id(course_id)
            self.schedule_repo.delete_by_course_id(course_id)
            
            # 删除课程
            success = self.course_repo.delete(course_id)
            if success:
                self.course_repo.save_data()
                return True, '课程删除成功'
            else:
                return False, '删除课程失败'
                
        except Exception as e:
            return False, f'删除课程时发生错误: {str(e)}'
    
    def get_enrolled_count(self, course_id: int) -> int:
        """获取课程选课人数"""
        return self.enrollment_repo.get_enrollment_count(course_id)
    
    def is_course_available(self, course_id: int) -> bool:
        """检查课程是否还有空位"""
        course = self.course_repo.get_by_id(course_id)
        if not course:
            return False
        
        if course.capacity is None:
            return True
        
        enrolled_count = self.get_enrolled_count(course_id)
        return enrolled_count < course.capacity
    
    def search_courses(self, keyword: str) -> List[Course]:
        """搜索课程"""
        return self.course_repo.search(keyword)

class EnrollmentService(BaseService):
    """选课服务类"""
    
    def __init__(self):
        super().__init__()
        self.enrollment_repo = self.repo_manager.enrollment_repo
        self.student_repo = self.repo_manager.student_repo
        self.course_repo = self.repo_manager.course_repo
    
    def enroll_student(self, student_id: int, course_id: int) -> Tuple[bool, Optional[Enrollment], str]:
        """学生选课"""
        # 验证学生和课程存在
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return False, None, '学生不存在'
        
        course = self.course_repo.get_by_id(course_id)
        if not course:
            return False, None, '课程不存在'
        
        # 检查是否已经选修
        if self.enrollment_repo.get_enrollment(student_id, course_id):
            return False, None, '该学生已经选修此课程'
        
        # 检查课程容量
        if course.capacity is not None:
            enrolled_count = self.enrollment_repo.get_enrollment_count(course_id)
            if enrolled_count >= course.capacity:
                return False, None, '课程已满，无法选课'
        
        try:
            # 创建选课记录
            enrollment_id = self.enrollment_repo.get_next_id()
            enrollment = Enrollment(
                id=enrollment_id,
                student_id=student_id,
                course_id=course_id,
                exam_score=None,
                performance_score=None
            )
            
            created_enrollment = self.enrollment_repo.create(enrollment)
            self.enrollment_repo.save_data()
            return True, created_enrollment, '选课成功'
            
        except Exception as e:
            return False, None, f'选课时发生错误: {str(e)}'
    
    def unenroll_student(self, student_id: int, course_id: int) -> Tuple[bool, str]:
        """学生退课"""
        enrollment = self.enrollment_repo.get_enrollment(student_id, course_id)
        if not enrollment:
            return False, '该学生未选修此课程'
        
        try:
            success = self.enrollment_repo.delete(enrollment.id)
            if success:
                self.enrollment_repo.save_data()
                return True, '退课成功'
            else:
                return False, '退课失败'
                
        except Exception as e:
            return False, f'退课时发生错误: {str(e)}'
    
    def update_scores(self, enrollment_id: int, exam_score: Optional[float] = None, 
                     performance_score: Optional[float] = None) -> Tuple[bool, Optional[Enrollment], str]:
        """更新成绩"""
        enrollment = self.enrollment_repo.get_by_id(enrollment_id)
        if not enrollment:
            return False, None, '选课记录不存在'
        
        # 验证成绩范围
        if exam_score is not None and (exam_score < 0 or exam_score > 100):
            return False, None, '考试成绩必须在0-100之间'
        
        if performance_score is not None and (performance_score < 0 or performance_score > 100):
            return False, None, '平时成绩必须在0-100之间'
        
        try:
            update_data = {}
            if exam_score is not None:
                update_data['exam_score'] = exam_score
            if performance_score is not None:
                update_data['performance_score'] = performance_score
            
            updated_enrollment = self.enrollment_repo.update(enrollment_id, **update_data)
            if updated_enrollment:
                self.enrollment_repo.save_data()
                return True, updated_enrollment, '成绩更新成功'
            else:
                return False, None, '更新成绩失败'
                
        except Exception as e:
            return False, None, f'更新成绩时发生错误: {str(e)}'
    

    def get_courses_for_student(self, student_id: int) -> List[int]:
        """获取学生选修的所有课程ID"""
        enrollments = self.enrollment_repo.get_by_student_id(student_id)
        return [enrollment.course_id for enrollment in enrollments]
# ... existing code ...
    def get_student_enrollments(self, student_id: int) -> List[Enrollment]:
        """获取学生的选课记录"""
        return self.enrollment_repo.get_by_student_id(student_id)
    
    def get_course_enrollments(self, course_id: int) -> List[Enrollment]:
        """获取课程的选课记录"""
        return self.enrollment_repo.get_by_course_id(course_id)
    
    def is_student_enrolled(self, student_id: int, course_id: int) -> bool:
        """检查学生是否已选修课程"""
        return self.enrollment_repo.get_enrollment(student_id, course_id) is not None

class AttendanceService(BaseService):
    """考勤服务类"""
    
    def __init__(self):
        super().__init__()
        self.attendance_repo = self.repo_manager.attendance_repo
        self.student_repo = self.repo_manager.student_repo
    
    def check_in_student(self, student_id: int, date: str = None) -> Tuple[bool, Optional[Attendance], str]:
        """学生签到"""
        if not date:
            date = datetime.date.today().strftime('%Y-%m-%d')
        
        # 验证学生存在
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return False, None, '学生不存在'
        
        # 检查今天是否已经签到
        existing_attendance = self.attendance_repo.get_by_student_and_date(student_id, date)
        if existing_attendance:
            return False, None, f'该学生今天 ({date}) 已经签到过了'
        
        try:
            # 创建考勤记录
            attendance_id = self.attendance_repo.get_next_id()
            attendance = Attendance(
                id=attendance_id,
                student_id=student_id,
                date=date,
                status='present',
                reason='学生自主签到'
            )
            
            created_attendance = self.attendance_repo.create(attendance)
            self.attendance_repo.save_data()
            return True, created_attendance, '签到成功'
            
        except Exception as e:
            return False, None, f'签到时发生错误: {str(e)}'
    
    def record_attendance(self, student_id: int, date: str, status: str, reason: str = '') -> Tuple[bool, Optional[Attendance], str]:
        """记录考勤"""
        # 验证学生存在
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return False, None, '学生不存在'
        
        # 验证状态
        if status not in ['present', 'absent', 'leave']:
            return False, None, '无效的考勤状态'
        
        # 检查是否已经记录
        existing_attendance = self.attendance_repo.get_by_student_and_date(student_id, date)
        if existing_attendance:
            return False, None, f'该学生 {date} 的考勤记录已存在'
        
        try:
            # 创建考勤记录
            attendance_id = self.attendance_repo.get_next_id()
            attendance = Attendance(
                id=attendance_id,
                student_id=student_id,
                date=date,
                status=status,
                reason=reason
            )
            
            created_attendance = self.attendance_repo.create(attendance)
            self.attendance_repo.save_data()
            return True, created_attendance, '考勤记录添加成功'
            
        except Exception as e:
            return False, None, f'记录考勤时发生错误: {str(e)}'
    
    def update_attendance(self, attendance_id: int, status: str, reason: str) -> Tuple[bool, Optional[Attendance], str]:
        """更新考勤记录"""
        attendance = self.attendance_repo.get_by_id(attendance_id)
        if not attendance:
            return False, None, '考勤记录不存在'
        
        # 验证状态
        if status not in ['present', 'absent', 'leave']:
            return False, None, '无效的考勤状态'
        
        try:
            update_data = {
                'status': status,
                'reason': reason
            }
            
            updated_attendance = self.attendance_repo.update(attendance_id, **update_data)
            if updated_attendance:
                self.attendance_repo.save_data()
                return True, updated_attendance, '考勤记录更新成功'
            else:
                return False, None, '更新考勤记录失败'
                
        except Exception as e:
            return False, None, f'更新考勤记录时发生错误: {str(e)}'
    
    def get_student_attendance(self, student_id: int) -> List[Attendance]:
        """获取学生的考勤记录"""
        return self.attendance_repo.get_by_student_id(student_id)
    
    def get_date_attendance(self, date: str) -> List[Attendance]:
        """获取某天的考勤记录"""
        return self.attendance_repo.get_by_date(date)
    
    def get_attendance_stats(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取考勤统计"""
        return self.attendance_repo.get_attendance_stats(start_date, end_date)


class RewardPunishmentService(BaseService):
    """奖励处分服务类"""
    
    def __init__(self):
        super().__init__()
        self.reward_punishment_repo = self.repo_manager.reward_punishment_repo
        self.student_repo = self.repo_manager.student_repo
    
    def create_record(self, student_id: int, rp_type: str, description: str, date: str) -> Tuple[bool, Optional[RewardPunishment], str]:
        """创建奖励处分记录"""
        # 验证学生存在
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return False, None, '学生不存在'
        
        # 验证类型
        if rp_type not in ['reward', 'punishment']:
            return False, None, '无效的记录类型'
        
        # 验证必填字段
        if not description or not date:
            return False, None, '描述和日期为必填项'
        
        try:
            # 创建记录
            record_id = self.reward_punishment_repo.get_next_id()
            record = RewardPunishment(
                id=record_id,
                student_id=student_id,
                type=rp_type,
                description=description,
                date=date
            )
            
            created_record = self.reward_punishment_repo.create(record)
            self.reward_punishment_repo.save_data()
            return True, created_record, '记录创建成功'
            
        except Exception as e:
            return False, None, f'创建记录时发生错误: {str(e)}'
    
    def get_student_records(self, student_id: int) -> List[RewardPunishment]:
        """获取学生的奖励处分记录"""
        return self.reward_punishment_repo.get_by_student_id(student_id)
    
    def update_record(self, record_id: int, rp_type: str, description: str, date: str) -> Tuple[bool, Optional[RewardPunishment], str]:
        """更新奖励处分记录"""
        record = self.reward_punishment_repo.get_by_id(record_id)
        if not record:
            return False, None, '记录不存在'
        
        # 验证类型
        if rp_type not in ['reward', 'punishment']:
            return False, None, '无效的记录类型'
        
        # 验证必填字段
        if not description or not date:
            return False, None, '描述和日期为必填项'
        
        try:
            update_data = {
                'type': rp_type,
                'description': description,
                'date': date
            }
            
            updated_record = self.reward_punishment_repo.update(record_id, **update_data)
            if updated_record:
                self.reward_punishment_repo.save_data()
                return True, updated_record, '记录更新成功'
            else:
                return False, None, '更新记录失败'
                
        except Exception as e:
            return False, None, f'更新记录时发生错误: {str(e)}'
    
    def delete_record(self, record_id: int) -> Tuple[bool, str]:
        """删除奖励处分记录"""
        record = self.reward_punishment_repo.get_by_id(record_id)
        if not record:
            return False, '记录不存在'
        
        try:
            success = self.reward_punishment_repo.delete(record_id)
            if success:
                self.reward_punishment_repo.save_data()
                return True, '记录删除成功'
            else:
                return False, '删除记录失败'
                
        except Exception as e:
            return False, f'删除记录时发生错误: {str(e)}'
    
    def get_rewards(self) -> List[RewardPunishment]:
        """获取所有奖励记录"""
        return self.reward_punishment_repo.get_rewards()
    
    def get_punishments(self) -> List[RewardPunishment]:
        """获取所有处分记录"""
        return self.reward_punishment_repo.get_punishments()
    
    def get_student_stats(self, student_id: int) -> Dict[str, int]:
        """获取学生的奖励处分统计"""
        return self.reward_punishment_repo.get_stats_by_student(student_id)
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """获取全校奖惩统计"""
        all_records = self.reward_punishment_repo.get_all()
        stats = {
            'total': len(all_records),
            'rewards': 0,
            'punishments': 0,
            'by_month': {}
        }
        
        for record in all_records:
            if record.type == 'reward':
                stats['rewards'] += 1
            elif record.type == 'punishment':
                stats['punishments'] += 1
                
            # 按月份统计
            year_month = record.date[:7]  # YYYY-MM
            if year_month not in stats['by_month']:
                stats['by_month'][year_month] = {'rewards': 0, 'punishments': 0}
            
            if record.type == 'reward':
                stats['by_month'][year_month]['rewards'] += 1
            else:
                stats['by_month'][year_month]['punishments'] += 1
                
        return stats
    
    def get_records_by_date_range(self, start_date: str, end_date: str) -> List[RewardPunishment]:
        """获取指定日期范围内的奖惩记录"""
        all_records = self.reward_punishment_repo.get_all()
        filtered_records = []
        
        for record in all_records:
            if start_date <= record.date <= end_date:
                filtered_records.append(record)
                
        return filtered_records
# ... existing code ...

class ParentService(BaseService):
    """家长信息服务类"""
    
    def __init__(self):
        super().__init__()
        self.parent_repo = self.repo_manager.parent_repo
        self.student_repo = self.repo_manager.student_repo
    
    def create_parent(self, student_id: int, parent_name: str, relationship: str, 
                     contact_phone: str, email: str = '', address: str = '') -> Tuple[bool, Optional[Parent], str]:
        """创建家长信息"""
        # 验证学生存在
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return False, None, '学生不存在'
        
        # 验证必填字段
        if not parent_name or not relationship or not contact_phone:
            return False, None, '家长姓名、关系和手机号为必填项'
        
        # 验证手机号格式
        if not contact_phone.isdigit() or len(contact_phone) != 11:
            return False, None, '请输入正确的11位手机号码'
        
        # 验证关系唯一性
        existing_parent = self.parent_repo.get_by_relationship(student_id, relationship)
        if existing_parent:
            return False, None, f'该学生已经存在{relationship}的联系信息'
        
        try:
            # 创建家长信息
            parent_id = self.parent_repo.get_next_id()
            parent = Parent(
                id=parent_id,
                student_id=student_id,
                parent_name=parent_name,
                relationship=relationship,
                contact_phone=contact_phone,
                email=email,
                address=address
            )
            
            created_parent = self.parent_repo.create(parent)
            self.parent_repo.save_data()
            return True, created_parent, '家长信息添加成功'
            
        except Exception as e:
            return False, None, f'创建家长信息时发生错误: {str(e)}'
    
    def get_student_parents(self, student_id: int) -> List[Parent]:
        """获取学生的家长信息"""
        return self.parent_repo.get_by_student_id(student_id)
    
    def update_parent(self, parent_id: int, parent_name: str, relationship: str, 
                     contact_phone: str, email: str = '', address: str = '') -> Tuple[bool, Optional[Parent], str]:
        """更新家长信息"""
        parent = self.parent_repo.get_by_id(parent_id)
        if not parent:
            return False, None, '家长信息不存在'
        
        # 验证必填字段
        if not parent_name or not relationship or not contact_phone:
            return False, None, '家长姓名、关系和手机号为必填项'
        
        # 验证手机号格式
        if not contact_phone.isdigit() or len(contact_phone) != 11:
            return False, None, '请输入正确的11位手机号码'
        
        # 验证关系唯一性（排除当前记录）
        existing_parent = self.parent_repo.get_by_relationship(parent.student_id, relationship)
        if existing_parent and existing_parent.id != parent_id:
            return False, None, f'该学生已经存在{relationship}的联系信息'
        
        try:
            update_data = {
                'parent_name': parent_name,
                'relationship': relationship,
                'contact_phone': contact_phone,
                'email': email,
                'address': address
            }
            
            updated_parent = self.parent_repo.update(parent_id, **update_data)
            if updated_parent:
                self.parent_repo.save_data()
                return True, updated_parent, '家长信息更新成功'
            else:
                return False, None, '更新家长信息失败'
                
        except Exception as e:
            return False, None, f'更新家长信息时发生错误: {str(e)}'
    
    def delete_parent(self, parent_id: int) -> Tuple[bool, str]:
        """删除家长信息"""
        parent = self.parent_repo.get_by_id(parent_id)
        if not parent:
            return False, '家长信息不存在'
        
        try:
            success = self.parent_repo.delete(parent_id)
            if success:
                self.parent_repo.save_data()
                return True, '家长信息删除成功'
            else:
                return False, '删除家长信息失败'
                
        except Exception as e:
            return False, f'删除家长信息时发生错误: {str(e)}'

class NoticeService(BaseService):
    """通知服务类"""
    
    def __init__(self):
        super().__init__()
        self.notice_repo = self.repo_manager.notice_repo
    
    def create_notice(self, title: str, content: str, target: str = '', sender: str = '') -> Tuple[bool, Optional[Notice], str]:
        """创建通知"""
        # 验证必填字段
        if not title or not content:
            return False, None, '标题和内容为必填项'
        
        # 验证长度限制
        if len(title) > 100:
            return False, None, '标题长度不能超过100个字符'
        
        if len(content) > 2000:
            return False, None, '内容长度不能超过2000个字符'
        
        try:
            # 创建通知
            notice_id = self.notice_repo.get_next_id()
            notice = Notice(
                id=notice_id,
                title=title,
                content=content,
                target=target,
                sender=sender or '系统',
                date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            created_notice = self.notice_repo.create(notice)
            self.notice_repo.save_data()
            return True, created_notice, '通知发布成功'
            
        except Exception as e:
            return False, None, f'创建通知时发生错误: {str(e)}'
    
    def update_notice(self, notice_id: int, title: str, content: str, target: str = '', sender: str = '') -> Tuple[bool, Optional[Notice], str]:
        """更新通知"""
        notice = self.notice_repo.get_by_id(notice_id)
        if not notice:
            return False, None, '通知不存在'
        
        # 验证必填字段
        if not title or not content:
            return False, None, '标题和内容为必填项'
        
        # 验证长度限制
        if len(title) > 100:
            return False, None, '标题长度不能超过100个字符'
        
        if len(content) > 2000:
            return False, None, '内容长度不能超过2000个字符'
        
        try:
            update_data = {
                'title': title,
                'content': content,
                'target': target,
                'sender': sender or notice.sender
            }
            
            updated_notice = self.notice_repo.update(notice_id, **update_data)
            if updated_notice:
                self.notice_repo.save_data()
                return True, updated_notice, '通知更新成功'
            else:
                return False, None, '更新通知失败'
                
        except Exception as e:
            return False, None, f'更新通知时发生错误: {str(e)}'
    
    def delete_notice(self, notice_id: int) -> Tuple[bool, str]:
        """删除通知"""
        notice = self.notice_repo.get_by_id(notice_id)
        if not notice:
            return False, '通知不存在'
        
        try:
            success = self.notice_repo.delete(notice_id)
            if success:
                self.notice_repo.save_data()
                return True, '通知删除成功'
            else:
                return False, '删除通知失败'
                
        except Exception as e:
            return False, f'删除通知时发生错误: {str(e)}'
    
    def get_recent_notices(self, limit: int = 5) -> List[Notice]:
        """获取最近的通知"""
        return self.notice_repo.get_recent_notices(limit)
    
    def get_notices_by_target(self, target: str) -> List[Notice]:
        """根据目标受众获取通知"""
        return self.notice_repo.get_by_target(target)
    
    def search_notices(self, keyword: str) -> List[Notice]:
        """搜索通知"""
        return self.notice_repo.search(keyword)
    
    def get_notices_for_user(self, user_role: str) -> List[Notice]:
        """根据用户角色获取可见通知"""
        all_notices = self.notice_repo.get_all()
        
        if user_role == 'student':
            # 学生只能看到：所有用户的通知 + 针对学生的通知
            return [notice for notice in all_notices if not notice.target or notice.target == 'students']
        elif user_role == 'teacher':
            # 教师能看到：所有用户的通知 + 针对教师的通知
            return [notice for notice in all_notices if not notice.target or notice.target in ['', 'teachers', 'students']]
        else:  # admin
            # 管理员可以看到所有通知
            return all_notices

class ScheduleService(BaseService):
    """排课服务类"""
    
    def __init__(self):
        super().__init__()
        self.schedule_repo = self.repo_manager.schedule_repo
        self.course_repo = self.repo_manager.course_repo
        self.user_repo = self.repo_manager.user_repo
    
    def create_schedule(self, course_id: int, teacher_user_id: int, day_of_week: str, 
                       start_time: str, end_time: str, location: str, semester: str) -> Tuple[bool, Optional[Schedule], str]:
        """创建排课"""
        # 验证课程存在
        course = self.course_repo.get_by_id(course_id)
        if not course:
            return False, None, '课程不存在'
        
        # 验证教师存在且角色正确
        teacher = self.user_repo.get_by_id(teacher_user_id)
        if not teacher or teacher.role != 'teacher':
            return False, None, '教师不存在或角色不正确'
        
        # 验证时间格式
        if start_time >= end_time:
            return False, None, '开始时间必须早于结束时间'
        
        # 检查排课冲突
        conflicting_schedules = self.schedule_repo.get_conflicting_schedules(
            day_of_week, start_time, end_time, location, teacher_user_id
        )
        
        if conflicting_schedules:
            conflict_info = []
            for schedule in conflicting_schedules:
                course_name = self.course_repo.get_by_id(schedule.course_id).name
                if schedule.location.lower() == location.lower():
                    conflict_info.append(f"教室 {location} 已被课程 '{course_name}' 占用")
                if schedule.teacher_user_id == teacher_user_id:
                    conflict_info.append(f"教师已被课程 '{course_name}' 占用")
            
            return False, None, '; '.join(conflict_info)
        
        try:
            # 创建排课
            schedule_id = self.schedule_repo.get_next_id()
            schedule = Schedule(
                id=schedule_id,
                course_id=course_id,
                teacher_user_id=teacher_user_id,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                location=location,
                semester=semester
            )
            
            created_schedule = self.schedule_repo.create(schedule)
            self.schedule_repo.save_data()
            return True, created_schedule, '排课添加成功'
            
        except Exception as e:
            return False, None, f'创建排课时发生错误: {str(e)}'
    
    def update_schedule(self, schedule_id: int, course_id: int, teacher_user_id: int, day_of_week: str, 
                       start_time: str, end_time: str, location: str, semester: str) -> Tuple[bool, Optional[Schedule], str]:
        """更新排课"""
        schedule = self.schedule_repo.get_by_id(schedule_id)
        if not schedule:
            return False, None, '排课不存在'
        
        # 验证课程存在
        course = self.course_repo.get_by_id(course_id)
        if not course:
            return False, None, '课程不存在'
        
        # 验证教师存在且角色正确
        teacher = self.user_repo.get_by_id(teacher_user_id)
        if not teacher or teacher.role != 'teacher':
            return False, None, '教师不存在或角色不正确'
        
        # 验证时间格式
        if start_time >= end_time:
            return False, None, '开始时间必须早于结束时间'
        
        # 检查排课冲突（排除当前排课）
        conflicting_schedules = self.schedule_repo.get_conflicting_schedules(
            day_of_week, start_time, end_time, location, teacher_user_id, schedule_id
        )
        
        if conflicting_schedules:
            conflict_info = []
            for conf_schedule in conflicting_schedules:
                course_name = self.course_repo.get_by_id(conf_schedule.course_id).name
                if conf_schedule.location.lower() == location.lower():
                    conflict_info.append(f"教室 {location} 已被课程 '{course_name}' 占用")
                if conf_schedule.teacher_user_id == teacher_user_id:
                    conflict_info.append(f"教师已被课程 '{course_name}' 占用")
            
            return False, None, '; '.join(conflict_info)
        
        try:
            update_data = {
                'course_id': course_id,
                'teacher_user_id': teacher_user_id,
                'day_of_week': day_of_week,
                'start_time': start_time,
                'end_time': end_time,
                'location': location,
                'semester': semester
            }
            
            updated_schedule = self.schedule_repo.update(schedule_id, **update_data)
            if updated_schedule:
                self.schedule_repo.save_data()
                return True, updated_schedule, '排课更新成功'
            else:
                return False, None, '更新排课失败'
                
        except Exception as e:
            return False, None, f'更新排课时发生错误: {str(e)}'
    
    def delete_schedule(self, schedule_id: int) -> Tuple[bool, str]:
        """删除排课"""
        schedule = self.schedule_repo.get_by_id(schedule_id)
        if not schedule:
            return False, '排课不存在'
        
        try:
            success = self.schedule_repo.delete(schedule_id)
            if success:
                self.schedule_repo.save_data()
                return True, '排课删除成功'
            else:
                return False, '删除排课失败'
                
        except Exception as e:
            return False, f'删除排课时发生错误: {str(e)}'
    
    def get_course_schedules(self, course_id: int) -> List[Schedule]:
        """获取课程的排课"""
        return self.schedule_repo.get_by_course_id(course_id)
    
    def get_teacher_schedules(self, teacher_id: int) -> List[Schedule]:
        """获取教师的排课"""
        return self.schedule_repo.get_by_teacher_id(teacher_id)
    
    def get_day_schedules(self, day_of_week: str) -> List[Schedule]:
        """获取某天的排课"""
        return self.schedule_repo.get_by_day(day_of_week)

class StatisticsService(BaseService):
    """统计服务类"""
    
    def __init__(self):
        super().__init__()
        self.student_repo = self.repo_manager.student_repo
        self.course_repo = self.repo_manager.course_repo
        self.attendance_repo = self.repo_manager.attendance_repo
        self.enrollment_repo = self.repo_manager.enrollment_repo
        self.reward_punishment_repo = self.repo_manager.reward_punishment_repo
    
    def get_general_statistics(self) -> Dict[str, Any]:
        """获取总体统计信息"""
        total_students = len(self.student_repo.get_all())
        total_courses = len(self.course_repo.get_all())
        
        # 按性别统计学生
        students_by_gender = {}
        for student in self.student_repo.get_all():
            gender = student.gender
            students_by_gender[gender] = students_by_gender.get(gender, 0) + 1
        
        # 将字典转换为列表格式以便模板使用
        students_by_gender_list = []
        for gender, count in students_by_gender.items():
            students_by_gender_list.append({
                'gender': gender,
                'count': count
            })
        
        # 考勤概览 (过去7天)
        today = datetime.date.today()
        attendance_summary = []
        for i in range(7):
            date = (today - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            day_attendance = self.attendance_repo.get_by_date(date)
            
            # 统计当天出勤情况
            present_count = sum(1 for a in day_attendance if a.status == 'present')
            absent_count = sum(1 for a in day_attendance if a.status == 'absent')
            leave_count = sum(1 for a in day_attendance if a.status == 'leave')
            
            attendance_summary.append({
                'date': date,
                'present_count': present_count,
                'absent_count': absent_count,
                'leave_count': leave_count
            })
        
        # 平均成绩统计
        course_scores = {}
        for enrollment in self.enrollment_repo.get_all():
            if enrollment.course_id not in course_scores:
                course_scores[enrollment.course_id] = {
                    'exam_scores': [], 
                    'performance_scores': []
                }
            
            if enrollment.exam_score is not None:
                course_scores[enrollment.course_id]['exam_scores'].append(enrollment.exam_score)
            if enrollment.performance_score is not None:
                course_scores[enrollment.course_id]['performance_scores'].append(enrollment.performance_score)
        
        avg_scores = []
        for course_id, scores_data in course_scores.items():
            course = self.course_repo.get_by_id(course_id)
            if course and scores_data['exam_scores']:
                avg_exam = sum(scores_data['exam_scores']) / len(scores_data['exam_scores'])
                avg_performance = (
                    sum(scores_data['performance_scores']) / len(scores_data['performance_scores']) 
                    if scores_data['performance_scores'] 
                    else None
                )
                
                avg_scores.append({
                    'course_name': course.name,
                    'avg_exam_score': round(avg_exam, 2),
                    'avg_performance_score': round(avg_performance, 2) if avg_performance else 'N/A'
                })
        
        # 奖励处分概览
        rp_summary = {}
        for record in self.reward_punishment_repo.get_all():
            rp_type = record.type
            rp_summary[rp_type] = rp_summary.get(rp_type, 0) + 1
        
        # 将字典转换为列表格式以便模板使用
        rp_summary_list = []
        for rp_type, count in rp_summary.items():
            rp_summary_list.append({
                'type': rp_type,
                'count': count
            })

        return {
            'total_students': total_students,
            'students_by_gender': students_by_gender_list,
            'total_courses': total_courses,
            'attendance_summary': attendance_summary,
            'avg_scores': avg_scores,
            'rp_summary': rp_summary_list
        }
    
    def get_student_statistics(self, student_id: int) -> Dict[str, Any]:
        """获取学生个人统计信息"""
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return {}
        
        # 成绩数据
        grades_data = []
        for enrollment in self.enrollment_repo.get_by_student_id(student_id):
            if enrollment.exam_score is not None:
                course = self.course_repo.get_by_id(enrollment.course_id)
                if course:
                    total_score = (enrollment.exam_score + enrollment.performance_score) / 2 if enrollment.performance_score else enrollment.exam_score
                    grades_data.append({
                        'course_name': course.name,
                        'exam_score': enrollment.exam_score,
                        'performance_score': enrollment.performance_score,
                        'total_score': round(total_score, 2)
                    })
        
        # 出勤数据
        attendance_records = self.attendance_repo.get_by_student_id(student_id)
        present_count = sum(1 for a in attendance_records if a.status == 'present')
        absent_count = sum(1 for a in attendance_records if a.status == 'absent')
        leave_count = sum(1 for a in attendance_records if a.status == 'leave')
        total_attendance = len(attendance_records)
        attendance_rate = round((present_count / total_attendance) * 100, 2) if total_attendance > 0 else 0
        
        # 奖励处分数据
        rewards = self.reward_punishment_repo.get_by_student_id_and_type(student_id, 'reward')
        punishments = self.reward_punishment_repo.get_by_student_id_and_type(student_id, 'punishment')
        
        return {
            'student': student,
            'grades_data': grades_data,
            'attendance_rate': attendance_rate,
            'present_count': present_count,
            'absent_count': absent_count,
            'leave_count': leave_count,
            'rewards_count': len(rewards),
            'punishments_count': len(punishments)
        }

class ServiceManager:
    """服务管理器，统一管理所有服务实例"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_services()
        return cls._instance
    
    def _init_services(self):
        """初始化所有服务实例"""
        self.user_service = UserService()
        self.student_service = StudentService()
        self.course_service = CourseService()
        self.enrollment_service = EnrollmentService()
        self.attendance_service = AttendanceService()
        self.reward_punishment_service = RewardPunishmentService()
        self.parent_service = ParentService()
        self.notice_service = NoticeService()
        self.schedule_service = ScheduleService()
        self.statistics_service = StatisticsService()

# 全局服务管理器实例
service_manager = ServiceManager()
"""
单元测试：使用项目中已有的函数/类进行校验。
覆盖点：学号唯一性、年龄校验、密码哈希、登录认证、必填字段。
框架：unittest（标准库，无需额外依赖）。
"""
import json
import os
import tempfile
import unittest
from werkzeug.security import generate_password_hash, check_password_hash

from models import Validator, Student
from repositories import StudentRepository
from services import BaseService, UserService


class TestValidations(unittest.TestCase):
    """围绕仓储/服务/验证器的单元测试"""

    def test_student_id_uniqueness_via_repository(self):
        """学号唯一性：StudentRepository.get_by_student_id（白盒场景）"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(json.dumps({"in_memory_data": {"students": []}, "next_id": {}}).encode())
            tmp_path = tmp.name

        repo = StudentRepository(data_file=tmp_path)
        repo.create(Student(id=1, name='张三', gender='男', age=16, student_id='S001'))

        self.assertIsNotNone(repo.get_by_student_id('S001'))  # 已存在 -> 非唯一
        self.assertIsNone(repo.get_by_student_id('S002'))     # 新学号 -> 唯一

        os.remove(tmp_path)

    def test_age_validation_via_validator(self):
        """年龄校验：Validator.validate_student_data 仅正整数通过（白盒场景）"""
        base = {"name": "张三", "gender": "男", "student_id": "S100"}

        ok, _ = Validator.validate_student_data({**base, "age": 18})
        self.assertTrue(ok)

        ok, msg = Validator.validate_student_data({**base, "age": -1})
        self.assertFalse(ok)
        self.assertEqual(msg, '年龄必须为正整数')

        ok, msg = Validator.validate_student_data({**base, "age": 0})
        self.assertFalse(ok)
        self.assertIn('必填项', msg)  # Validator 对 0 判定为缺失

        ok, msg = Validator.validate_student_data({**base, "age": "abc"})
        self.assertFalse(ok)
        self.assertEqual(msg, '年龄必须为正整数')

    def test_password_hashing_with_werkzeug(self):
        """密码哈希：与业务同源的 generate_password_hash/check_password_hash（白盒场景）"""
        pwd = "123456"
        h1 = generate_password_hash(pwd)
        h2 = generate_password_hash(pwd)

        self.assertNotEqual(h1, h2)  # 相同明文多次哈希应不同
        self.assertTrue(check_password_hash(h1, pwd))
        self.assertTrue(check_password_hash(h2, pwd))

    def test_login_validation_via_user_service(self):
        """登录校验：UserService.authenticate_user（黑盒场景）"""
        user_service = UserService()

        # 空用户名/密码 -> 应返回 None（登录失败）
        self.assertIsNone(user_service.authenticate_user('', ''))

        # 错误密码 -> 返回 None（登录失败）
        self.assertIsNone(user_service.authenticate_user('admin', 'wrong_password'))

    def test_required_fields_via_base_service(self):
        """必填字段：BaseService._validate_required_fields（黑盒场景）"""
        base_service = BaseService()
        data = {"name": "张三", "gender": "男", "student_id": "S100"}

        ok, msg = base_service._validate_required_fields(data, ['name', 'gender', 'student_id'])
        self.assertTrue(ok)
        self.assertEqual(msg, '验证通过')

        ok, msg = base_service._validate_required_fields({**data, 'name': ''}, ['name', 'gender', 'student_id'])
        self.assertFalse(ok)
        self.assertIn('为必填项', msg)

        ok, msg = base_service._validate_required_fields({**data, 'gender': ''}, ['name', 'gender', 'student_id'])
        self.assertFalse(ok)
        self.assertIn('为必填项', msg)

        ok, msg = base_service._validate_required_fields({**data, 'student_id': ''}, ['name', 'gender', 'student_id'])
        self.assertFalse(ok)
        self.assertIn('为必填项', msg)


if __name__ == '__main__':
    unittest.main()
"""Locust 测试脚本：模拟登录 + 核心查询场景。"""

from locust import HttpUser, task, between


# 预置可用账号（teacher/admin），密码与存量 hash 匹配，避免登录失败
USER_POOL = [
    {"username": "admin", "password": "adminpass"},
    {"username": "admin2", "password": "admin2"},
    {"username": "teacher_li", "password": "teacher"},
    {"username": "teacher_wang", "password": "teacher"},
]


class WebsiteUser(HttpUser):
    # 请求间隔 1~3 秒，避免一股脑压满接口
    wait_time = between(0.5, 1)

    def on_start(self) -> None:
        """每个虚拟用户启动时先登录，保持会话 Cookie。"""
        creds = USER_POOL[self.environment.runner.user_count % len(USER_POOL)] if self.environment.runner else USER_POOL[0]
        with self.client.post(
            "/login",
            data={"username": creds["username"], "password": creds["password"]},
            allow_redirects=True,
            name="login",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                print(resp.text)  # 打印响应内容
                resp.failure(f"login failed: status {resp.status_code}")
            elif "请先登录" in resp.text or "用户名或密码错误" in resp.text:
                print(resp.text)  # 打印响应内容
                resp.failure("login failed: wrong credentials or redirected")

    @task(3)
    def view_dashboard(self):
        """访问首页仪表盘。"""
        self.client.get("/", name="dashboard")

    @task(3)
    def list_students(self):
        """教师/管理员查询学生列表（支持搜索）。"""
        self.client.get("/students?search=张三", name="students:list")

    @task(2)
    def list_courses(self):
        """查看课程列表。"""
        self.client.get("/courses", name="courses:list")

    @task(1)
    def list_notices(self):
        """浏览通知列表（部分页面重用首页数据）。"""
        self.client.get("/notices", name="notices:list")
# main.py
from app_factory import run_app, create_app

# 为 Flask CLI 创建应用实例
app = create_app('development')

if __name__ == '__main__':
    # 开发环境运行
    run_app(environment='development', host='127.0.0.1', port=5000)
    
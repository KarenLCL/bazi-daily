"""
PythonAnywhere WSGI 入口
上传到 /home/你的用户名/ 目录后，
在 PythonAnywhere Web 页面配置中指向这个文件
"""
import sys, os

# 添加项目路径
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

# 初始化数据库
from database import init_db
init_db()

# 导入 WSGI 应用
from server import app

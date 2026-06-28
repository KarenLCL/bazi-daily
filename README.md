# 🌟 Karen 专属命理工具

基于你的八字命盘（丙寅 庚寅 辛巳 乙未）和40年人生经历校准的专属命理解读系统。

## 功能

- **每日运势** - 每天早上打开看今日运势评分、事业财运、感情人际、健康提示
- **月度运势** - 查看当月吉日和需谨慎日
- **年度运势** - 年度总览和月度走势
- **日记系统** - 记录每天的实际经历，帮助校准算法
- **反馈系统** - 评价预测准确度，越用越准

## 本地运行

```bash
cd bazi-daily
pip install -r requirements.txt
python app.py
```

然后打开浏览器访问: `http://127.0.0.1:5000`

## 手机访问（同一WiFi）

1. 找到你电脑的局域网IP（macOS: 系统设置 → 网络 → 查看IP）
2. 确保手机和电脑连接同一个WiFi
3. 在手机浏览器打开 `http://你的IP:5000`

## 部署到云服务器（手机随时随地访问）

### 方案一：Render.com（免费，推荐）

1. 注册 https://render.com
2. 点击「New +」→「Web Service」
3. 连接你的 GitHub 仓库，或上传代码
4. 设置：
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. 部署完成后会得到一个 URL，手机可以随时打开

### 方案二：PythonAnywhere（免费）

1. 注册 https://www.pythonanywhere.com
2. 上传代码到文件区
3. 设置 Web app 为 Flask + Python 3
4. WSGI 配置指向 `app`

## 使用流程

1. 🌅 **早上8点** - 打开页面看今日运势
2. 💼 **白天** - 按照宜忌建议行事
3. 🌙 **晚上** - 在「日记」页面记录今天发生的事
4. ⭐ **反馈** - 评价今天的预测准确度
5. 📊 **长期** - 反馈越多，算法越了解你，预测越精准

## 个性化定制

如果你是其他生辰，可以修改 `user_profile.py` 中的八字信息和用神忌神。

## 技术栈

- 后端: Python + Flask + SQLite
- 前端: 纯HTML/CSS/JS（移动端响应式）
- 无外部依赖（只需 Flask）

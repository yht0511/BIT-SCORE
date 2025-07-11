# 网站设置
# 网站的URL
URL = 'https://webvpn.bit.edu.cn/http/77726476706e69737468656265737421fae04c8f69326144300d8db9d6562d'
# token刷新间隔
refresh_interval = 5 # 每隔5秒刷新一次

# 设置
# 学号
student_code='' # 在此处填写学号
password='' # 在此处填写密码
# 邮箱
mail_host='' # 在此处邮箱smtp服务器
mail_user = '' # 在此处邮箱账号
mail_pass = '' # 在此处邮箱密码
mail_targets = [] # 在此处填写接收邮箱
mail_anonymous = [] # 在此处填写接收异常的邮箱
mail_title = "TECLAB-成绩监测系统"
mail_port = 587 # 邮箱端口
mail_ssl = True # 是否使用SSL连接

# 从环境变量中读取设置
import os
if os.getenv("STUDENT_CODE"):
    student_code = os.getenv("STUDENT_CODE")
if os.getenv("PASSWORD"):
    password = os.getenv("PASSWORD")
if os.getenv("MAIL_HOST"):
    mail_host = os.getenv("MAIL_HOST")
if os.getenv("MAIL_USER"):
    mail_user = os.getenv("MAIL_USER")
if os.getenv("MAIL_PASS"):
    mail_pass = os.getenv("MAIL_PASS")
if os.getenv("MAIL_TARGETS"):
    mail_targets = os.getenv("MAIL_TARGETS").split(",")
if os.getenv("MAIL_ANONYMOUS"):
    mail_anonymous = os.getenv("MAIL_ANONYMOUS").split(",")
if os.getenv("MAIL_TITLE"):
    mail_title = os.getenv("MAIL_TITLE")
if os.getenv("REFRESH_INTERVAL"):
    refresh_interval = int(os.getenv("REFRESH_INTERVAL"))
if os.getenv("MAIL_PORT"):
    mail_port = int(os.getenv("MAIL_PORT"))
if os.getenv("MAIL_SSL"):
    mail_ssl = os.getenv("MAIL_SSL").lower() == "true"

if not os.path.exists("data/"):
    os.makedirs("data/")

# 检查设置
if not student_code or not password or not mail_host or not mail_user or not mail_pass or not mail_targets:
    raise Exception("缺少必要设置!请检查在settings.py中填写学号,密码,邮箱各参数或设置环境变量STUDENT_CODE,PASSWORD,MAIL_HOST,MAIL_USER,MAIL_PASS,MAIL_TARGETS")
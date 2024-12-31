# 网站设置
# 网站的URL
URL = 'https://webvpn.bit.edu.cn/http/77726476706e69737468656265737421fae04c8f69326144300d8db9d6562d'
# token刷新间隔
refresh_interval = 30 # 每隔30秒刷新一次

# 设置
# 学号
student_code='' # 在此处填写学号
password='' # 在此处填写密码
# 邮箱
mail_host='' # 在此处邮箱smtp服务器
mail_user = '' # 在此处邮箱账号
mail_pass = '' # 在此处邮箱密码
mail_targets = [""] # 在此处填写接收邮箱
mail_title = "TECLAB-成绩查询系统"

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
if os.getenv("MAIL_TITLE"):
    mail_title = os.getenv("MAIL_TITLE")

# 检查设置
if not student_code or not password or not mail_host or not mail_user or not mail_pass or not mail_targets:
    raise Exception("缺少必要设置!请检查在settings.py中填写学号,密码,邮箱各参数或设置环境变量STUDENT_CODE,PASSWORD,MAIL_HOST,MAIL_USER,MAIL_PASS,MAIL_TARGETS")
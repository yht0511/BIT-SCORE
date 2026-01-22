import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
import settings
import datetime
import json
import os
import time

HISTORY_FILE = "data/history.json"
DATA_FILE = "data/data.json"

def send_emails(subject,message,targets):
    if not targets: return False
    message = MIMEText(message, 'html', 'utf-8')
    message['From'] = formataddr((settings.mail_title, settings.mail_user))
    message['To'] = formataddr(("管理员", targets[0]))
    message['Subject'] = Header(subject, 'utf-8')
    
    for i in range(3):
        try:
            smtpObj = get_smtp_connection()
            if not smtpObj:
                print("Error: 无法连接到邮件服务器")
                continue
            smtpObj.sendmail(settings.mail_user, targets, message.as_string())
            smtpObj.quit()
            print("邮件发送成功")
            return True
        except Exception as e:
            print(e)
    print("Error: 无法发送邮件")
    return False

def get_smtp_connection():
    """根据端口和SSL设置获取SMTP连接"""
    try:
        if settings.mail_port == 465:
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(settings.mail_host, settings.mail_port, context=context, timeout=10)
        elif settings.mail_port == 587:
            server = smtplib.SMTP(settings.mail_host, settings.mail_port, timeout=10)
            if settings.mail_ssl: server.starttls()
        elif settings.mail_port == 25:
            if settings.mail_ssl:
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(settings.mail_host, settings.mail_port, context=context, timeout=10)
            else:
                server = smtplib.SMTP(settings.mail_host, settings.mail_port, timeout=10)
        else:
            raise ValueError("不支持的邮件端口: {}".format(settings.mail_port))
        
        server.login(settings.mail_user, settings.mail_pass)
        return server
    except Exception as e:
        print(f"邮件服务器连接失败: {e}")
        return None

def send_emails_setup(targets):
    subject="TECLAB-成绩监测系统"
    message="""<!DOCTYPE html>
        <html lang="zh-cn">
        <head>
        <meta charset="UTF-8">
        <title>TECLAB 成绩监测系统已启动</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
            background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif;
            margin: 0;
            padding: 0;
            }
            .container {
            background: rgba(255,255,255,0.95);
            max-width: 480px;
            margin: 40px auto;
            border-radius: 16px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08);
            padding: 32px 28px 24px 28px;
            text-align: center;
            }
            .title {
            font-size: 1.6em;
            font-weight: bold;
            color: #2b5876;
            margin-bottom: 12px;
            }
            .desc {
            color: #555;
            margin-bottom: 18px;
            font-size: 1.1em;
            }
            .github-link {
            display: inline-block;
            margin: 12px 0 24px 0;
            padding: 8px 18px;
            background: #24292f;
            color: #fff;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            transition: background 0.2s;
            }
            .github-link:hover {
            background: #444c56;
            }
            .info-block {
            background: #f5f7fa;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 18px;
            color: #333;
            font-size: 1em;
            text-align: left;
            }
            .label {
            font-weight: 500;
            color: #2b5876;
            }
            .footer {
            color: #aaa;
            font-size: 0.95em;
            margin-top: 18px;
            text-align: center;
            }
            select {
            padding: 4px 10px;
            border-radius: 4px;
            border: 1px solid #b0c4de;
            background: #fff;
            font-size: 1em;
            margin-left: 8px;
            }
            #semester {
                color:black;
            }
        </style>
        </head>
        <body>
        <div class="container">
            <div class="title">TECLAB 成绩监测系统已启动</div>
            <div class="desc">由杨浩天开发的北理工成绩检测程序.</div>
            <a class="github-link" href="https://github.com/yht0511/BIT-SCORE" target="_blank">
            查看项目 GitHub
            </a>
            <div class="info-block">
            <div><span class="label">当前时间：</span><span id="current-time">{current-time}</span></div>
            <div style="margin-top:10px;">
                <span class="label">学期：</span>
                <span id="semester">{semester}</span>
            </div>
            <div style="margin-top:10px;">
                <span class="label">当前用户：</span>
                <span id="user-type">{user}</span>
            </div>
            </div>
            <div class="footer">
            &copy; 2025 TECLAB | BIT-SCORE 成绩监测系统
            </div>
        </div>
        </body>
        </html>
        """
    message=message.replace("{current-time}",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    message=message.replace("{semester}",get_current_kksj())
    message=message.replace("{user}",settings.student_code if settings.student_code else "未设置学号")
    send_emails(subject,message,targets)

def send_emails_update_basic(score,student,course,credit,average,max,class_proportion,major_proportion,school_proportion):
    message="""<!DOCTYPE html>
<html lang="zh-cn">
<head>
  <meta charset="UTF-8">
  <title>成绩更新通知</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      background: linear-gradient(120deg, #f6d365 0%, #fda085 100%);
      font-family: 'Segoe UI', 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif;
      margin: 0;
      padding: 0;
    }
    .container {
      background: rgba(255,255,255,0.96);
      max-width: 420px;
      margin: 40px auto;
      border-radius: 14px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.10);
      padding: 30px 24px 22px 24px;
    }
    .title {
      font-size: 1.4em;
      font-weight: bold;
      color: #d35400
      margin: 0 0 12px 0;
    }
    .info-list li {
      padding: 8px 0;
      border-bottom: 1px solid #f2e9e1;
      font-size: 1.05em;
      color: #444;
    }
    .info-list li:last-child {
      border-bottom: none;
    }
    .label {
      color: #d35400;
      font-weight: 500;
      margin-right: 6px;
    }
    .footer {
            color: #aaa;
            font-size: 0.95em;
            margin-top: 18px;
            text-align: center;
            }
  </style>
</head>
<body>
  <div class="container">
    <div class="title">成绩更新：{{ course }}</div>
    <ul class="info-list">
      <li><span class="label">成绩：</span>{{ score }}</li>
      <li><span class="label">姓名：</span>{{ student }}</li>
      <li><span class="label">课程：</span>{{ course }}</li>
      <li><span class="label">学分：</span>{{ credit }}</li>
      <li><span class="label">平均分：</span>{{ average }}</li>
      <li><span class="label">最高分：</span>{{ max }}</li>
      <li><span class="label">班级排名：</span>{{ class_proportion }}</li>
      <li><span class="label">专业排名：</span>{{ major_proportion }}</li>
      <li><span class="label">全体排名：</span>{{ school_proportion }}</li>
    </ul>
    <div class="footer">
    更新时间：{{ update_time }}
    <br/>
            &copy; 2025 TECLAB | BIT-SCORE 成绩监测系统
            </div>
  </div>
</body>
</html>"""
    message=message.replace("{{ score }}",score)
    message=message.replace("{{ student }}",student)
    message=message.replace("{{ course }}",course)
    message=message.replace("{{ credit }}",credit)
    message=message.replace("{{ average }}",average if average else "无")
    message=message.replace("{{ max }}",max if max else "无")
    message=message.replace("{{ class_proportion }}",class_proportion if class_proportion else "无")
    message=message.replace("{{ major_proportion }}",major_proportion if major_proportion else "无")
    message=message.replace("{{ school_proportion }}",school_proportion if school_proportion else "无")
    message=message.replace("{{ update_time }}",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    send_emails(f"[BIT-SCORE] 成绩更新:{course}",message,settings.mail_targets)

def send_emails_anonymous(course,credit,average,max):
    message="""<!DOCTYPE html>
<html lang="zh-cn">
<head>
  <meta charset="UTF-8">
  <title>成绩更新通知</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      background: linear-gradient(120deg, #f6d365 0%, #fda085 100%);
      font-family: 'Segoe UI', 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif;
      margin: 0;
      padding: 0;
    }
    .container {
      background: rgba(255,255,255,0.96);
      max-width: 420px;
      margin: 40px auto;
      border-radius: 14px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.10);
      padding: 30px 24px 22px 24px;
    }
    .title {
      font-size: 1.4em;
      font-weight: bold;
      color: #d35400;
      margin-bottom: 18px;
      text-align: center;
    }
    .info-list {
      list-style: none;
      padding: 0;
      margin: 0 0 12px 0;
    }
    .info-list li {
      padding: 8px 0;
      border-bottom: 1px solid #f2e9e1;
      font-size: 1.05em;
      color: #444;
    }
    .info-list li:last-child {
      border-bottom: none;
    }
    .label {
      color: #d35400;
      font-weight: 500;
      margin-right: 6px;
    }
    .footer {
            color: #aaa;
            font-size: 0.95em;
            margin-top: 18px;
            text-align: center;
            }
  </style>
</head>
<body>
  <div class="container">
    <div class="title">成绩更新：{{ course }}</div>
    <ul class="info-list">
      <li><span class="label">课程：</span>{{ course }}</li>
      <li><span class="label">学分：</span>{{ credit }}</li>
      <li><span class="label">平均分：</span>{{ average }}</li>
      <li><span class="label">最高分：</span>{{ max }}</li>
    </ul>
    <div class="footer">
    更新时间：{{ update_time }}
    <br/>
            &copy; 2025 TECLAB | BIT-SCORE 成绩监测系统
    </div>
  </div>
</body>
</html>"""
    message=message.replace("{{ course }}",course)
    message=message.replace("{{ credit }}",credit)
    message=message.replace("{{ average }}",average if average else "无")
    message=message.replace("{{ max }}",max if max else "无")
    message=message.replace("{{ update_time }}",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    send_emails(f"[BIT-SCORE] 成绩更新:{course}",message,settings.mail_anonymous)
    
def send_score(score,student,course,credit,average,max,class_proportion,major_proportion,school_proportion):
    send_emails_update_basic(score,student,course,credit,average,max,class_proportion,major_proportion,school_proportion)
    send_emails_anonymous(course,credit,average,max)

def check_update(last,data):
    updates=[]
    for i in data:
        t=False
        for j in last:
            if i["course"] == j["course"]:
                t=True
                break
        if not t:
            updates.append(i)
    return updates

def get_current_kksj():
    now = datetime.datetime.now()
    year = now.year
    if 10 <= now.month <= 12:
        semester = f"{year}-{year + 1}-1"
    if 1 <= now.month <= 3:
        semester = f"{year - 1}-{year}-1"
    if 4 <= now.month <= 9:
        semester = f"{year - 1}-{year}-2"
    return semester

def get_all_kksj(user):
    if type(user) == dict:
        if 'xznj' in user:
          year = int(user['xznj']) # 入学年份
        elif 'detail' in user and 'xznj' in user['detail']:
          year = int(user['detail']['xznj'])
    else:
        year = int(user[0:4])
    now = datetime.datetime.now()
    semesters = []
    current_year = now.year
    current_month = now.month
    for y in range(year, current_year + 1):
        if y == current_year:
            if current_month >= 10:
                semesters.append(f"{y}-{y + 1}-1")
            if current_month >= 4:
                semesters.append(f"{y - 1}-{y}-2")
        else:
            semesters.append(f"{y}-{y + 1}-1")
            if y + 1 < current_year:
                semesters.append(f"{y}-{y + 1}-2")
    return semesters

def send_credit(student_name, completed_credit, total_credit, offset_credit=0):
    message="""<!DOCTYPE html>
<html lang="zh-cn">
<head>
  <meta charset="UTF-8">
  <title>学分更新通知</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      background: linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%);
      font-family: 'Segoe UI', 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif;
      margin: 0;
      padding: 0;
    }
    .container {
      background: rgba(255,255,255,0.96);
      max-width: 420px;
      margin: 40px auto;
      border-radius: 14px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.10);
      padding: 30px 24px 22px 24px;
    }
    .title {
      font-size: 1.4em;
      font-weight: bold;
      color: #2b5876;
      margin-bottom: 18px;
      text-align: center;
    }
    .info-list {
      list-style: none;
      padding: 0;
      margin: 0 0 12px 0;
    }
    .info-list li {
      padding: 8px 0;
      border-bottom: 1px solid #f2e9e1;
      font-size: 1.05em;
      color: #444;
    }
    .info-list li:last-child {
      border-bottom: none;
    }
    .label {
      color: #2b5876;
      font-weight: 500;
      margin-right: 6px;
    }
    .footer {
            color: #aaa;
            font-size: 0.95em;
            margin-top: 18px;
            text-align: center;
            }
  </style>
</head>
<body>
  <div class="container">
    <div class="title">学分更新通知</div>
    <ul class="info-list">
      <li><span class="label">姓名：</span>{{ student }}</li>
      <li><span class="label">已修学分：</span>{{ completed_credit }}</li>
      <li><span class="label">总学分：</span>{{ total_credit }}</li>
      <li><span class="label">新增学分：</span>{{ offset_credit }}</li>
    </ul>
    <div class="footer">
    更新时间：{{ update_time }}
    <br/>
            &copy; 2025 TECLAB | BIT-SCORE 成绩监测系统
            </div>
  </div>
</body>
</html>"""
    message=message.replace("{{ student }}", str(student_name))
    message=message.replace("{{ completed_credit }}", str(completed_credit))
    message=message.replace("{{ total_credit }}", str(total_credit))
    message=message.replace("{{ offset_credit }}", str(offset_credit))
    message=message.replace("{{ update_time }}",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("发送学分更新邮件...")
    send_emails(f"[BIT-SCORE] 学分更新通知",message,settings.mail_targets)


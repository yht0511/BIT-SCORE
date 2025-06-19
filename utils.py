import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import settings
import datetime

def send_emails(subject,message,targets):
    message = MIMEText(message, 'plain', 'utf-8')
    message['From'] = formataddr((settings.mail_title, settings.mail_user))
    message['To'] = formataddr(("管理员", targets[0]))
    message['Subject'] = Header(subject, 'utf-8')
    
    for i in range(3):
        try:
            smtpObj = smtplib.SMTP(settings.mail_host, 587,timeout=10)
            smtpObj.login(settings.mail_user,settings.mail_pass)  
            smtpObj.sendmail(settings.mail_user, targets, message.as_string())
            print("邮件发送成功")
            return True
        except Exception as e:
            print(e)
    print("Error: 无法发送邮件")
    return False

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

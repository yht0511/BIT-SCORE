import ddddocr
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import settings

def get_captcha(img_path):
    # 创建一个ddddocr对象
    ocr = ddddocr.DdddOcr(show_ad=False)

    # 读取验证码图片的字节数据
    with open(img_path, 'rb') as f:
        img_bytes = f.read()

    # 使用ddddocr进行验证码识别
    result = ocr.classification(img_bytes).upper()

    # 返回识别结果
    return result


def send_email(subject,message):
    message = MIMEText(message, 'plain', 'utf-8')
    message['From'] = formataddr((settings.mail_title, settings.mail_user))
    message['To'] = formataddr(("管理员", settings.mail_targets[0]))
    message['Subject'] = Header(subject, 'utf-8')
    
    for i in range(3):
        try:
            smtpObj = smtplib.SMTP(settings.mail_host, 25,timeout=5)
            # smtpObj.starttls()
            smtpObj.login(settings.mail_user,settings.mail_pass)  
            smtpObj.sendmail(settings.mail_user, settings.mail_targets, message.as_string())
            print("邮件发送成功")
            return True
        except Exception as e:
            print(e)
    print("Error: 无法发送邮件")
    return False
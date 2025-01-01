# 百丽宫的自动成绩查询系统

## 简介

使用自动化程序每隔30s就检查一遍你的成绩是否更新，并使用邮件第一时间通知你~

支持docker一键化部署!

## 使用方式

### DOCKER

#### 自己构建

```bash
git clone https://github.com/yht0511/BIT-SCORE.git
cd BIT-SCORE
docker build -t bit-score:v1 .
docker run -d \
    --name BIT-SCORE \
    --restart=always \
    -e STUDENT_CODE=你的学号 \
    -e PASSWORD=统一身份验证密码 \
    -e MAIL_HOST=SMTP服务器地址 \
    -e MAIL_USER=邮箱用户名 \
    -e MAIL_PASS=邮箱密码 \
    -e MAIL_TARGETS=接收通知的邮箱(以逗号分隔) \
    -e TZ=Asia/Shanghai \
    bit-score:v1
```

#### 直接运行!

```bash
docker run -d \
    --name BIT-SCORE \
    --restart=always \
    -e STUDENT_CODE=你的学号 \
    -e PASSWORD=统一身份验证密码 \
    -e MAIL_HOST=SMTP服务器地址 \
    -e MAIL_USER=邮箱用户名 \
    -e MAIL_PASS=邮箱密码 \
    -e MAIL_TARGETS=接收通知的邮箱(以逗号分隔) \
    -e TZ=Asia/Shanghai \
    yht0511/bit-score:v1
```

#### ENJOY!

程序会立即启动监测，如果网络以及配置没有问题，20s内你将收到来自程序的邮件，包含启动提示、刚更新的几门科目的具体信息（包含成绩、学分、各占比、更新时间等信息）。
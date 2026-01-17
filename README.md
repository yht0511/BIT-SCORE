# 百丽宫的自动成绩查询系统 (今晚出分!)

## 简介

使用自动化程序每隔 5s 就检查一遍你的成绩是否更新，并使用邮件第一时间通知你~

支持 docker 一键化部署!

新增学分检查,在成绩录入的第一时间告知你“今晚出分”!

新增 webui 界面,可视化查看成绩和学分情况.

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
    -e MAIL_PORT=SMTP服务器端口(默认587) \
    -e MAIL_SSL=true \
    -e REFRESH_INTERVAL=每隔几秒查一次(默认1s) \
    -e WEB_PORT=程序对外端口(默认80) \
    -e WEB_PASSWORD=访问程序的密码 \
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
    -e MAIL_PORT=SMTP服务器端口(默认587) \
    -e MAIL_SSL=true \
    -e REFRESH_INTERVAL=每隔几秒查一次(默认1s) \
    -e WEB_PORT=程序对外端口(默认80) \
    -e WEB_PASSWORD=访问程序的密码 \
    -e TZ=Asia/Shanghai \
    yht0511/bit-score:latest
```

#### ENJOY!

程序会立即启动监测，如果网络以及配置没有问题，20s 内你将收到来自程序的邮件，包含启动提示、刚更新的几门科目的具体信息（包含成绩、学分、各占比、更新时间等信息）。

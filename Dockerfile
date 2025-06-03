FROM ubuntu:latest
RUN apt-get update && apt-get install -y python3 python3-pip wget unzip wget curl nano -y
RUN mkdir /Program
WORKDIR /Program
COPY . /Program
# 安装python依赖包
RUN pip3 install -r requirements.txt --break-system-packages
ENTRYPOINT [ "python3", "main.py" ]


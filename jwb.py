import time
import requests
import settings
import utils
import bit_login
from bs4 import BeautifulSoup

class jwb:
    def __init__(self,username=settings.student_code,password=settings.password):
        self.username=username
        self.password=password

        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Host': settings.URL.split("//")[1].split("/")[0],
            'Referer': settings.URL,
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
            'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        self.jxzxehall_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "sec-ch-ua-mobile": "?0"
        }
        self.refresh()
        
    def refresh(self):
        print("登陆教务部...")
        self.jwb_login = bit_login.jwb_login().login(self.username,self.password)
        self.jwb = bit_login.jwb.jwb(self.jwb_login.get_session())
        self.headers["Cookie"]=self.jwb_login.get_result()["cookie"]
        print("✅ 成功")
        print("登陆教学中心...")
        self.jxzxehall_login = bit_login.jxzxehall_login().login(self.username,self.password)
        self.jxzxehall = bit_login.jxzxehall.jxzxehall(self.jxzxehall_login.get_session())
        self.jxzxehall_headers["Cookie"] = self.jxzxehall_login.get_result()["cookie"]
        print("✅ 成功")
        self.student_info = self.get_base_data()
        print(f"登陆成功: {self.student_info['name']} ({self.student_info['student_code']})")


    def get(self,kksj=None,detailed=True):
        try:
            return self.jwb.get_score(kksj,detailed=detailed)
        except:
            self.refresh()
            return self.get(kksj,detailed)
            
    def get_base_data(self):
        try:
            return self.jxzxehall.get_student_data()
        except:
            self.refresh()
            return self.get_base_data()
    
    def check(self,data):
        if "通行密钥认证" in data:
            return False
        return True
    
    def wait_for_update(self,last:dict):
        res=self.get()
        while utils.check_update(last,res)==[]:
            res=self.get()
            open("data/log.txt",mode="w",encoding="utf-8").write(f"更新时间:{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())}\nData:{res}\n")
            time.sleep(settings.refresh_interval)
        return res
    
    def wait_for_credit_update(self,last:dict):
        res = self.get_base_data()
        while last['total_credit'] == res['total_credit'] and last['completed_credit'] == res['completed_credit']:
            res = self.get_base_data()
            open("data/log.txt", mode="w", encoding="utf-8").write(f"更新时间:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\nData:{res}\n")
            time.sleep(settings.refresh_interval)
        return res

    def get_all_score(self):
        try:
            return self.jwb.get_all_score()
        except: 
            self.refresh()
            return self.get_all_score()
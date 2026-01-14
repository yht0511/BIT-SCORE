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
        self.headers["Cookie"]=bit_login.jwb_login().login(self.username,self.password)["cookie"]
        self.jxzxehall_headers["Cookie"] = bit_login.jxzxehall_login().login(self.username,self.password)["cookie"]
        print(f"登陆成功: {self.get_base_data()['name']} ({self.get_base_data()['student_code']})")

    def get(self):
        data = {
            'kksj': utils.get_current_kksj(),
            'kcxz': '',
            'kcmc': '',
            'xsfs': 'all',
        }
        response = requests.post(f'{settings.URL}/jsxsd/kscj/cjcx_list', headers=self.headers, data=data)
        if not self.check(response.text):
            self.refresh()
            return self.get()
        return self.parse(response.text)
    
    def get_detail(self,url):
        response = requests.get(url, headers=self.headers)
        if not self.check(response.text):
            self.refresh()
            return self.get_detail(url)
        return self.parse_detail(response.text)
        
    def parse(self,data):
        parser = BeautifulSoup(data, 'html.parser')
        dataList = parser.find(id='dataList')
        dataList = dataList.find_all('tr')
        student_name = parser.find(id='Top1_divLoginName').text
        res=[]
        for data in dataList[1:]:
            data = data.find_all('td')
            t={
                'student':student_name,
                'course':data[3].string,
                'score':data[4].string,
                'credit':data[6].string,
            }
            # 合并
            if data[-1].find('a'):
                t.update(self.get_detail(settings.URL+data[-1].find('a')["onclick"].split("JsMod('")[1].split("'")[0]))
            else:
                t.update({
                    'average': None,
                    'max': None,
                    'class_proportion': None,
                    'major_proportion': None,
                    'school_proportion': None,
                })
            res.append(t)
        return res
    
    def parse_detail(self,data):
        parser = BeautifulSoup(data, 'html.parser')
        dataLists = parser.find_all(id='dataList')
        class_detail=dataLists[1].find_all('tr')[-1]
        class_detail=class_detail.find_all("td")
        self_detail=dataLists[2].find_all("td")
        return {
            'average':class_detail[0].string.split("：")[-1],
            'max':class_detail[1].string.split("：")[-1],
            'class_proportion':self_detail[1].string.split("：")[-1],
            'major_proportion':self_detail[2].string.split("：")[-1],
            'school_proportion':self_detail[3].string.split("：")[-1],
        }
    
    def get_base_data(self):
        response = requests.get(
            'https://jxzxehallapp.bit.edu.cn/jwapp/sys/xsfacx/modules/pyfacxepg/grpyfacx.do',
            headers=self.jxzxehall_headers,
        )
        if not self.check(response.text):
            self.refresh()
            return self.get_base_data()
        res_json = response.json()
        data = {
            "name": res_json["datas"]["grpyfacx"]["rows"][0]["XM"],
            "student_code": res_json["datas"]["grpyfacx"]["rows"][0]["XH"],
            "major": res_json["datas"]["grpyfacx"]["rows"][0]["ZYDM_DISPLAY"],
            "class": res_json["datas"]["grpyfacx"]["rows"][0]["BJDM_DISPLAY"],
            "grade": res_json["datas"]["grpyfacx"]["rows"][0]["XZNJ_DISPLAY"],
            "gender": res_json["datas"]["grpyfacx"]["rows"][0]["XBDM_DISPLAY"],
            "college": res_json["datas"]["grpyfacx"]["rows"][0]["YXDM_DISPLAY"],
            "total_credit": res_json["datas"]["grpyfacx"]["rows"][0]["ZSYQXF"],
            "completed_credit": res_json["datas"]["grpyfacx"]["rows"][0]["YWCXF"],
            "required_credit": res_json["datas"]["grpyfacx"]["rows"][0]["ZSYQXFXSZ"],
            "id": res_json["datas"]["grpyfacx"]["rows"][0]["WID"],
            "detail": {
                "pyfadm": res_json["datas"]["grpyfacx"]["rows"][0]["PYFADM"],
                "zydm": res_json["datas"]["grpyfacx"]["rows"][0]["ZYDM"],
                "xdlxdm": res_json["datas"]["grpyfacx"]["rows"][0]["XDLXDM"],
                "xdlxdm_display": res_json["datas"]["grpyfacx"]["rows"][0]["XDLXDM_DISPLAY"],
                "xbdm": res_json["datas"]["grpyfacx"]["rows"][0]["XBDM"],
                "xbdm_display": res_json["datas"]["grpyfacx"]["rows"][0]["XBDM_DISPLAY"],
                "zydm_display": res_json["datas"]["grpyfacx"]["rows"][0]["ZYDM_DISPLAY"],
                "yxdm": res_json["datas"]["grpyfacx"]["rows"][0]["YXDM"],
                "yxdm_display": res_json["datas"]["grpyfacx"]["rows"][0]["YXDM_DISPLAY"],
                "wxdm": res_json["datas"]["grpyfacx"]["rows"][0]["WID"],
                "xznj": res_json["datas"]["grpyfacx"]["rows"][0]["XZNJ"],
                "xznj_display": res_json["datas"]["grpyfacx"]["rows"][0]["XZNJ_DISPLAY"],
            }
        }
        return data
    
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


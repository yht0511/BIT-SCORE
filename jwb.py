import time
import requests
import settings
import webvpn
from bs4 import BeautifulSoup

class jwb:
    def __init__(self,username=settings.student_code,password=settings.password):
        self.username=username
        self.password=password

        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Origin': 'https://webvpn.bit.edu.cn',
            'Referer': 'https://webvpn.bit.edu.cn/http/77726476706e69737468656265737421fae04c8f69326144300d8db9d6562d/jsxsd/kscj/cjcx_query?Ves632DSdyV=NEW_XSD_XJCJ',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
            'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        
        self.refresh()
        
    def refresh(self):
        self.headers["Cookie"]=webvpn.login(self.username,self.password,settings.URL)

    def get(self):
        data = {
            'kksj': '',
            'kcxz': '',
            'kcmc': '',
            'xsfs': 'all',
        }

        response = requests.post('https://webvpn.bit.edu.cn/http/77726476706e69737468656265737421fae04c8f69326144300d8db9d6562d/jsxsd/kscj/cjcx_list', headers=self.headers, data=data)
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
            t.update(self.get_detail(settings.URL+data[-1].find('a')["onclick"].split("JsMod('")[1].split("'")[0]))
            res.append(t)
            print(t)
        return res
    
    def parse_detail(self,data):
        parser = BeautifulSoup(data, 'html.parser')
        dataLists = parser.find_all(id='dataList')
        class_detail=dataLists[1].find_all('tr')[-1]
        class_detail=class_detail.find_all("td")
        self_detail=dataLists[2].find_all("td")
        return {
            'average':class_detail[0].string,
            'max':class_detail[1].string,
            'class_proportion':class_detail[1].string,
            'major_proportion':self_detail[2].string,
            'school_proportion':self_detail[3].string,
        }
    
    def check(self,data):
        if "滑块验证码" in data:
            return False
        return True
    
    def wait_for_update(self,last:dict):
        res=self.get()
        while res == last:
            time.sleep(settings.refresh_interval)
            res=self.get()
            open("log.txt",mode="w",encoding="utf-8").write(f"更新时间:{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())}\nData:{res}\n")
        return res


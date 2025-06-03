import time
import jwb
import json
import utils

if __name__ == "__main__":
    utils.send_email("程序启动","成绩监测程序已启动.")
    while True:
        try:
            # 读取旧的成绩
            try:
                with open("data.json",mode="r",encoding="utf-8") as f:
                    data = json.load(f)
            except:
                data = []
            j = jwb.jwb()
            while True:
                res=j.wait_for_update(data)
                for i in utils.check_update(data,res):
                    utils.send_email(f"成绩更新:{i["course"]}",f"成绩:{i['score']}\n姓名:{i["student"]}\n课程:{i['course']}\n学分:{i['credit']}\n{i['average']}\n{i['max']}\n{i['class_proportion']}\n{i['major_proportion']}\n{i['school_proportion']}\n更新时间:{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())}")
                data=res
                with open("data.json",mode="w",encoding="utf-8") as f:
                    json.dump(data,f,ensure_ascii=False,indent=4)
        except ZeroDivisionError as e:
            utils.send_email("程序异常",str(e))
            time.sleep(1)

import time
import jwb
import json
import utils
import settings

if __name__ == "__main__":
    utils.send_emails("程序启动","成绩监测程序已启动.",settings.mail_targets+settings.mail_anonymous)
    while True:
        try:
            # 读取旧的成绩
            try:
                with open("data/data.json",mode="r",encoding="utf-8") as f:
                    data = json.load(f)
            except:
                data = []
            t = time.time()
            j = jwb.jwb()
            print(f"登录成功(耗时{time.time()-t:.2f}秒)")
            print(f"程序启动,当前学期:{utils.get_current_kksj()}")
            while True:
                res=j.wait_for_update(data)
                for i in utils.check_update(data,res):
                    utils.send_emails(f"成绩更新:{i['course']}",f"成绩:{i['score']}\n姓名:{i['student']}\n课程:{i['course']}\n学分:{i['credit']}\n{i['average']}\n{i['max']}\n{i['class_proportion']}\n{i['major_proportion']}\n{i['school_proportion']}\n更新时间:{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())}",settings.mail_targets)
                    utils.send_emails(f"成绩更新:{i['course']}",f"课程:{i['course']}\n学分:{i['credit']}\n{i['average']}\n更新时间:{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())}",settings.mail_anonymous)
                data=res
                with open("data/data.json",mode="w",encoding="utf-8") as f:
                    json.dump(data,f,ensure_ascii=False,indent=4)
        except ZeroDivisionError as e:
            utils.send_email("程序异常",str(e))
            time.sleep(1)

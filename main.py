import time
import jwb
import json
import utils
import settings

if __name__ == "__main__":
    utils.send_emails_setup(settings.mail_targets)
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
                    utils.send_score(i['score'],i['student'],i['course'],i['credit'],i['average'],i['max'],i['class_proportion'],i['major_proportion'],i['school_proportion'])
                data=res
                with open("data/data.json",mode="w",encoding="utf-8") as f:
                    json.dump(data,f,ensure_ascii=False,indent=4)
        except ZeroDivisionError as e:
            utils.send_email("程序异常",str(e))
            time.sleep(1)

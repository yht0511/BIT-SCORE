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
                data = {
                    'student': {},
                    'score': [],
                }
            t = time.time()
            j = jwb.jwb()
            print(f"登录成功(耗时{time.time()-t:.2f}秒)")
            print(f"程序启动,当前学期:{utils.get_current_kksj()}")
            
            # 初始化数据（如果为空）
            if not data['student'] or not data['score']:
                print("初始化本地数据...")
                try:
                    data['score'] = j.get()
                    data['student'] = j.get_base_data()
                    with open("data/data.json",mode="w",encoding="utf-8") as f:
                        json.dump(data,f,ensure_ascii=False,indent=4)
                except Exception as e:
                    print(f"初始化数据失败: {e}")

            while True:
                has_change = False
                
                # 检查成绩更新
                try:
                    res1 = j.get()
                    updates = utils.check_update(data["score"], res1)
                    if updates:
                        print(f"检测到 {len(updates)} 条成绩更新")
                        for i in updates:
                            utils.send_score(i['score'],i['student'],i['course'],i['credit'],i['average'],i['max'],i['class_proportion'],i['major_proportion'],i['school_proportion'])
                        data["score"] = res1
                        has_change = True
                except Exception as e:
                    print(f"检查成绩更新时出错: {e}")
                    j.refresh()

                # 检查学分更新
                try:
                    res2 = j.get_base_data()
                    last_student = data.get("student", {})
                    print(res2)
                    # 比较关键字段
                    if str(last_student.get('total_credit')) != str(res2.get('total_credit')) or \
                       str(last_student.get('completed_credit')) != str(res2.get('completed_credit')):
                        print("检测到学分更新")
                        utils.send_credit(res2['name'], res2['completed_credit'], res2['total_credit'])
                        data["student"] = res2
                        has_change = True
                except Exception as e:
                    print(f"检查学分更新时出错: {e}")

                # 如果有更新，保存数据
                if has_change:
                    with open("data/data.json",mode="w",encoding="utf-8") as f:
                        json.dump(data,f,ensure_ascii=False,indent=4)
                
                # 记录日志
                open("data/log.txt",mode="w",encoding="utf-8").write(f"最后检查时间:{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())}\n")
                
                time.sleep(settings.refresh_interval)

        except Exception as e:
            print(f"发生主循环异常: {e}")
            time.sleep(5)

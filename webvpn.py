import os
import requests
import time
import utils
from selenium import webdriver
# 导入BY
from selenium.webdriver.common.by import By
# 导入Keys
from selenium.webdriver.common.keys import Keys


def login(username,password,url="https://webvpn.bit.edu.cn"):
    # 启动selenium
    options = webdriver.ChromeOptions()
    # 无头模式
    options.add_argument('headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3') # 不要输出日志
    browser = webdriver.Chrome(options=options)
    with open('stealth.min.js', mode='r') as f:
        js = f.read()
    # 关键代码
    browser.execute_cdp_cmd(
        cmd_args={'source': js},
        cmd="Page.addScriptToEvaluateOnNewDocument",
    )
    browser.get(url)
    # 输入用户名
    username_input = browser.find_element(By.ID,"username")
    username_input.send_keys(username)
    # 输入密码
    password_input = browser.find_element(By.ID,"password")
    password_input.send_keys(password)
    time.sleep(1) # 等待图片加载
    # 检查验证码
    if browser.execute_script('return $(".captcha")[0].style.display') == "block":
        print("检测到验证码,输入中...")
        # 获取验证码图片
        captcha_img = browser.find_element(By.ID,"captchaImg")
        captcha_img.screenshot("./captcha.png")
        captcha=utils.get_captcha("./captcha.png")
        captcha_input = browser.find_element(By.ID,"captcha")
        captcha_input.send_keys(captcha)
    # 点击登录
    login_button = browser.find_element(By.ID,"login_submit")
    login_button.click()
    time.sleep(1) # 等待登录
    # 检查是否成功登录
    res=browser.execute_script('if($("#showErrorTip")[0]) {return $("#showErrorTip")[0].innerText}return "";')
    if res == "":
        # 获取cookies
        cookies = browser.get_cookies()
        # 保存cookies为字符串
        cookies_str = ""
        for cookie in cookies:
            cookies_str += cookie["name"] + "=" + cookie["value"] + ";"
        # 关闭浏览器
        browser.quit()
        return cookies_str
    # 关闭浏览器
    browser.quit()
    raise Exception("登录失败: "+res)
    

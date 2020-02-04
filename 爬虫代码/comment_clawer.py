# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf8')
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep


class taobao_infos:

    # 对象初始化
    def __init__(self):
        url = "https://login.taobao.com/member/login.jhtml"
        self.url = url

        options = webdriver.ChromeOptions()

        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.browser = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.browser, 10)  # 超时时长为10s

    # 延时操作,并可选择是否弹出窗口提示
    def sleep_and_alert(self, sec, message, is_alert):

        for second in range(sec):
            if (is_alert):
                alert = "alert(\"" + message + ":" + str(sec - second) + "秒\")"
                self.browser.execute_script(alert)
                al = self.browser.switch_to.alert
                sleep(1)
                al.accept()
            else:
                sleep(1)

    # 登录淘宝
    def login(self):

        # 打开网页
        self.browser.get(self.url)

        # 自适应等待，点击密码登录选项
        self.browser.implicitly_wait(30)  # 智能等待，直到网页加载完毕，最长等待时间为30s
        self.browser.find_element_by_xpath('//*[@class="forget-pwd J_Quick2Static"]').click()

        # 自适应等待，点击微博登录宣传
        self.browser.implicitly_wait(30)
        self.browser.find_element_by_xpath('//*[@class="weibo-login"]').click()

        # 自适应等待，输入微博账号
        self.browser.implicitly_wait(30)
        self.browser.find_element_by_name('username').send_keys(weibo_username)

        # 自适应等待，输入微博密码
        self.browser.implicitly_wait(30)
        self.browser.find_element_by_name('password').send_keys(weibo_password)

        # 自适应等待，点击确认登录按钮
        self.browser.implicitly_wait(30)
        self.browser.find_element_by_xpath('//*[@class="btn_tip"]/a/span').click()

        # 直到获取到淘宝会员昵称才能确定是登录成功
        taobao_name = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                      '.site-nav-bd > ul.site-nav-bd-l > li#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-user > a.site-nav-login-info-nick ')))
        # 输出淘宝昵称
    def crawl_comment(self,itemid):
        self.browser.get(itemid)
        comment_file = eval(repr(itemid).replace('/', ''))+'.txt'
        comment = open(comment_file,'w')
        all_handles = self.browser.window_handles
        for handle in all_handles:
            num = 0
            while num < 4:
                texts = self.browser.find_elements_by_class_name('tm-col-master')
                for each in texts:
                    text = each.find_element_by_class_name('tm-rate-fulltxt')
                    print text.text
                    comment.write(text.text+'\n')
                    num = num + 1
        comment.close()

weibo_username = ""  # 改成你的微博账号
weibo_password = ""  # 改成你的微博密码
a = taobao_infos()
a.login()  # 登录
file=open("url.txt",'r')#url.txt保存了需要访问爬取评论的商品页
line=file.readline()
comment=[]
while line:
    comment.append(line.strip())
    line = file.readline()
for i in comment:
    a.crawl_comment(i)
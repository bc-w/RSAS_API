import pycurl
import requests
import smtplib
from io import BytesIO
import urllib
import re
import sys
from xml.dom.minidom import parse
import os
import time
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from time import strftime

class rsas_api:

    def __init__(self):
        pass

    def getip(self):  # 获取资产
        print('开始获取 asset.cctv.tv互联网IP：')
        file2 = open("pubip.txt", "a", encoding='utf-8')
        try:
            for page in range(1, 101):
                jd = '\r %2d%% [%s%s]' #爬虫进度条
                url = "https://asset.cctv.tv/host/?page=" + str(page)
                req = requests.get(url)
                rea_json = req.json()
                a = "▋" * page #已完成进度条
                b = '-' * (100-int(page)) #未完成进度条
                c = (int(page)/100) * 100 #
                print(jd % (c,a,b),end='') #进度条整体显示
                time.sleep(0.5)
                sys.stdout.flush()
                time.sleep(0.05)
                data = rea_json['results']
                for i in data:
                    ip = i['public_ip']
                    if len(ip) != 0:
                        for d in ip:
                            file2.write(d + "\n")
            file2.close()
        except Exception as err:
            print(err)
        print("获取资产完成")

    def quchong(self): # IP去重
        print('开始去重...')
        path = "pubip.txt"
        new_list = []
        for line in open('pubip.txt', 'r+'):
            new_list.append(line)
        new_list2 = list(set(new_list))  # 去重
        new_list2.sort(key=new_list.index)  # 以原list的索引为关键词进行排序
        new_txt = ''.join(new_list2)  # 将新list连接成一个字符串
        with open('newip.txt', 'w') as f:
            f.write(new_txt)
            f.close()
        print('资产去重完毕')
        if os.path.exists(path):
            os.remove(path)

    def ipv4(self): #去除IPV6地址
        file = open("allip.txt", "w", encoding='utf-8')
        with open("newip.txt", "r") as da:
            for line in da:
                ip_list = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", line)
                if len(ip_list) != 0:
                    file.write(str(ip_list[0]) + "\n")
            file.close()
            print("去除IPV6完成")

    def xml_change(self):# 将地址添加进XML文件
        today = datetime.datetime.today()
        month = today.month
        list = []
        with open("allip.txt", "r") as da1:
            for line in da1:
                list.append(line.split('\n'))
            #print(list)
            file6 = open ("hengip.txt", "w", encoding='utf-8')
            for i in list:
                file6.write(str(i[0])+";")
            file6.close()
        with open("hengip.txt", "r") as da2:
            for line in da2:
                str9 = str(line)
        str1 = '''<key name="targets"'''
        str12 = "互联网IP月度扫描"
        file = open("newxm.xml", "w", encoding='utf-8')
        with open("testgreat.xml", "r",encoding="utf-8") as da:
            for line in da:
                if str1 in str(line):
                    file.write('\t'+'\t'+'<key name="targets" value="'+str9+'"/>'+"\n")
                if str12 in str(line):
                    file.write('\t'+'\t'+'<taskname>['+str(month)+'月互联网IP月度扫描]</taskname>'+"\n")
                else:
                    file.write(str(line))
        file.close()
        print("IP地址填充XML完毕")

    def great_task(self): # 下发扫描任务
        # 扫描设备IP
        host = '10.10.112.239'
        # 全局参数配置
        username = 'admin'
        password = '*******'
        result_format = 'xml'
        # 请求参数（POST）
        # XML路径
        config_xml = 'newxm.xml'
        # 任务类型
        task_type = '1'
        print("开始下发扫描任务")
        url = 'https://' + host + '/api/task/create?username=' + username + '&password=' + password + '&format=' + result_format
        io = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEFUNCTION, io.write)
        curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        curl.setopt(pycurl.SSL_VERIFYHOST, 0)
        # POST请求参数type和config_xml
        curl.setopt(pycurl.HTTPPOST, [('config_xml', (curl.FORM_FILE, config_xml)),
                                      ('type', (curl.FORM_CONTENTS, task_type)),
                                      ])
        curl.perform()
        ret = io.getvalue()
        file = open("response.xml", "w", encoding='utf-8')
        for line in ret.decode("utf-8"):
            file.write(str(line))
        file.close()
        io.close()
        curl.close()

    def read_xml(self): # 读取XML发送邮件
        domTree = parse("response.xml")
        rootNode = domTree.documentElement
        sub = rootNode.getElementsByTagName("ret_code")
        sub1 = rootNode.getElementsByTagName("task_id")
        sub3 = rootNode.getElementsByTagName("ret_msg")
        code = sub[0].firstChild.data
        id = sub1[0].firstChild.data
        msg = sub3[0].firstChild.data
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        username = 'someone@cc.cn'  # 邮件地址
        password = '********'  # 邮件密码
        sender = 'someone@cc.cn'
        receiver = "infosec@cc.cn"
        if code == str(0):
            try:
                subject = '自动扫描任务创建成功'
                msg = MIMEMultipart('mixed')
                msg['Subject'] = subject
                msg['From'] = '绿盟扫描器'
                msg.attach(
                    MIMEText(
                        "Dear all: \r\n\r\n" + str(date) + " 本月互联网IP月度扫描任务创建成功，任务id:" + str(id) + "，扫描完成自动发送报告\r\n\r\n"))
                smtp_server = "smtp.qiye.163.com"
                smtp = smtplib.SMTP_SSL(smtp_server,994)
                smtp.login(username, password)
                smtp.sendmail(sender, receiver, msg.as_string())
                smtp.quit()
                print("扫描任务下发成功，邮件已发送")
            except Exception as err:
                print(err)
        else:
            pass

    def run(self):
        g.getip()
        g.quchong()
        g.ipv4()
        g.xml_change()
        g.great_task()
        g.read_xml()

if __name__ == '__main__':
    g = rsas_api()
    g.run()


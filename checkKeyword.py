import requests
import re
from prettytable import PrettyTable
import yagmail
import datetime
import threading

def check_website_status():
    yag = yagmail.SMTP( user="1111111111@qq.com", password="22222222222", host='smtp.qq.com')
    logs = open('.\\logs.log',encoding='utf-8',mode='a+')
    config = open('D:\\workspace\\PyCharm\checkLinksAutoBuild\\config.txt',encoding='utf-8')

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding':'Accept-Encoding',
        'Accept-Language':'Accept-Language',
        'Connection': 'keep-alive',
        'Cookie': 'enable_undefined=true; C9nvPf17Htt4O=55MsQoQ_cSem2S6FqFURU7xP0DNn3hdzfz9fnEyCW74inD9OPEHbucZZIZJ1BBwXD3fhgtAIK3oDijaamIj.jlG; C9nvPf17Htt4P=cJ3uBC0BF5uDssXJlJL132C4TeDdDpy98T.ruL28_Hpyy2cjfaoWPARfV._bSi9vaqHjTqP8ct0z8xQQbahhCcJi_nYnYLqqCSMBUEzR6NQIouBdPjR.3rRYH5NAs1kd3Ej5JhAKm.Z68MpgP0VZRb4eaiRmGx7mPTE81d5e_3zkdVEQIZ2GYLssFGB31d39fS9r2.4CI72l_r148sLVepv3.ZmhnkImtw5P4wiDLakbbzbQ.o2iJVFEtOqQV.nMkqNm3zsk0_qicdfrBqzLTe.MVZhTv5ZuZXxc7tfU9dN37MUdLJmfwhoAYeVbjj3Oshs3X3FblpHohJJnL.5EwEoHEZxVrDdyB_PP39ZfC0cDIAnzy5.FjSVb2XnxBPin; 849899999d514676a3=db5b19f02871b5caed0ddb84d90821ce',
        'DNT': '1',
        'Host': 'bg.yjj.gxzf.gov.cn',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }

    table = PrettyTable(['系统名称','系统地址','网络状态','耗时(秒)','检查结果'])
    timelap = 0
    code = 0
    isSandMail = 0
    threads = []  # 创建线程列表

    def get_build_time(html):
        tar = '"BUILD_TIME": "(.*?)( - .*)"'#定义要检测的关键字
        tar2 = 'Build Time: (.*?) for (.*)'
        target = re.findall(tar, html)
        target2 = re.findall(tar2, html)
        if target != [] and target2 == []:
            return target
        elif target2 !=[] and target == []:
            return target2
        else:
            return []

    def check(web_title,url):
        try:
            resp = requests.get(url, headers=headers)
            html = resp.text
            code = resp.status_code
            build_time = get_build_time(html)
            if build_time !=[]:
                print(web_title+"\033[0;32;m =="+str(build_time)+"== \033[0m")
            else:
                print(web_title+str(code)+"\033[1;31;m ==存在反爬虫措施需要手工测试==\033[0m"+"\033[0;34;m "+str(url)+"\033[0m")
        except Exception as e:
            err = str(e)
            print(web_title+"\033[1;31;m ==存在反爬虫措施需要手工测试==\033[0m"+"\033[0;34;m "+str(url)+"\033[0m")

    for each_line in config.readlines():
        parts = str(each_line).strip().split(';')
        if len(parts) >= 4:
            web_title = parts[0]
            url = parts[1]
            mans = parts[2]
            man = mans.split(',')
            mailAddrs = parts[3]
            receiver = mailAddrs.split(',')
            #check(web_title,url)
            # 创建线程，目标函数为 check, 参数为 web_title 和 url
            thread = threading.Thread(target=check, args=(web_title, url))
            threads.append(thread)  # 添加到线程列表
            thread.start()  # 启动线程
        else:
            logs.write(str(datetime.datetime.now()) + '\t' + f'配置文件行格式错误，跳过: {each_line.strip()}\n')
            print(f"警告: 配置文件行格式错误，跳过: {each_line.strip()}")

    for thread in threads: # 等待所有线程完成
        thread.join()

    logs.close()
    config.close()

if __name__ == "__main__":
    check_website_status()

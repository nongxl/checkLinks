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
    print_lock = threading.Lock() # 为多线程打印操作创建一个锁

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
                # 使用锁确保多线程打印时输出不会混乱，并用f-string优化代码
                with print_lock:
                    print(f"{web_title}\033[0;32;m =={build_time}== \033[0m")
            else:
                with print_lock:
                    print(f"{web_title}{code}\033[1;31;m ==存在反爬虫措施需要手工测试==\033[0m\033[0;34;m {url}\033[0m")
        except Exception as e:
            err = str(e)
            with print_lock:
                print(f"{web_title}\033[1;31;m ==存在反爬虫措施需要手工测试==\033[0m\033[0;34;m {url}\033[0m")

    for each_line in config.readlines():
        # 清理并分割行数据，rstrip(';') 确保能处理行末尾有分号的情况
        parts = each_line.strip().rstrip(';').split(';')
        if len(parts) != 4:
            logs.write(str(datetime.datetime.now()) + '\t' + f'配置文件行格式错误，跳过: {each_line.strip()}\n')
            print(f"警告: 配置文件行格式错误，跳过: {each_line.strip()}")
            continue

        # 使用您喜欢的序列解包方式进行赋值
        web_title, url, mans, mailAddrs = parts

        # 创建并启动线程
        thread = threading.Thread(target=check, args=(web_title, url))
        threads.append(thread)
        thread.start()

    for thread in threads: # 等待所有线程完成
        thread.join()

    logs.close()
    config.close()

if __name__ == "__main__":
    check_website_status()

from urllib.request import urlopen
from urllib import request
import requests,re,chardet
from prettytable import PrettyTable
import yagmail
import datetime
import time
import ssl
import urllib3
import threading
'''
颜色显示的格式：
\ 033 [显示方式;字体色;背景色m ...... [\ 033 [0m]
显示颜色的参数：
显示方式 	    效果 	    字体色 	    背景色 	    颜色描述
0 	      终端默认设置 	      30 	      40 	      黑色
1 	          高亮显示 	      31 	      41 	      红色
4 	        使用下划线 	      32 	      42 	      绿色
5 	            闪烁 	      33 	      43 	      黄色
7 	          反白显示 	      34 	      44 	      蓝色
8 	           不可见 	      35 	      45 	     紫红色
		                      36 	      46 	     青蓝色
		                      37 	      47 	      白色
'''
#链接邮箱服务器
yag = yagmail.SMTP( user="123456789@qq.com", password="aykzrsxelgzedfbh", host='smtp.qq.com') #注意是否会被当成垃圾邮件

#logs = open('c:\\checkLinks\\logs.log',encoding='utf-8',mode='a+')
logs = open('logs.log',encoding='utf-8',mode='a+')
config = open('config.txt',encoding='utf-8')

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
headers = { 'User-Agent':user_agent }
table = PrettyTable(['系统名称','系统地址','网络状态','耗时(秒)','检查结果']) # 全局表格对象
context=ssl.SSLContext()
urllib3.disable_warnings() #忽略证书错误

def check(url, web_title):
    try:
        start_time = time.time()
        req = request.Request(url, None, headers)
        if url.startswith('https'): #处理https请求
            resp = request.urlopen(req,context=context, timeout=10)
        else: #非https请求
            resp = request.urlopen(req,timeout=10)
        code = resp.getcode()
        timelap = round(time.time() - start_time, 2)
        html = resp.read()
        charset = chardet.detect(html)
        encoding = charset['encoding'] if charset['encoding'] else 'utf-8'
        html_str = str(html, encoding, errors='ignore')
        title = get_title(html_str) or web_title # 如果网页没有标题，则使用配置文件中的标题
        return 'success', [title, url, code, timelap, "\033[0;32;m 连接成功 \033[0m"]
    except Exception as e:
        err = str(e)
        return 'failure', [web_title, url, err, 'N/A', "\033[0;31;m 连接错误 \033[0m"]

#通过正则匹配<title>标签的内容判断网页标题
def get_title(html):
    tar = '<title>.*?</title>'
    tar = re.compile(tar, re.IGNORECASE)#不区分大小写，否则不同编码时<TITLE></TITLE>标签为大写匹配不出来
    target = re.findall(tar,html)
    if target:
        title = target[0]
        #对获取的title做进一步处理，取第七位之后和倒数第八位之前的内容作为网页标题
        title = title[7:-8]
        return title.strip()

def sandMail(web_title,man,receiver):
    try:
        #MSG = '运维邮件：%s 无法访问，请 %s 尽快处理' % (web_title,man)
        MSG = '%s 无法访问，请 %s 尽快处理' % (web_title,man)
        yag.send(receiver,MSG,str(table))
        logs.write(str(datetime.datetime.now()) + '\t' + '运维邮件发送成功,收信人' + str(man) + str(receiver) + '\n' + str(table) + '\n')
    except Exception as sendErr:
        print('邮件发送失败' + str(sendErr))
        logs.write(str(datetime.datetime.now()) + '\t' + '邮件发送失败' + str(sendErr) + '\n' + str(table) + '\n')

webhook = 'https://qyapi.weixin.com/xxxxxxxxxx'
def sendQyWeixin(web_title,man,webhook):
    MSG = '%s 无法访问，请 %s 尽快处理' % (web_title, man)
    data = {
        "msgtype":"text",
        "text":{
            "content":MSG,
        }
    }
    req = requests.post(url=webhook,headers=headers,json=data)
    print(req)

def process_url_in_thread(config_line, table_lock):
    """每个线程处理一个URL的检查、重试和通知逻辑"""
    parts = config_line.strip().split(';')
    if len(parts) < 4:
        return # 跳过格式不正确的行
    web_title, url, mans, mailAddrs = parts
    man = mans.split(',')
    receiver = mailAddrs.split(',')

    for retry in range(3):
        status, row_data = check(url, web_title)
        if status == 'success':
            if retry > 0:
                logs.write(f"{datetime.datetime.now()}\t不稳定 {url}\n")
            with table_lock:
                table.add_row(row_data)
            return # 检查成功，结束此函数
        else: # 检查失败
            logs.write(f"{datetime.datetime.now()}\t检查失败，{10 * (retry + 1)}秒后重试 {url}\n")
            time.sleep(10)

    # 循环结束，意味着3次重试都失败了
    status, final_row_data = check(url, web_title) # 获取最后一次的失败信息
    with table_lock:
        table.add_row(final_row_data)
    logs.write(f"{datetime.datetime.now()}\t重试3次后仍然失败 {url}\n")
    sandMail(web_title, man, receiver)
    # sendQyWeixin(web_title, man, webhook) # 如果需要，也可以在这里发送企业微信通知

if __name__ == '__main__':
    try:
        urlopen('https://www.baidu.com', timeout=5).getcode() # 访问百度测试网络连接
        print(f"{datetime.datetime.now()} \033[1;32;m网络连接正常，开始并发检查...\033[0m")

        threads = []
        table_lock = threading.Lock()
        config_lines = config.readlines()
        config.close()

        for line in config_lines:
            thread = threading.Thread(target=process_url_in_thread, args=(line, table_lock))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join() # 等待所有线程完成

        print(table) # 所有检查完成后，打印最终的表格

    except Exception as e:
        print(f"{datetime.datetime.now()} \033[1;31;m网络检查错误,无法访问外网。请先检查本机网络\033[0m\n{e}")
        logs.write(f"{datetime.datetime.now()}\t网络错误: {e}\n")
    finally:
        logs.write(f"{datetime.datetime.now()}\t检查完成\n")
        logs.close()

from urllib.request import urlopen
from urllib import request
import requests,re,chardet
from prettytable import PrettyTable
import yagmail
import datetime
import time
import ssl
import urllib3
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
table = PrettyTable(['系统名称','系统地址','网络状态','耗时(秒)','检查结果'])
timelap = 0
code = 0
isSandMail = 0
context=ssl.SSLContext()
urllib3.disable_warnings() #忽略证书错误
def check(timelap,url,web_title):
    try:
        req = request.Request(url, None, headers)
        if url[0:5] == 'https': #处理https请求
            resp = request.urlopen(req,context=context, timeout=10)
        else: #非https请求
            resp = request.urlopen(req,timeout=10)
        # 获取状态码
        code = resp.getcode()
        # 获取响应时间
        timelap = requests.get(url,verify=False,timeout=10).elapsed.total_seconds()
        html = resp.read()
        # 识别网页编码方式
        charset = chardet.detect(html)
        # 按网页的编码方式解码，否则会乱码报错
        html = str(html, charset['encoding'])
        title = get_title(html)
        # 将检查结果添加到表格中
        table.add_row([title, url, code, timelap, "\033[0;32;m 连接成功 \033[0m"])
    except Exception as e:
        # 将异常也添加到表格中
        err = str(e)
        table.add_row([web_title, url, err, timelap, "\033[0;31;m 连接错误 \033[0m"])
        return 'checkAgain'

#通过正则匹配<title>标签的内容判断网页标题
def get_title(html):
    tar = '<title>.*?</title>'
    tar = re.compile(tar, re.IGNORECASE)#不区分大小写，否则不同编码时<TITLE></TITLE>标签为大写匹配不出来
    target = re.findall(tar,html)
    if target:
        title = target[0]
        #对获取的title做进一步处理，取第七位之后和倒数第八位之前的内容作为网页标题
        title = title[7:-8]
        return title

def sandMail(web_title,man,receiver):
    try:
        #MSG = '运维邮件：%s 无法访问，请 %s 尽快处理' % (web_title,man)
        MSG = '%s 无法访问，请 %s 尽快处理' % (web_title,man)
        yag.send(receiver,MSG,str(table))
        logs.write(str(datetime.datetime.now()) + '\t' + '运维邮件发送成功,收信人' + str(man) + str(receiver) + '\n' + str(table) + '\n')
    except Exception as sendErr:
        print('邮件发送失败' + str(sendErr))
        logs.write(str(datetime.datetime.now()) + '\t' + '邮件发送失败' + str(sendErr) + '\n' + str(table) + '\n')

try:
    netCheck = urlopen('https://www.baidu.com').getcode()#访问百度测试网络连接
    print(netCheck)
    print(str(datetime.datetime.now())+"\033[1;32;m 网络连接正常，开始检查... \033[0m")
    for each_line in config.readlines():
        web_title = str(each_line).split(';')[0]
        url = str(each_line).split(';')[1]
        mans = str(each_line).split(';')[2]
        man = mans.split(',')
        mailAddrs = str(each_line).split(';')[3]
        receiver = mailAddrs.split(',')
        if check(timelap,url,web_title) == 'checkAgain':
            logs.write(str(datetime.datetime.now()) + '\t' + '10秒后重新检查' + url+'\n')
            time.sleep(10)
            if check(timelap, url,web_title) == 'checkAgain':
                logs.write(str(datetime.datetime.now()) + '\t' + '10秒后重新检查' + url + '\n')
                time.sleep(10)
                if check(timelap, url,web_title) == 'checkAgain':
                    logs.write(str(datetime.datetime.now()) + '\t' + '重新检查' + url + '\n')
                    sandMail(web_title,man,receiver)
                else:
                    logs.write(str(datetime.datetime.now()) + '\t'+'不稳定'+ url + '\n')

except Exception as e:
    #如果不能访问百度，判断为网络错误
    print(str(datetime.datetime.now())+"\033[1;31;m 网络检查错误,不能访问外网。请先检查本机网络 \033[0m\n",e)
    logs.write(str(datetime.datetime.now())+'\t'+'网络错误'+'\n')

#logs.write(str(datetime.datetime.now())+'\t'+'检查完成'+'\n')
logs.close()
config.close()

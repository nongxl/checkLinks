from urllib.request import urlopen
from urllib import request
import requests,re,chardet
from prettytable import PrettyTable

urls = [
    'https://mail.qq.com',
    'https://www.12306.cn/',
    'https://www.ithome.com',
    'https://www.taobao.com',
    'https://www.adobe.com',
    'https://www.csdn.net',
    'http://www.microsoft.com',
    'https://github.com'
    ]

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
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
headers = { 'User-Agent':user_agent }
table = PrettyTable(['编号','系统名称','系统地址','网络状态','耗时(秒)','检查结果'])
timelap = 0
code = 0
try:
    netCheck = urlopen('http://www.baidu.com').getcode()#访问百度测试网络连接
    print("\033[1;32;m 网络连接正常，开始检查... \033[0m")
    for url in urls:
        try:
            req = request.Request(url, None, headers)
            resp = request.urlopen(req)
            #获取状态码
            code = resp.getcode()
            #获取响应时间
            timelap = requests.get(url).elapsed.total_seconds()
            html = resp.read()
            #获取网页编码方式
            charset = chardet.detect(html)
            #按网页的编码方式解码，否则会乱码报错
            html = str(html,charset['encoding'])
            title = get_title(html)
            #将检查结果添加到表格中
            table.add_row([urls.index(url)+1,title,url,code,timelap,"\033[0;32;m 连接成功 \033[0m"])

        except Exception as e:
            #将异常也添加到表格中
            err = str(e)
            table.add_row([urls.index(url) + 1, "null", url, err, timelap, "\033[0;31;m 连接错误 \033[0m"])

except Exception as e:
    #如果不能访问百度，通常就是网络错误
    print("\033[1;31;m 网络检查错误,不能访问外网。请先检查本机网络 \033[0m\n",e)

print(table)

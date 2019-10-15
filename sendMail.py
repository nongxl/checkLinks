class sendMail:
    import yagmail
    #https://www.cnblogs.com/fnng/p/7967213.html
    #设置邮件接收人，可设置群发
    receivers = ['2724223624@qq.com']
    #链接邮箱服务器
    yag = yagmail.SMTP( user="checklinks@163.com", password="passw0rd222", host='smtp.163.com')

    # 邮箱正文
    contents = ['This is the body, and here is just text ',
                'You can find an audio file attached']

    # 发送邮件
    try:
        yag.send(receivers[0], 'subject', contents)
    except Exception as e:
        print(e)


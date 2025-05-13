import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailSender:
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        """
        初始化 EmailSender 类
        :param smtp_server: 邮件服务器地址（如：smtp.163.com 或 smtp.126.com）
        :param smtp_port: 邮件服务器端口（465 或 994）
        :param username: 发件人邮箱
        :param password: 发件人邮箱授权码（网易邮箱需要使用授权码）
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_email(self, from_email: str, to_email: str, subject: str, body: str):
        """
        发送电子邮件
        :param from_email: 发件人邮箱
        :param to_email: 收件人邮箱
        :param subject: 邮件主题
        :param body: 邮件正文
        """
        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))  # 邮件正文内容

        server = None  # 初始化 server 变量

        try:
            # 连接到邮件服务器并发送邮件
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)  # 使用SSL连接
            server.login(self.username, self.password)  # 登录邮件服务器

            # 发送邮件
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            print("邮件发送成功！")

        except Exception as e:
            print(f"发送邮件时发生错误: {e}")

        finally:
            if server:  # 只有在server创建成功后才调用 quit()
                server.quit()  # 关闭连接
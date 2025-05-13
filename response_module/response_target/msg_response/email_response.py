import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
from config.config import *
from utils.logger import log

from response_module.abstract_response import AbstractResponseMessage


class EmailResponse(AbstractResponseMessage):
    def __init__(self, config):
        super().__init__(config)
        self.type = config['type']
        self.smtp_server = config.get('smtp_server')
        self.smtp_port = config.get('smtp_port', 465)
        self.smtp_user = config.get('smtp_user')
        self.smtp_password = config.get('smtp_password')
        self.from_addr = config.get('from_addr', self.smtp_user)
        self.to_addrs = config.get('to_addrs')  # 逗号分隔或 list

    def send(self, message):
        if not ENABLE_EMAIL:
            return False
        if self.type != 'push':
            return False
        
        log.info(f"发送email: {message}")
        if isinstance(self.to_addrs, str):
            to_addrs = [addr.strip() for addr in self.to_addrs.split(',')]
        else:
            to_addrs = self.to_addrs

        try:
            msg = MIMEMultipart()
            msg['From'] = Header(self.from_addr)
            msg['To'] = Header(', '.join(to_addrs))
            msg['Subject'] = Header('Code Review Notification')

            msg.attach(MIMEText(message, 'plain', 'utf-8'))

             # 将 Markdown 内容作为附件（.md 文件）
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(message.encode('utf-8'))  # 将 Markdown 内容作为文件内容
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={"review.md"}')
            msg.attach(part)

            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.from_addr, to_addrs, msg.as_string())
            server.quit()

            return True
        except Exception as e:
            print(f"[EmailResponse] Failed to send email: {e}")
            return False

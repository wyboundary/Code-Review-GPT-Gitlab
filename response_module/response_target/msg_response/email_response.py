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
import markdown
import re

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

    def clean_markdown_headings(self, md_text) -> str:
        """
        去除 Markdown 标题（# 开头）前的多余空格，例如：
        '   ## 标题' -> '## 标题'
        """
        # 匹配以空格开头，后面是1~6个#号，并确保后面还有空格+文字
        return re.sub(r'^\s{1,}(#{1,6})\s+', r'\1 ', md_text, flags=re.MULTILINE)

    def send(self, message):
        if not ENABLE_EMAIL:
            return False
        if self.type != 'push':
            return False
        
        # log.info(f"发送email: {message}")
        if isinstance(self.to_addrs, str):
            to_addrs = [addr.strip() for addr in self.to_addrs.split(',')]
        else:
            to_addrs = self.to_addrs
        log.info(f"[EmailResponse] 收件人: {to_addrs}")
        log.info(f"[EmailResponse] 发件人: {self.from_addr}")
        try:
            cleaned_md = self.clean_markdown_headings(message)
            print(f"[EmailResponse] Cleaned Markdown: {cleaned_md}")
            message_html = markdown.markdown(
                                            cleaned_md,
                                            extensions=[
                                                'extra',         
                                                'tables',    
                                                'fenced_code',           
                                                'sane_lists',
                                                'toc'
                                            ]
                                        )
           
            msg = MIMEMultipart()
            msg['From'] = Header(self.from_addr)
            msg['To'] = Header(', '.join(to_addrs))
            msg['Subject'] = Header('Code Review Notification')

            # ✅ 正文使用 HTML 格式
            msg.attach(MIMEText(message_html, 'html', 'utf-8'))

            # ✅ 附件使用 HTML 文件
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(message_html.encode('utf-8'))
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename=\"review.html\"')
            msg.attach(part)

            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.from_addr, to_addrs, msg.as_string())
            server.quit()

            return True
        except Exception as e:
            print(f"[EmailResponse] Failed to send email: {e}")
            return False

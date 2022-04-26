from datetime import time, datetime
from email.header import decode_header
from email.mime.text import MIMEText
from email.parser import Parser
from email.utils import parseaddr, parsedate
from poplib import POP3
from smtplib import SMTP


class Mail:
    From = ''
    To = ''
    Subject = ''
    Date = ''
    Body = ''

    def __init__(self, From, To, Subject, Date, Body):
        self.From = From
        self.To = To
        self.Subject = Subject
        self.Date = Date
        self.Body = Body

    def __str__(self):
        return f'From: {self.From}\nTo: {self.To}\nSubject: {self.Subject}\nDate: {self.Date}\nBody: {self.Body}'


class MailUtil:
    username = ""
    password = ""
    pop: POP3
    smtp: SMTP

    def __init__(self, pop3host, smtphost, username, password):
        self.username = username
        self.password = password
        self.pop = POP3(pop3host)
        self.pop.set_debuglevel(1)
        self.pop.user(username)
        try:
            self.pop.pass_(password)
            print('POP3 server login success')
        except Exception as e:
            print(e)
            print('POP3 server login failed')
        self.smtp = SMTP(smtphost)
        self.smtp.set_debuglevel(1)
        try:
            self.smtp.login(username, password)
            print('SMTP server login success')
        except Exception as e:
            print(e)
            print('SMTP server login failed')

    def get_mails(self) -> list[Mail]:
        resp, mails, octets = self.pop.list()
        res = []
        for i in range(len(mails)):
            resp, lines, octets = self.pop.retr(i + 1)
            msg_content = b'\r\n'.join(lines).decode('utf-8')
            msg = Parser().parsestr(msg_content)
            mail = self._parser_info(msg)
            res.append(mail)
        res = sorted(res, key=lambda m: m.Date, reverse = True)
        return res

    @staticmethod
    def _decode_str(s):
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value

    @staticmethod
    def _guess_charset(msg):
        charset = msg.get_charset()
        if charset is None:
            content_type = msg.get('Content-Type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = content_type[pos + 8:].strip()
        return charset

    @staticmethod
    def _parser_info(msg, idx=0):
        res = Mail('', '', '', '', '')
        if idx == 0:
            for header in ['From', 'To', 'Subject', 'Date']:
                value = msg.get(header, '')
                if value:
                    if header == 'Subject':
                        value = MailUtil._decode_str(value)
                    elif header == 'Date':
                        value = datetime(*(parsedate(value)[:6]))
                    else:
                        hdr, addr = parseaddr(value)
                        name = MailUtil._decode_str(hdr)
                        value = f'{name} <{addr}>'
                res.__dict__[header] = value
        Body = ''
        if msg.is_multipart():
            parts = msg.get_payload()
            for n, part in enumerate(parts):
                Body += MailUtil._parser_info(part, n)
        else:
            content_type = msg.get_content_type()
            if content_type != 'text/plain':
                return ''
            content = msg.get_payload(decode=True)
            if charset := MailUtil._guess_charset(msg):
                content = content.decode(charset)
            return content
        res.Body = Body
        return res

    def send_mail(self, to_addr, subject, content):
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = self.username
        msg['To'] = to_addr
        msg['Subject'] = subject
        try:
            self.smtp.sendmail(self.username, to_addr, msg.as_string())
            print('send mail success')
        except Exception as e:
            print(e)
            print('send mail failed')

    def __del__(self):
        self.pop.quit()
        self.smtp.quit()


if __name__ == '__main__':
    mailUtil = MailUtil(
        pop3host="pop.163.com",
        smtphost="smtp.163.com",
        username="18873564337@163.com",
        password="BJJTOUKRFYPZRYIS"
    )

    emails = mailUtil.get_mails()
    for email in emails:
        print(email)

    mailUtil.send_mail('2046883927@qq.com', 'test email', 'qwqqq')
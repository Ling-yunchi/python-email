from datetime import time, datetime
from email.header import decode_header
from email.mime.text import MIMEText
from email.parser import Parser
from email.utils import parseaddr, parsedate
from poplib import POP3
from smtplib import SMTP


class Mail:
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
        self.pop.pass_(password)

        self.smtp = SMTP(smtphost)
        self.smtp.set_debuglevel(1)
        self.smtp.login(username, password)

    def get_mails(self) -> list[Mail]:
        resp, mails, octets = self.pop.list()
        res = []
        for i in range(len(mails)):
            resp, lines, octets = self.pop.retr(i + 1)
            msg_content = b'\r\n'.join(lines).decode('utf-8')
            msg = Parser().parsestr(msg_content)
            try:
                mail = self._parser_info(msg)
            except Exception as e:
                print(e)
                continue
            res.append(mail)
        res = sorted(res, key=lambda m: m.Date, reverse=True)
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
        return charset or msg.get('X-CM-HeaderCharset', '').lower() or 'gbk'

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
            res.Body = MailUtil._parser_info(msg, idx + 1)
        elif msg.is_multipart():
            parts = msg.get_payload()
            return ''.join(MailUtil._parser_info(part, idx + 1) for part in parts)
        else:
            content_type = msg.get_content_type()
            if content_type != 'text/plain':
                return ''
            content = msg.get_payload(decode=True)
            if charset := MailUtil._guess_charset(msg):
                content = content.decode(charset)
            return content
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


def get_pop_host(email):
    if '@qq.com' in email:
        return 'pop.qq.com'
    elif '@163.com' in email:
        return 'pop.163.com'
    elif '@126.com' in email:
        return 'pop.126.com'
    elif '@sina.com' in email:
        return 'pop.sina.com'
    elif '@sina.cn' in email:
        return 'pop.sina.cn'
    elif '@gmail.com' in email:
        return 'pop.gmail.com'
    elif '@sohu.com' in email:
        return 'pop.sohu.com'
    elif '@139.com' in email:
        return 'pop.139.com'
    elif '@hotmail.com' in email:
        return 'pop.live.com'
    elif '@foxmail.com' in email:
        return 'pop.foxmail.com'
    else:
        return ''


def get_smtp_host(email):
    if '@qq.com' in email:
        return 'smtp.qq.com'
    elif '@163.com' in email:
        return 'smtp.163.com'
    elif '@126.com' in email:
        return 'smtp.126.com'
    elif '@sina.com' in email:
        return 'smtp.sina.com'
    elif '@sina.cn' in email:
        return 'smtp.sina.cn'
    elif '@gmail.com' in email:
        return 'smtp.gmail.com'
    elif '@sohu.com' in email:
        return 'smtp.sohu.com'
    elif '@139.com' in email:
        return 'smtp.139.com'
    elif '@hotmail.com' in email:
        return 'smtp.live.com'
    elif '@foxmail.com' in email:
        return 'smtp.foxmail.com'
    else:
        return ''


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

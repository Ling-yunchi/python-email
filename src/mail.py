from email.header import decode_header
from email.parser import Parser
from email.utils import parseaddr
from poplib import POP3
from smtplib import SMTP


class Mail:
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

    def get_mails(self):
        resp, mails, octets = self.pop.list()
        res = []
        for i in range(len(mails)):
            resp, lines, octets = self.pop.retr(i + 1)
            msg_content = b'\r\n'.join(lines).decode('utf-8')
            msg = Parser().parsestr(msg_content)
            self._parser_msg(msg)
            self._print_info(msg)
            res.append(msg)
            # self.pop.dele(i + 1)
        res = sorted(res, key=lambda m: m.get('Date'), reverse=True)
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
    def _print_info(msg):
        for header in ['From', 'To', 'Subject']:
            value = msg.get(header, '')
            if value:
                if header == 'Subject':
                    value = Mail._decode_str(value)
                else:
                    hdr, addr = parseaddr(value)
                    name = Mail._decode_str(hdr)
                    value = u'%s <%s>' % (name, addr)
            print('%s: %s' % (header, value))

    @staticmethod
    def _parser_msg(msg):
        idx = 0
        for part in msg.walk():
            filename = part.get_filename()
            content_type = part.get_content_type()
            print('%d: %s' % (idx, content_type))
            print('%d: %s' % (idx, filename))
            charset = Mail._guess_charset(part)
            if filename:
                filename = Mail._decode_str(filename)
                data = part.get_payload(decode=True)
                if filename != 'None' or filename!='':
                    print('Accessory: %s' % filename)
                    with open(filename, 'wb') as f:
                        f.write(data)
            else:
                email_content_type = ''
                content = ''
                if content_type == 'text/plain':
                    email_content_type = 'text'
                elif content_type == 'text/html':
                    email_content_type = 'html'
                if charset:
                    content = part.get_payload(decode=True).decode(charset)
                print("%s %s" % (email_content_type, content))


if __name__ == '__main__':
    mail = Mail(
        pop3host="pop.163.com",
        smtphost="smtp.163.com",
        username="18873564337@163.com",
        password="BJJTOUKRFYPZRYIS"
    )

    print(mail.get_mails())

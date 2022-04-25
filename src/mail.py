from email.header import decode_header
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
        pop = POP3(pop3host)
        pop.user(username)
        pop.pass_(password)
        try:
            print(pop.getwelcome())
        except Exception as e:
            print(e)

    def _decode_charset(self, str):
        value, charset = decode_header(str)[0]
        if charset:
            value = value.decode(charset)
        return value


if __name__ == '__main__':
    mail = Mail(
        pop3host="pop.163.com",
        smtphost="smtp.163.com",
        username="18873564337@163.com",
        password="BJJTOUKRFYPZRYIS"
    )

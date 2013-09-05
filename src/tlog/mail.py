import smtplib
from email.mime.text import MIMEText
from tlog.config import Config

class Mail(object):

    @classmethod
    def send(cls, recipients, subject, message):
        '''
        :param recipients: list of str (email addresses)
        :param subject: str
        :param message: str
        '''
        if not recipients:
            return
        msg = MIMEText(
            message,
            'html'
        )
        subject = '{}: {}'.format(Config.data['notification_prefix'], subject)
        subject = (subject[:72] + '...') if len(subject) > 72 else subject
        msg['From'] = Config.data['email']['from']
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        session = smtplib.SMTP(
            Config.data['email']['server'], 
            Config.data['email']['port']
        )
        if Config.data['email']['use_tls']:
            session.ehlo()
            session.starttls()
            session.ehlo
        session.login(
            Config.data['email']['username'],
            Config.data['email']['password'],
        )
        session.sendmail(
            Config.data['email']['from'],
            recipients,
            msg.as_string()
        )
        session.quit()
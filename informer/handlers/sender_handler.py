from pony.orm import db_session

from abc import ABCMeta, abstractmethod
from viberbot.api.messages.text_message import TextMessage
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .. import viber
from .. import app


from ..handlers import TelegramBotCommand

# print('!!!!!')


class SenderHandlerException(Exception):
    pass


class SenderHandler(metaclass=ABCMeta):

    @abstractmethod
    def send_message(self):
        pass


class ViberSenderHandler(SenderHandler):
    def __init__(self, user, message):
        self.user = user
        self.message = message

    def send_message(self):
        return viber.send_messages(self.user.name, [
            TextMessage(text=self.message)
        ])


class TelegramSenderHandler(SenderHandler):
    def __init__(self, user, message):
        self.user = user
        self.message = message

    def send_message(self):
        return TelegramBotCommand.send_message(self.user.name, self.message)


class EmailSenderHandler(SenderHandler):
    def __init__(self, user, message):
        self.user = user
        self.message = message

    def send_message(self):
        msg = MIMEMultipart()
        msg["FROM"] = "robots@inmormer"
        msg["TO"] = self.user.name
        msg["Subject"] = "Robot Informer"

        body = self.message

        msg.attach(MIMEText(body, "html"))

        smail = smtplib.SMTP('smtp.gmail.com', 587)
        smail.starttls()
        smail.login(**app.config.get('MAIL'))
        smail.sendmail(msg["FROM"], msg["TO"], msg.as_string())
        smail.quit()


class Sender(object):
    def __init__(self):
        self.types = {}

    def add_hooks(cls, name, klass):
        if not name:
            raise SenderHandlerException('Sender must have a name!')

        if not issubclass(klass, SenderHandler):
            raise SenderHandlerException(
                'Class "{}" is not SenderHandler!'.format(klass)
            )
        cls.types[name] = klass

    @db_session
    def get_hook(cls, user, name, *args, **kwargs):
        if user.type not in cls.types:
            raise SenderHandlerException(
                'Hook with name "{}" not found'.format(name))
        klass = cls.types.get(user.type)
        return klass(user, name, *args, **kwargs).send_message()

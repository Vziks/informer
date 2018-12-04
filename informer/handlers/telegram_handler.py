import requests
import json

from pony.orm import db_session, flush
from ..models import Project, User

from .. import app
from abc import ABCMeta, abstractmethod

def format_string(text):
    format_message = """
Доступные проекты:
{}
Что бы подписать наберите
subscribe <имя проекта>
Пример: projects example-backend
""".format(text)
    return format_message


class TelegramBotHandlerException(Exception):
    pass


class TelegramBotCommand(metaclass=ABCMeta):

    @abstractmethod
    def answer(self):
        pass

    @staticmethod
    def send_message(chat_id, text):
        token = app.config.get('TELEGRAM_KEY')
        api_url = "https://api.telegram.org/bot{}/".format(token)
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(api_url + method, params)
        return resp


class SubscribeTelegramBotCommand(TelegramBotCommand):
    def __init__(self, req):
        self.req = json.loads(req.decode("utf-8"))

    @db_session
    def answer(self):
        message = ''

        projects = Project.select().order_by(Project.id)

        for item in projects:
            message = message + item.sys_name + "\n"

        self.send_message(self.req['message']['chat']['id'], message)


class UnSubscribeTelegramBotCommand(TelegramBotCommand):
    def __init__(self, req):
        self.req = json.loads(req.decode("utf-8"))

    @db_session
    def answer(self):

        if self.req['message']['text'].lower().find(' ') != -1:
            _, project_name = self.req['message']['text'].split(" ", 1)
            project = Project.get(sys_name=project_name)
            if project:
                user = User.get(name=str(self.req['message']['from']['id']))
                project.users.remove(user)

                self.send_message(self.req['message']['chat']['id'], 'Вы отписались от проекта {}'.format(project.name))
            else:
                self.send_message(self.req['message']['chat']['id'],
                                  'Проекта с именем {} нет в системе'.format(project_name))

        else:

            user_project = User.get(name=str(self.req['message']['from']['id']))
            if user_project:
                message = 'Ваши подписки:\n'
                for item in user_project.projects:
                    message = message + item.sys_name + "\n"
                self.send_message(self.req['message']['chat']['id'], message)
            else:
                self.send_message(self.req['message']['chat']['id'], "No subscribe")


class ProjectTelegramBotCommand(TelegramBotCommand):
    def __init__(self, req):
        self.req = json.loads(req.decode("utf-8"))

    @db_session
    def answer(self):
        message = ''

        if self.req['message']['text'].lower().find(' ') != -1:
            _, project_name = self.req['message']['text'].split(" ", 1)
            project = Project.get(sys_name=project_name)

            if project:
                user = User.get(name=str(self.req['message']['chat']['id']))
                if not user:
                    user = User(name=str(self.req['message']['chat']['id']), type='telegram')
                    flush()

                project.users.add(user)

                self.send_message(self.req['message']['chat']['id'], 'Вы подписались на проект {}'.format(project.name))
            else:
                self.send_message(self.req['message']['chat']['id'],
                                  'Проекта с именем {} нет в системе'.format(project_name))

        else:
            projects = Project.select().order_by(Project.id)
            for item in projects:
                message = message + item.sys_name + "\n"
            self.send_message(self.req['message']['chat']['id'], format_string(message))


class TelegramBotHandler(object):
    def __init__(self):
        self.types = {}

    def add_types(cls, name, klass):
        if not name:
            raise TelegramBotHandlerException('Bot must have a name!')

        if not issubclass(klass, TelegramBotCommand):
            raise TelegramBotHandlerException(
                'Class "{}" is not TelegramBotCommand!'.format(klass)
            )
        cls.types[name] = klass

    def execute(cls, request, *args, **kwargs):
        json_data = json.loads(request.decode("utf-8"))
        if json_data['message']['text'].lower().find(' ') != -1:
            name, project = json_data['message']['text'].split(" ", 1)
        else:
            name = json_data['message']['text'].lower()
        if name not in cls.types:
            return TelegramBotCommand.send_message(json_data['message']['chat']['id'],
                                                   'Вы использовали не существующую команду!\n'
                                                   'Доступные команды:\n'
                                                   'projects - список доступных проектов\n'
                                                   'subscribe <имя проекта>\n'
                                                   'unsubscribe <имя проекта>')
        klass = cls.types.get(name.lower())
        return klass(request, *args, **kwargs).answer()

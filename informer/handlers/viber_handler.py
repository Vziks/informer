from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberDeliveredRequest
from viberbot.api.viber_requests import ViberSeenRequest
from pony.orm import db_session, flush
from ..models import Project, User

from .. import viber
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


class ViberBotHandlerException(Exception):
    pass


class ViberBotCommand(metaclass=ABCMeta):
    @abstractmethod
    def answer(self):
        pass

    @staticmethod
    def send_message(req, message):
        return viber.send_messages(req.sender.id, [
            TextMessage(text=message)
        ])


class SubscribeViberBotCommand(ViberBotCommand):
    def __init__(self, req):
        self.req = req

    @db_session
    def answer(self):
        message = ''

        projects = Project.select().order_by(Project.id)

        for item in projects:
            message = message + item.sys_name + "\n"
        if isinstance(self.req, ViberMessageRequest):
            self.send_message(self.req, format_string(message))


class ProjectViberBotCommand(ViberBotCommand):
    def __init__(self, req):
        self.req = req

    @db_session
    def answer(self):
        message = ''

        if self.req.message.text.lower().find(' ') != -1:
            _, project_name = self.req.message.text.split(" ", 1)
            project = Project.get(sys_name=project_name)

            if project and isinstance(self.req, ViberMessageRequest):
                user = User.get(name=self.req.sender.id)
                if not user:
                    user = User(name=self.req.sender.id, type='viber')
                    flush()

                project.users.add(user)

                self.send_message(self.req, 'Вы подписались на проект {}'.format(project.name))
            else:
                self.send_message(self.req, 'Проекта с именем {} нет в системе'.format(project_name))

        else:
            projects = Project.select().order_by(Project.id)
            for item in projects:
                message = message + item.sys_name + "\n"
            if isinstance(self.req, ViberMessageRequest):
                self.send_message(self.req, format_string(message))


class UnSubscribeViberBotCommand(ViberBotCommand):
    def __init__(self, req):
        self.req = req

    @db_session
    def answer(self):

        if self.req.message.text.lower().find(' ') != -1:
            _, project_name = self.req.message.text.split(" ", 1)
            project = Project.get(sys_name=project_name)
            if project and isinstance(self.req, ViberMessageRequest):
                user = User.get(name=self.req.sender.id)
                project.users.remove(user)

                self.send_message(self.req, 'Вы отписались от проекта {}'.format(project.name))
            else:
                self.send_message(self.req, 'Проекта с именем {} нет в системе'.format(project_name))

        else:

            user_project = User.get(name=self.req.sender.id)

            message = 'Ваши подписки:\n'
            for item in user_project.projects:
                message = message + item.sys_name + "\n"
            if isinstance(self.req, ViberMessageRequest):
                self.send_message(self.req, message)


class ViberBot(object):
    def __init__(self):
        self.types = {}

    def add_types(cls, name, klass):
        if not name:
            raise ViberBotHandlerException('Bot must have a name!')

        if not issubclass(klass, ViberBotCommand):
            raise ViberBotHandlerException(
                'Class "{}" is not ViberBotCommand!'.format(klass)
            )
        cls.types[name] = klass

    def execute(cls, request, *args, **kwargs):
        if not isinstance(request, (ViberDeliveredRequest, ViberSeenRequest)):

            if request.message.text.lower().find(' ') != -1:
                name, project = request.message.text.split(" ", 1)
            else:
                name = request.message.text.lower()
            if name not in cls.types:
                return ViberBotCommand.send_message(request, 'Вы использовали не существующую команду!\n'
                                                             'Доступные команды:\n'
                                                             'projects - список доступных проектов\n'
                                                             'subscribe <имя проекта>\n'
                                                             'unsubscribe <имя проекта>')
            klass = cls.types.get(name.lower())
            return klass(request, *args, **kwargs).answer()

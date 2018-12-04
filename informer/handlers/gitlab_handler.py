from pony.orm import db_session
from ..models import Project, IncomingTraffic
import json
from abc import ABCMeta, abstractmethod


# print('!!!!')


class GitLabHandlerException(Exception):
    pass


class GitLabHook(metaclass=ABCMeta):
    @abstractmethod
    def run(self):
        pass

    # @staticmethod
    # def send_message(user_id, message):
    #     return viber.send_messages(user_id, [
    #         TextMessage(text=message)
    #     ])


class PushHookGitLab(GitLabHook):
    def __init__(self, req_data):
        self.req_data = req_data

    @db_session
    def run(self):

        json_data = json.loads(self.req_data.decode("utf-8"))
        message = 'Информер: GitLab\n'
        message = message + 'Проект: ' + json_data['project']['name'] + "\n"
        message = message + 'Был сделан Push commit\n'
        project = Project.get(sys_name=json_data['project']['name'])

        IncomingTraffic(type='pushhook', frm='gitlab', value=self.req_data.decode("utf-8"),
                        project=project)

        if project and project.users.count() > 0:
            message = message + "Запушил: " + json_data['user_name'] + "\n"
            message = message + "Содержит коммиты: \n"
            for item in json_data['commits']:
                message = message + item['message'].rstrip('\n') + " Автор " + item['author']['name'] + "\n"
            from .. import sender

            for user in project.users:
                sender.get_hook(user, message)


class MergeRequestHookGitLab(GitLabHook):
    def __init__(self, req_data):
        self.req_data = req_data

    @db_session
    def run(self):

        json_data = json.loads(self.req_data.decode("utf-8"))
        message = 'Информер: GitLab\n'
        message = message + 'Проект: ' + json_data['project']['name'] + "\n"
        message = message + 'Был создан Merge Request\n'
        message = message + "Запушил: " + json_data['user']['name'] + '\n'
        project = Project.get(sys_name=json_data['project']['name'])
        IncomingTraffic(type='mergerequest', frm='gitlab', value=self.req_data.decode("utf-8"),
                        project=project)

        if project and project.users.count() > 0:
            message = \
                message + \
                json_data['object_attributes']['source_branch'] + \
                '->' + \
                json_data['object_attributes']['target_branch'] + '\n'
            from .. import sender
            for user in project.users:
                sender.get_hook(user, message)


class PipelineHookGitLab(GitLabHook):
    def __init__(self, req_data):
        self.req_data = req_data

    @db_session
    def run(self):

        json_data = json.loads(self.req_data.decode("utf-8"))

        message = 'Информер: GitLab\n'
        message = message + 'Проект: ' + json_data['project']['name'] + "\n"
        message = message + 'Статус Pipeline Hook\n'
        message = message + "Запустил: " + json_data['user']['name'] + '\n'
        project = Project.get(sys_name=json_data['project']['name'])
        IncomingTraffic(type='pipeline', frm='gitlab', value=self.req_data.decode("utf-8"),
                        project=project)

        if project and project.users.count() > 0 and json_data['object_attributes']['status'] not in ['running',
                                                                                                      'pending']:
            message = \
                message + \
                'Pipeline: ' + json_data['object_attributes']['status']
            from .. import sender
            for user in project.users:
                sender.get_hook(user, message)


class GitLabWebHook(object):
    def __init__(self):
        self.evens = {}

    def add_evens(cls, name, klass):
        if not name:
            raise GitLabHandlerException('Hook must have a name!')

        if not issubclass(klass, GitLabHook):
            raise GitLabHandlerException(
                'Class "{}" is not GitLabHook!'.format(klass)
            )
        cls.evens[name] = klass

    def get_event(cls, request, *args, **kwargs):
        if request.headers.get('X-Gitlab-Event') not in cls.evens:
            raise GitLabHandlerException(
                'Command with name "{}" not found'.format(request.headers.get('X-Gitlab-Event')))
        klass = cls.evens.get(request.headers.get('X-Gitlab-Event'))
        return klass(request.get_data(), *args, **kwargs).run()

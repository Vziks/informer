from pony.orm import db_session
from ..models import Project, IncomingTraffic
import json
from abc import ABCMeta, abstractmethod



class BitBuketHandlerException(Exception):
    pass


class BitBucketHook(metaclass=ABCMeta):
    @abstractmethod
    def run(self):
        pass

    # @staticmethod
    # def send_message(user_id, message):
    #     return viber.send_messages(user_id, [
    #         TextMessage(text=message)
    #     ])


class PushHookBitBucket(BitBucketHook):
    def __init__(self, req_data):
        self.req_data = req_data

    @db_session
    def run(self):

        json_data = json.loads(self.req_data.decode("utf-8"))
        message = 'Информер: BitBucket\n'
        message = message + 'Проект: ' + json_data['repository']['name'] + "\n"
        message = message + 'Был сделан Push commit\n'
        project = Project.get(sys_name=json_data['repository']['name'])
        traffic = IncomingTraffic(type='mergerequest', frm='bitbucket', value=self.req_data.decode('utf-8'), project=project)
        # print(project)
        if project and project.users.count() > 0:
            message = message + "Запушил: " + json_data['actor']['display_name'] + "\n"
            message = message + "Содержит коммиты: \n"
            for change in json_data['push']['changes']:
                for item in change['commits']:
                    # print(item)
            #         print(type(item))
                    message = message + item['summary']['raw'].rstrip('\n') + " Автор " + item['author']['user']['display_name'] + "\n"
            from .. import sender
            for user in project.users:
                sender.get_hook(user, message)


class MergeRequestHookBitBucket(BitBucketHook):
    def __init__(self, req_data):
        self.req_data = req_data

    @db_session
    def run(self):


        json_data = json.loads(self.req_data.decode("utf-8"))
        message = 'Информер: BitBucket\n'
        message = message + 'Проект: ' + json_data['repository']['name'] + "\n"
        message = message + 'Был создан Merge Request\n'
        message = message + "Запушил: " + json_data['actor']['display_name'] + '\n'
        project = Project.get(sys_name=json_data['repository']['name'])
        traffic = IncomingTraffic(type='mergerequest', frm='bitbucket', value=self.req_data.decode('utf-8'), project=project)

        if project and project.users.count() > 0:

            message = \
                message + \
                json_data['pullrequest']['source']['branch']['name'] + \
                ' -> ' + \
                json_data['pullrequest']['destination']['branch']['name']
            from .. import sender
            for user in project.users:
                sender.get_hook(user, message)


# class PipelineHookGitLab(BitBucketHook):
#     def __init__(self, req_data):
#         self.req_data = req_data
#
#     @db_session
#     def run(self):
#
#         json_data = json.loads(self.req_data.decode("utf-8"))
#
#         message = 'Информер: GitLab\n'
#         message = message + 'Проект: ' + json_data['project']['name'] + "\n"
#         message = message + 'Статус Pipeline Hook\n'
#         message = message + "Запустил: " + json_data['user']['name'] + '\n'
#         project = Project.get(sys_name=json_data['project']['name'])
#
#         if project and project.users.count() > 0 and json_data['object_attributes']['status'] not in ['running', 'pending'] :
#             message = \
#                 message + \
#                 'Pipeline: ' + json_data['object_attributes']['status']
#             from .. import sender
#             for user in project.users:
#                 sender.get_hook(user, message)


class BitBucketWebHook(object):
    def __init__(self):
        self.evens = {}

    def add_evens(cls, name, klass):
        if not name:
            raise BitBuketHandlerException('Hook must have a name!')

        if not issubclass(klass, BitBucketHook):
            raise BitBuketHandlerException(
                'Class "{}" is not BitBucketWebHook!'.format(klass)
            )
        cls.evens[name] = klass

    def get_event(cls, request, *args, **kwargs):
        if request.headers.get('X-Event-Key') not in cls.evens:
            raise BitBuketHandlerException(
                'Command with name "{}" not found'.format(request.headers.get('X-Event-Key')))
        klass = cls.evens.get(request.headers.get('X-Event-Key'))
        # print(klass)
        return klass(request.get_data(), *args, **kwargs).run()

import json
from collections import defaultdict
from ..models import Project, IncomingTraffic
from pony.orm import db_session

import threading


class CodeShipWebHook(object):

    def __init__(self, data):
        self.json_data = json.loads(data.decode("utf-8"))

    def init(self):
        self.selector(self.json_data['build']['status'])

    @db_session
    def error(self):
        _, project_name = self.json_data['build']['project_name'].split("/", 1)
        project = Project.get(sys_name=project_name)
        IncomingTraffic(type='error', frm='codeship', value=json.dumps(self.json_data),
                        project=project)

        message = 'Информер: CodeShip\n'
        message = message + 'Проект: ' + project_name + "\n"
        message = message + 'Статус сборки\n'

        if project and project.users.count() > 0:
            message = message + """
Build {} for new push request in {}@{}
Build number: {}
Short Git ID: {}
Commit message: {}
""".format(
                self.json_data['build']['status'],
                self.json_data['build']['project_full_name'],
                self.json_data['build']['branch'],
                self.json_data['build']['build_id'],
                self.json_data['build']['short_commit_id'],
                self.json_data['build']['message'].replace("\n", "")
            )
            from .. import sender

            for user in project.users:
                sender.get_hook(user, message)

    @db_session
    def success(self):
        _, project_name = self.json_data['build']['project_name'].split("/", 1)
        project = Project.get(sys_name=project_name)
        IncomingTraffic(type='error', frm='codeship', value=json.dumps(self.json_data),
                        project=project)
        message = 'Информер: CodeShip\n'
        message = message + 'Проект: ' + project_name + "\n"
        message = message + 'Статус сборки\n'
        if project and project.users.count() > 0:
            message = message + """
Build {} for new push request in {}@{}
Build number: {}
Short Git ID: {}
Commit message: {}
""".format(
                self.json_data['build']['status'],
                self.json_data['build']['project_full_name'],
                self.json_data['build']['branch'],
                self.json_data['build']['build_id'],
                self.json_data['build']['short_commit_id'],
                self.json_data['build']['message'].replace("\n", "")
            )
            from .. import sender

            for user in project.users:
                sender.get_hook(user, message)

    def selector(self, status):
        sel = defaultdict(lambda: 'status not found', {'success': self.success, 'error': self.error})
        return sel[status]()

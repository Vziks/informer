from pony.orm import (
    Required, Set, LongStr,
    Database,

)

db = Database()


class Project(db.Entity):
    name = Required(str, 255)
    sys_name = Required(str, 32)
    users = Set('User')
    Incomings = Set('IncomingTraffic')


class User(db.Entity):
    name = Required(str, 255, unique=True)
    type = Required(str, 64)
    projects = Set('Project')


class IncomingTraffic(db.Entity):
    type = Required(str, 255)
    frm = Required(str, 255)
    value = Required(LongStr)
    project = Required('Project')

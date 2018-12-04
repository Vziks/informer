from flask import request, render_template, redirect, url_for, abort, Response
from flask.views import MethodView
from pony.orm import db_session, ObjectNotFound, flush

from .. import app
from ..forms import ProjectForm
from ..models import Project, User

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


@app.route('/', methods=['GET'])
@db_session
def main():
    # user = User.get(name="vziks@live.ru")
    # project = Project.get(sys_name="mexx-test")
    # if not user:
    #     user = User(name="vziks@live.ru", type='email')
    #     flush()
    #
    # project.users.add(user)

    # msg = MIMEMultipart()
    # msg["FROM"] = "robots@inmormer"
    # msg["TO"] = 'vziks@live.ru'
    # msg["Subject"] = "Robot Informer"
    #
    # body = 'dscdcsdcsdc'
    #
    # msg.attach(MIMEText(body, "html"))
    #
    # smail = smtplib.SMTP('smtp.gmail.com', 587)
    # smail.starttls()
    # smail.login(app.config.get('MAIL_LOGIN'), app.config.get('MAIL_PASSWORD'))
    # smail.sendmail(app.config.get('MAIL_LOGIN'), msg["TO"], msg.as_string())
    # smail.quit()

    return Response(status=200)

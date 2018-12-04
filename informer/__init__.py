from flask import Flask
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect

from viberbot import Api

from viberbot.api.bot_configuration import BotConfiguration

from .models import db
from .config import config

app = Flask(__name__)
app.config.update(config)

Bootstrap(app)
csrf = CSRFProtect(app)

try:
    db.bind(**app.config['PONY'])
    db.generate_mapping(create_tables=True)
except AttributeError:
    db.disconnect()

viber = Api(BotConfiguration(**app.config['VIBER']))

from .handlers import Sender
from .handlers import ViberSenderHandler, EmailSenderHandler, TelegramSenderHandler

from .controllers import projects_views
from .controllers import incoming_traffic_view
from .controllers import bots_views
from .controllers import webhook_views
from .controllers import api_views

sender = Sender()
sender.add_hooks('viber', ViberSenderHandler)
sender.add_hooks('email', EmailSenderHandler)
# sender.add_hooks('telegram', TelegramSenderHandler)

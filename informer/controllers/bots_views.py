from flask import request, Response

import logging
from .. import app
from .. import viber
from .. import csrf

from ..handlers import ViberBot, SubscribeViberBotCommand, ProjectViberBotCommand, UnSubscribeViberBotCommand

logger = logging.getLogger()


@app.route('/bot/', methods=['POST'])
@app.route('/bot/<path:anything>/', methods=['POST'])
@csrf.exempt
def bot(anything=None):
    if request.headers.get('X-Viber-Content-Signature'):
        if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
            return Response(status=403)

        viber_request = viber.parse_request(request.get_data())
        viberbot = ViberBot()
        viberbot.add_types('projects', SubscribeViberBotCommand)
        viberbot.add_types('subscribe', ProjectViberBotCommand)
        viberbot.add_types('unsubscribe', UnSubscribeViberBotCommand)
        viberbot.execute(viber_request)

    if anything and anything.lower() == 'telegram':
        return "OK"
        # tc = TelegramBotHandler()
        # tc.add_types('projects', SubscribeTelegramBotCommand)
        # tc.add_types('subscribe', ProjectTelegramBotCommand)
        # tc.add_types('unsubscribe', UnSubscribeTelegramBotCommand)
        # tc.execute(request.get_data())
    return Response(status=200)

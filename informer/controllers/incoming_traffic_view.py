from flask import render_template, abort
from flask.views import MethodView
from pony.orm import db_session, ObjectNotFound

from .. import app
from ..models import IncomingTraffic


@app.route('/incoming/show/<int:id>')
@db_session
def incomings_show(id):
    try:
        return render_template('incoming/show.html', incoming_traffic=IncomingTraffic[id])
    except ObjectNotFound:
        abort(404)


class IncomingsList(MethodView):
    decorators = [db_session]

    def get(self):
        return render_template('incoming/list.html', incoming_traffics=IncomingTraffic.select().order_by(IncomingTraffic.id))


app.add_url_rule('/incoming',
                 view_func=IncomingsList.as_view('incomings_list'))

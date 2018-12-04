from flask import request, abort
from flask import jsonify
from pony.orm import db_session, ObjectNotFound, flush

from .. import app
from ..models import Project, User
from .. import csrf




@app.route('/errors', methods=['POST'])
@db_session
@csrf.exempt
def errors():
    if request.method == 'POST':

        data = request.get_json()
        user = User.get(name=data['email'])
        project = Project.get(id=data['id'])
        if not project:
            abort(404)
        if not request.json:
            abort(400)

        if not user:
            user = User(name=data['email'], type='email')
            flush()

        if data['type'] == 'subscribe':
            project.users.add(user)
            status = "create"
            code = 201

        else:
            project.users.remove(user)
            status = "remove"
            code = 202

        response = jsonify(status=status)
        response.status_code = code
        return response
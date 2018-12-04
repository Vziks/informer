from flask import request, render_template, redirect, url_for, abort
from flask.views import MethodView
from pony.orm import db_session, ObjectNotFound, flush

from .. import app
from ..forms import ProjectForm
from ..models import Project


@app.route('/projects/show/<int:id>')
@db_session
def projects_show(id):
    try:
        return render_template('projects/show.html', project=Project[id])
    except ObjectNotFound:
        abort(404)


@app.route('/projects/delete/<int:id>')
@db_session
def projects_delete(id):
    try:
        Project[id].delete()
        return redirect(url_for('projects_list'))
    except ObjectNotFound:
        abort(404)


class ProjectList(MethodView):
    decorators = [db_session]

    def get(self):
        return render_template('projects/list.html', projects=Project.select().order_by(Project.id))


class ProjectAdd(MethodView):
    decorators = [db_session]

    def get(self):
        form = ProjectForm()
        return render_template('projects/add.html', form=form)

    def post(self):
        form = ProjectForm()
        if form.validate_on_submit():
            project = Project(name=form.name.data, sys_name=form.sys_name.data)
            flush()
            return redirect(
                url_for('projects_edit', id=project.id)
            )


class ProjectEdit(MethodView):
    decorators = [db_session]

    def __get_or_404(self, id):
        try:
            return Project[id]
        except ObjectNotFound:
            abort(404)

    def get(self, id):
        project = self.__get_or_404(id)
        form = ProjectForm(obj=project)
        return render_template('projects/edit.html',
                               project=project,
                               form=form)

    def post(self, id):
        project = self.__get_or_404(id)
        form = ProjectForm(obj=project)

        if form.validate_on_submit():
            project.name = form.name.data
            project.sys_name = form.sys_name.data
            return redirect(
                url_for('projects_edit', id=project.id)
            )

        return render_template('projects/edit.html',
                               role=project,
                               form=form)


app.add_url_rule('/projects/edit/<int:id>',
                 view_func=ProjectEdit.as_view('projects_edit'))

app.add_url_rule('/projects/add',
                 view_func=ProjectAdd.as_view('projects_add'))

app.add_url_rule('/projects',
                 view_func=ProjectList.as_view('projects_list'))

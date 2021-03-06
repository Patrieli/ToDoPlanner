from flask import redirect, render_template, request, url_for
from flask_login import login_required, current_user, login_manager

from application import app, db
from application.projects.models import Project
from application.projects.forms import ProjectForm
from application.tasks.models import Task

@app.route("/projects", methods=["GET"])
@login_required
def projects_index():
    return render_template("projects/list.html", projects = Project.query.filter_by(user_id = current_user.id))

@app.route("/projects/create/")
@login_required
def projects_form():
    return render_template("projects/create.html", form = ProjectForm())

@app.route("/projects/", methods=["POST"])
@login_required
def create_project():
    form = ProjectForm(request.form)

    if not form.validate():
        return render_template("projects/create.html", form = form)

    p = Project(form.name.data)
    p.user_id = current_user.id
    p.active = True

    db.session().add(p)
    db.session().commit()

    return render_template("projects/tasks.html", form = ProjectForm(),
    tasks = Task.query.filter_by(user_id = current_user.id).filter(Task.project_id == None).filter(Task.archived == False),
    count = Task.query.filter_by(user_id = current_user.id).filter(Task.project_id == None).filter(Task.archived == False).count(),
    project_id = p.id, project_name = p.name)

@app.route("/projects/<int:project_id>", methods=["GET"])
@login_required
def open_project(project_id):
    return render_template("projects/project.html", project = Project.query.get(project_id),
    tasks = Project.project_tasks(project_id))

@app.route("/projects/tasks/<project_id>", methods=["POST"])
@login_required
def project_tasks(project_id):

    p = Project.query.filter_by(id=project_id).first()   

    task_ids = request.form.getlist('check')
    for task in task_ids:
        t = Task.query.get(task)
        t.project_id = p.id
        db.session().commit()

    return redirect(url_for("projects_index"))

@app.route("/projects/edit/<project_id>", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    if request.method == "GET":
        return render_template("projects/edit.html", form = ProjectForm(),
        tasks = Task.query.filter_by(user_id = current_user.id).filter(Task.project_id == None).filter(Task.archived == False),
        count = Task.query.filter_by(user_id = current_user.id).filter(Task.project_id == None).filter(Task.archived == False).count(),
        project = Project.query.get(project_id),
        project_tasks = Project.project_tasks(project_id),
        tasks_count = len(Project.project_tasks(project_id)))

    form = ProjectForm(request.form)

    if not form.validate():
        return render_template("projects/edit.html", form = form,
        tasks = Task.query.filter_by(user_id = current_user.id).filter(Task.project_id == None).filter(Task.archived == False),
        count = Task.query.filter_by(user_id = current_user.id).filter(Task.project_id == None).filter(Task.archived == False).count(),
        project = Project.query.get(project_id),
        project_tasks = Project.project_tasks(project_id),
        tasks_count = len(Project.project_tasks(project_id)))

    p = Project.query.get(project_id) 

    p.name = form.name.data
    db.session().commit()

    project_task_ids = request.form.getlist('remove_check')
    for p_task in project_task_ids:
        t = Task.query.get(p_task)
        t.project_id = None
        db.session().commit()

    task_ids = request.form.getlist('add_check')
    for task in task_ids:
        t = Task.query.get(task)
        t.project_id = p.id
        db.session().commit()

    return redirect(url_for("open_project", project_id=p.id))

@app.route("/projects/delete/<project_id>", methods=["GET", "POST"])
@login_required
def delete_project(project_id):
    project_tasks = Task.query.filter_by(project_id = project_id)   

    for task in project_tasks:
        t = Task.query.get(task.id)
        t.project_id = None
        db.session().commit()

    p = Project.query.get(project_id)

    db.session().delete(p)
    db.session().commit()

    return redirect(url_for("projects_index"))
from application import db
from application.models import Base

from sqlalchemy.sql import text

class Project(Base):
    name = db.Column(db.String(30), nullable=False)
    active = db.Column(db.Boolean, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    tasks = db.relationship("Task", backref='project', lazy=True)

    def __init__(self, name):
        self.name = name
        self.active = False

    @staticmethod
    def project_tasks(project_id):

        stmt = text("SELECT task.id, task.name, task.deadline, task.state, task.description, COUNT(task.id) AS count FROM project"
                    " INNER JOIN task ON (task.project_id = project.id)"
                    " WHERE (task.project_id = :project_id) "
                    " GROUP BY task.id, task.name, task.deadline, task.state" ).params(project_id=project_id)
        
        res = db.engine.execute(stmt)

        response = []
        for row in res:
            response.append({"id":row[0], "name":row[1], "deadline":row[2], "state":row[3], "description":row[4], "count":row[5]})

        return response
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
    def project_tasks(user_id, project_id):

        stmt = text("SELECT task.name, task.deadline, task.state, COUNT(task.id) AS count FROM project"
                    " INNER JOIN task ON (task.project_id = project.id)"
                    " INNER JOIN user ON (project.user_id = user.id)" 
                    " WHERE (project.user_id = :user_id) AND (task.project_id = :project_id) "
                    " GROUP BY task.name, task.deadline, task.state" ).params(user_id=user_id, project_id=project_id)
        
        res = db.engine.execute(stmt)

        response = []
        for row in res:
            response.append({"name":row[0], "deadline":row[1], "state":row[2], "count":row[3]})

        return response
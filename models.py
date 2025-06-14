from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()


class Todo(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True )
    content = db.Column(db.String, nullable=False)
    date_created = db.Column(db.Date, nullable=False, default=date.today)


    #serialize Todo entries
    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "date_created": self.date_created.isoformat()  # format date as string
        }


    def __repr__(self):
        return f"< Content: {self.content},  Date created: {self.date_created}>"
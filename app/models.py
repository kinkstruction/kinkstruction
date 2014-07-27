import app
from app import db
from datetime import datetime, date


class Task(db.Model):
    __tablename__ = "task"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow(), index=True)
    end_timestamp = db.Column(db.DateTime, default=datetime.utcnow(), index=True)
    description = db.Column(db.Text, nullable=False, index=True)
    requester_id = db.Column(db.Integer, nullable=False)
    doer_id = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    __table_args__ = (
        db.CheckConstraint("requester_id != doer_id"),
    )

    def requester(self):
        return db.session.query(User, Task).filter(self.requester_id == User.id).first()

    def doer(self):
        return db.session.query(User, Task).filter(self.doer_id == User.id).first()

    def __repr__(self):
        return "<Task: Requester: %d, doer: %d, '%r'>" % (self.requester_id, self.doer_id, self.description)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, index=True)
    pw_hash = db.Column(db.Text, index=True)
    email = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow())
    role = db.Column(db.Integer, default=0)
    __table_args__ = (
        db.UniqueConstraint('username'),
        db.UniqueConstraint('email')
    )

    def tasks_todo(self, active=True):
        return [x[1] for x in
                db.session.query(User, Task).filter(User.id == Task.doer_id and Task.is_active == bool(active)).
                    filter(User.id == self.id).all()
                ]

    def tasks_assigned(self, active=True):
        return [x[1] for x in
                    db.session.query(User, Task).filter(User.id == Task.requester_id and Task.is_active == bool(active)).
                        filter(User.id == self.id).all()
                ]

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return "<User '%r'>" % (self.name)
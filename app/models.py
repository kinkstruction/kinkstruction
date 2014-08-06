import app
from app import db
from datetime import datetime, date


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sent_timestamp = db.Column(db.DateTime, default=datetime.utcnow(), index=True)
    to_user_id = db.Column(db.Integer, nullable=False)
    from_user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String, index=True)
    body = db.Column(db.String, nullable=False, index=True)
    is_read = db.Column(db.Boolean, default=False)
    __table_args__ = (
        db.CheckConstraint("to_user_id != from_user_id"),
    )

    def from_user(self):
        user = User.query.filter_by(id=self.from_user_id).first()
        if user is not None:
            return user
        else:
            return None

    def to_user(self):
        user = User.query.filter_by(id=self.to_user_id).first()
        if user is not None:
            return user
        else:
            return None

    def __repr__(self):
        return "<Message: From: %d, to: %d, title: %r>" % (self.from_user_id, self.to_user_id, self.title)


class Task(db.Model):
    __tablename__ = "task"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow(), index=True)
    end_timestamp = db.Column(db.DateTime, default=datetime.utcnow(), index=True)
    description = db.Column(db.String, nullable=False, index=True)
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
    username = db.Column(db.String, index=True)
    pw_hash = db.Column(db.String, index=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(24))
    role = db.Column(db.String(24))
    bio = db.Column(db.String)
    email = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow())
    user_role = db.Column(db.Integer, default=0)
    is_validated = db.Column(db.Boolean, default=False)
    __table_args__ = (
        db.UniqueConstraint('username'),
        db.UniqueConstraint('email'),
        db.CheckConstraint('age is null or (age >= 18 and age <= 100)')
    )

    def get_all_inbox_messages(self):
        return Message.query.filter_by(to_user_id=self.id).order_by(Message.sent_timestamp.desc()).all()

    def get_all_outbox_messages(self):
        return Message.query.filter_by(from_user_id=self.id).order_by(Message.sent_timestamp.desc()).all()

    def num_unread_messages(self):
        return Message.query.filter_by(to_user_id=self.id).filter(not Message.is_read).count()

    def age_gender_role(self):
        return " ".join([str(x) if x is not None else "" for x in [self.age, self.gender, self.role]])

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

import app
from app import db
from datetime import datetime, date


class FriendRequest(db.Model):
    __tablename__ = "friend_requests"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (
        db.CheckConstraint("user_id != friend_id"),
    )


class Friend(db.Model):
    __tablename__ = "friends"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (
        db.CheckConstraint("user_id != friend_id"),
    )


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sent_timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    to_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    from_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
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
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    title = db.Column(db.String, nullable=False, index=True)
    description = db.Column(db.String, nullable=False, index=True)
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    doer_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    tasks_todo = db.relationship('User',
        primaryjoin="User.id == Task.doer_id",
        backref=db.backref('tasks_todo', lazy='dynamic'))

    tasks_assigned = db.relationship('User',
        primaryjoin="User.id == Task.requester_id",
        backref=db.backref('tasks_assigned', lazy='dynamic'))

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
    username = db.Column(db.String, index=True, unique=True)
    pw_hash = db.Column(db.String, index=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(24))
    role = db.Column(db.String(24))
    orientation = db.Column(db.String(24))
    bio = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    user_role = db.Column(db.Integer, default=0)
    is_validated = db.Column(db.Boolean, default=False)
    password_reset_token = db.Column(db.String)
    password_reset_token_expiration = db.Column(db.DateTime)
    users_sending_friend_requests = db.relationship('User',
        secondary="friend_requests",
        primaryjoin=(FriendRequest.friend_id == id),
        secondaryjoin=(FriendRequest.user_id == id),
        backref=db.backref("users_with_pending_friend_requests", lazy="dynamic"),
        lazy="dynamic"
    )
    friends = db.relationship('User',
        secondary="friends",
        primaryjoin=(Friend.user_id == id),
        secondaryjoin=(Friend.friend_id == id),
        lazy="dynamic"
    )

    __table_args__ = (
        db.UniqueConstraint('username'),
        db.UniqueConstraint('email'),
        db.CheckConstraint('age is null or (age >= 18 and age <= 100)')
    )

    def tasks(self):
        return self.tasks_todo.union_all(self.tasks_assigned)

    def inbox_messages(self):
        return Message.query.filter_by(to_user_id=self.id).order_by(Message.sent_timestamp.desc())

    def outbox_messages(self):
        return Message.query.filter_by(from_user_id=self.id).order_by(Message.sent_timestamp.desc())

    def num_unread_messages(self):
        return Message.query.filter_by(to_user_id=self.id).filter(~Message.is_read).count()

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
        return "<User '%r'>" % (self.username)

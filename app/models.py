import app
from app import db
from datetime import datetime, date
from config import TASK_STATUSES
from sqlalchemy import or_, and_


class Point(db.Model):
    __tablename__ = "points"
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"))
    spent = db.Column(db.Integer, default=0)
    awarded = db.Column(db.Integer, default=0)

    user = db.relationship("User", backref=db.backref("points", lazy="dynamic"))
    task = db.relationship("Task", backref=db.backref("points", lazy="dynamic"))

    def issuing_user(self):
        return User.query.filter_by(id=self.task.requester_id).first()

    def __repr__(self):

        if self.task_id:
            return "<Point: Task %d, User: %d, Points: %d>" % (self.task_id, self.user_id, self.points)
        else:
            return "<Point: User: %d, Points: %d>" % (self.user_id, self.points)

    __table_args__ = (
        db.CheckConstraint("spent >= 0 and spent <= points", name="spent_check"),
        db.CheckConstraint("awarded >= 0 and awarded <= points", name="awarded_check")
    )


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


class TaskPost(db.Model):
    __tablename__ = "task_posts"
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    post = db.Column(db.String(140), nullable=False, index=True)

    task = db.relationship('Task',
        primaryjoin="Task.id == TaskPost.task_id",
        backref=db.backref("posts", lazy="dynamic"))

    author = db.relationship('User',
        primaryjoin="User.id == TaskPost.user_id",
        backref=db.backref("task_posts", lazy="dynamic"))


class TaskHistory(db.Model):
    __tablename__ = "task_history"
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False, index=True)
    prev_status = db.Column(db.Integer, nullable=False)
    new_status = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed = db.Column(db.DateTime, index=True)
    title = db.Column(db.String, nullable=False, index=True)
    description = db.Column(db.String, nullable=False, index=True)
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    doer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(db.Integer, default=0)
    log = db.Column(db.String, index=True)
    privacy = db.Column(db.Integer, default=0)

    tasks_todo = db.relationship('User',
        primaryjoin="User.id == Task.doer_id",
        backref=db.backref('tasks_todo', lazy='dynamic'))

    tasks_assigned = db.relationship('User',
        primaryjoin="User.id == Task.requester_id",
        backref=db.backref('tasks_assigned', lazy='dynamic'))

    __table_args__ = (
        db.CheckConstraint("requester_id != doer_id"),
        db.CheckConstraint("status in (" + ",".join([str(x) for x in TASK_STATUSES.keys()]) + ")"),
        db.CheckConstraint("privacy in (0,1,2)", name="privacy_check")
    )

    def requester(self):
        return db.session.query(User, Task).filter(self.requester_id == User.id).first()

    def doer(self):
        return db.session.query(User, Task).filter(self.doer_id == User.id).first()

    def __repr__(self):
        return "<Task: Requester: %d, doer: %d, '%r'>" % (self.requester_id, self.doer_id, self.title)


class UserOptions(db.Model):
    __tablename__ = "user_options"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    profile_privacy = db.Column(db.Integer, default=0)
    default_task_privacy = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.CheckConstraint("profile_privacy in (0,1,2)", name="profile_privacy_check"),
        db.CheckConstraint("default_task_privacy in (0,1,2)", name="default_task_privacy_check")
    )


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
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    options = db.relationship('UserOptions', uselist=False, backref="user")

    doer = db.relationship('Task',
        primaryjoin="User.id == Task.doer_id",
        backref=db.backref('doer'))

    requester = db.relationship('Task',
        primaryjoin="User.id == Task.requester_id",
        backref=db.backref('requester'))

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

    def can_view_profile(self, other):
        if self.id == other.id or other.options.profile_privacy == 0:
            return True

        if other.options.profile_privacy == 1 and self.is_friends_with(other):
            return True

        return False

    def viewable_public_tasks(self):
        return Task.query.filter(
            or_(
                Task.privacy == 0,
                and_(
                    Task.privacy == 1,
                    or_(
                        Task.doer_id.in_([x.id for x in self.friends.all()]),
                        Task.requester_id.in_([x.id for x in self.friends.all()])
                    )
                ),
                and_(
                    Task.privacy == 2,
                    or_(
                        Task.doer_id == self.id,
                        Task.requester_id == self.id
                    )
                )
            )
        )

    def viewable_friend_tasks(self):
        return Task.query.filter(
            or_(
                and_(
                    Task.privacy == 1,
                    or_(
                        Task.doer_id.in_([x.id for x in self.friends.all()]),
                        Task.requester_id.in_([x.id for x in self.friends.all()])
                    )
                ),
                and_(
                    Task.privacy == 2,
                    or_(
                        Task.doer_id == self.id,
                        Task.requester_id == self.id
                    )
                )
            )

        )

    def viewable_private_tasks(self):
        return Task.query.filter(
            and_(
                Task.privacy == 2,
                or_(
                    Task.doer_id == self.id,
                    Task.requester_id == self.id
                )
            )
        )

    def is_friend(self, friend_id):
        return friend_id in [x.id for x in self.friends.all()]

    def is_friends_with(self, other):
        return other.id in [x.id for x in self.friends.all()]

    def tasks(self):
        return self.tasks_todo.union_all(self.tasks_assigned)

    def inbox_messages(self):
        return Message.query.filter_by(to_user_id=self.id).order_by(Message.sent_timestamp.desc())

    def outbox_messages(self):
        return Message.query.filter_by(from_user_id=self.id).order_by(Message.sent_timestamp.desc())

    def num_unread_messages(self):
        return Message.query.filter_by(to_user_id=self.id).filter(~Message.is_read).count()

    def age_gender_orientation_role(self):
        return " ".join(
            [
                str(x) for x in [x for x in [self.age, self.gender, self.orientation, self.role] if x is not None]
            ]
        )

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

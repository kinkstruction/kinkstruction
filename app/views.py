from app import app, db, lm, bcrypt, mailer
from flask import render_template, g, url_for, session, flash, redirect, request, Markup
from flask.ext.login import login_user, logout_user, current_user, login_required, AnonymousUserMixin
from app.models import User, Friend, FriendRequest, Message, Task, TaskPost, Point, TaskHistory
from forms import *
from markdown import markdown
from config import *
from random import choice
import re
import uuid
from datetime import datetime, date, timedelta
import sqlalchemy
from itsdangerous import Signer
from math import floor

signer = Signer(ITSDANGEROUS_SECRET_KEY)

verify_flash_msg = r'You need to verify your email address to continue. Please look for an email from <i>verifications@kinkstruction.com</i>. <a href="/resend_verification_email">Click here to resend the email</a>.'


@lm.user_loader
def loadUser(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user

    # Populate task statuses (lookup dict)
    g.TASK_STATUSES = TASK_STATUSES

    # If we're sent to the root URL with age_verification=1, then set the cookie
    if request.args.get("age_verification"):
        session["kinkstruction.com|18+"] = 1

    # If g.user doesn't point to an actual user, and if we aren't given an ?age_verification=1,
    # then we see if we need to show the 18+ disclaimer...
    if g.user.get_id() is None and not request.args.get("age_verification") and request.path != "/18_years_or_older" and not re.match("^/static", request.path):
        # The key of our cookie is "kinkstruction.com|18+"
        # The value is just 1...we don't care about the value, so much as
        # whether or not the cookie exists.
        # NOTE: By default, the `permanent_session_lifetime` parameter is set
        # to a timedelta of 31 days, hence this will last a month or so.

        if not session.get("kinkstruction.com|18+"):
            return redirect(url_for("age_verification"))

    # Only flash the "You need to verify..." msg if we have a user is not validated, and if the request is not for something static.
    # Of course, don't redirect if we're already going to "not_validated.html"
    if g.user.get_id() is not None and \
            not re.match("^/static/", request.path) and \
            not g.user.is_validated and \
            request.path not in [url_for(x) for x in ["not_validated", "logout", "resend_verification_email", "verify_email"]]:
        return redirect(url_for("not_validated"))


@app.route("/18_years_or_older")
def age_verification():
    return render_template("18_years_or_older.html")


@app.route("/not_validated")
def not_validated():
    return render_template("not_validated.html")


@app.route("/index", methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
@app.route("/index/<int:page>", methods=['GET', 'POST'])
def index(page=1):

    tasks = None
    requested = request.values.get("requested")
    completed = request.values.get("completed")

    last_seen_members = None

    if g.user.is_authenticated():
        if requested:
            if completed:
                tasks = g.user.tasks_assigned.order_by(Task.status).paginate(page, NUM_TASKS_PER_PAGE, False)
            else:
                tasks = g.user.tasks_assigned.filter(Task.status < 3).order_by(Task.status).paginate(page, NUM_TASKS_PER_PAGE, False)
        else:
            if completed:
                tasks = g.user.tasks_todo.order_by(Task.status).paginate(page, NUM_TASKS_PER_PAGE, False)
            else:
                tasks = g.user.tasks_todo.filter(Task.status < 3).order_by(Task.status.desc()).paginate(page, NUM_TASKS_PER_PAGE, False)

        last_seen_members = User.query.filter(User.last_seen.isnot(None)).order_by(User.last_seen.desc()).limit(6)

    return render_template("index.html", tasks=tasks, requested=requested, page=page, completed=completed, last_seen_members=last_seen_members)


@app.route("/options", methods=['GET', 'POST'])
@login_required
def options():

    form = OptionsForm()

    print "\n\n"
    print form.data
    print "\n\n"

    try:
        form.profile_privacy.data = int(form.profile_privacy.data)
    except:
        form.profile_privacy.data = g.user.options.profile_privacy

    try:
        form.default_task_privacy.data = int(form.default_task_privacy.data)
    except:
        form.default_task_privacy.data = g.user.options.default_task_privacy

    if form.validate_on_submit():

        username = form.username.data
        email = form.email.data
        password = form.password.data
        profile_privacy = int(form.profile_privacy.data)
        default_task_privacy = int(form.default_task_privacy.data)

        if username and username != g.user.username:
            if not User.query.filter_by(username=username).count():
                g.user.username = username
            else:
                flash("Sorry, that username is taken.", "error")

        if email and email != g.user.email:
            if not User.query.filter_by(email=email).count():
                g.user.email = email
            else:
                flash("Sorry, that email is taken", "error")

        if password and not bcrypt.check_password_hash(g.user.pw_hash, password):
            g.user.pw_hash = bcrypt.generate_password_hash(password)

        if profile_privacy != g.user.options.profile_privacy:
            g.user.options.profile_privacy = profile_privacy

        if default_task_privacy != g.user.options.default_task_privacy:
            g.user.options.default_task_privacy = default_task_privacy

        print form.friend_request_email_alert
        print form.friend_request_email_alert.data

        for alert_attr in [x for x in dir(g.user.options) if "_email_alert" in x]:

            setattr(g.user.options, alert_attr, getattr(form, alert_attr).data)

        db.session.add(g.user.options)
        db.session.commit()

        db.session.add(g.user)
        db.session.commit()

        flash("Changes updated!", "success")

    else:
        form.username.data = g.user.username
        form.email.data = g.user.email

        for email_attr in [x for x in dir(g.user.options) if "_email_alert" in x]:
            getattr(form, email_attr).data = getattr(g.user.options, email_attr)

        form.profile_privacy.data = g.user.options.profile_privacy
        form.default_task_privacy.data = g.user.options.default_task_privacy

    return render_template("options.html", form=form)


@app.route("/members/<int:page>", methods=['GET', 'POST'])
@app.route("/members", methods=['GET', 'POST'])
@login_required
def members(page=1):

    users = User.query.order_by(User.username).paginate(page, NUM_MEMBERS_PER_PAGE, False)

    return render_template("members.html", users=users)


@app.route("/task/<int:id>", methods=['GET', 'POST'])
@login_required
def view_task(id):
    task = Task.query.filter_by(id=id).first()

    if task is None:
        flash("No such task found!", "error")
        return redirect(url_for("index"))

    page = request.values.get("page")

    if page is None:
        page = 1
    elif page == "last":
        post_count = task.posts.count()

        # If NUM_TASK_POSTS_PER_PAGE does not evenly divide post_count, then
        # proceed as usual: take the quotient, floor it, add 1
        page = int(floor(post_count / NUM_TASK_POSTS_PER_PAGE)) + 1

        # But otherwise, we need to subtract 1 from page in order
        # to avoid having no tasks and just the "add post" form.
        if post_count % NUM_TASK_POSTS_PER_PAGE == 0:
            page -= 1

    else:
        page = int(page)

    posts = task.posts.filter_by(task_id=task.id).order_by(TaskPost.created).paginate(page, NUM_TASK_POSTS_PER_PAGE, False)

    return render_template("view_task.html", task=task, posts=posts)


@app.route("/tasks/public/<int:page>", methods=['GET', 'POST'])
@app.route("/tasks/public", methods=['GET', 'POST'])
@login_required
def all_tasks(page=1):

    tasks = g.user.viewable_public_tasks().order_by(Task.created.desc()).paginate(page, NUM_TASKS_PER_PAGE, False)

    return render_template("task/list.html", tasks=tasks, endpoint="all_tasks")


@app.route("/tasks/friends/<int:page>", methods=['GET', 'POST'])
@app.route("/tasks/friends", methods=['GET', 'POST'])
@login_required
def friend_tasks(page=1):

    tasks = g.user.viewable_friend_tasks().order_by(Task.created.desc()).paginate(page, NUM_TASKS_PER_PAGE, False)

    return render_template("task/list.html", tasks=tasks, endpoint="friend_tasks")


@app.route("/tasks/private/<int:page>", methods=['GET', 'POST'])
@app.route("/tasks/private", methods=['GET', 'POST'])
@login_required
def private_tasks(page=1):
    tasks = g.user.viewable_private_tasks().order_by(Task.created.desc()).paginate(page, NUM_TASKS_PER_PAGE, False)

    return render_template("task/list.html", tasks=tasks, endpoint="private_tasks")


@app.route("/task/add_post/<int:id>", methods=['GET', 'POST'])
@login_required
def add_post_to_task(id):
    task = Task.query.filter_by(id=id).first()

    if task is None:
        flash("No such task found!", "error")
        return redirect(url_for("index"))

    # TODO: Allow tasks to be updated by anyone/friends/only doer and requester
    elif g.user.id != task.doer_id and g.user.id != task.requester_id:
        flash("You are not allowed to update that task!", "error")
    else:
        post = request.values.get("post")

        if post is None or post == "":
            flash("Hmmm, weird...I didn't get the update post for this task that you tried to send...", "warning")
        elif len(post) > 140:
            flash("For some bizarre reason, I received a post update longer than 140 characters. Truncating...", "warning")
            post = post[:140]

        task_post = TaskPost(task_id=id, user_id=g.user.id, post=post)
        db.session.add(task_post)
        db.session.commit()

        flash("Post has been posted. Everything's nice and posty!", "success")

        user = None
        if g.user.id == task.doer_id:
            user = task.requester
        elif g.user.id == task.requester_id:
            user = task.doer

        if user.options.task_new_post_email_alert:
            email_body = render_template("mail/task_post_created.html", user=user, task=task, post=task_post)
            subject = "%s Updated The Task '%s'" % (g.user.username, task.title)

            mailer.send_mail(user.email, subject, email_body)

    return redirect(url_for("view_task", id=id, page="last"))


@app.route("/task/new/<int:id>", methods=['GET', 'POST'])
@login_required
def create_task(id):

    user = User.query.filter_by(id=id).first()
    if user is None:
        flash("No such user!", "error")
        return redirect(url_for("index"))
    elif not g.user.is_friends_with(user):
        flash("You can only create tasks for friends!", "error")
        return redirect(url_for("profile_page", id=id))

    form = CreateTaskForm()

    # AH HA!!!! Need to do this manual coercion to int, otherwise
    # the form is NEVER validated! Gods, this was driving me INSANE!!!
    try:
        form.privacy.data = int(form.privacy.data)
    except:
        form.privacy.data = g.user.options.default_task_privacy

    if form.validate_on_submit():

        title = form.title.data
        description = form.description.data
        privacy = int(form.privacy.data)

        task = Task(title=title, description=description, requester_id=g.user.id, doer_id=id, status=0, privacy=privacy)
        db.session.add(task)
        db.session.commit()

        num_points = form.points.data

        if num_points is None:
            num_points = 0

        pt = Point(user_id=task.doer_id, task_id=task.id, points=num_points)

        db.session.add(pt)
        db.session.commit()

        flash("Task created!", "success")

        if user.options.task_created_email_alert:
            email_body = render_template("mail/new_task.html", task=task)
            subject = "%s Has Created A New Task For You!" % g.user.username

            mailer.send_mail(task.doer.email, subject, email_body)

        return redirect(url_for("view_task", id=task.id))

    form.privacy.data = g.user.options.default_task_privacy

    return render_template("task/new.html", form=form)


@app.route("/task/start/<int:id>", methods=['GET', 'POST'])
@login_required
def task_start(id):

    task = Task.query.filter_by(id=id).first()

    if task is None:
        flash("No such task!", "error")
        return redirect(url_for("index"))

    if TASK_STATUSES[task.status] != "Not Started":
        flash("You can't start a task that has already been started!", "error")
    elif g.user.id != task.doer_id:
        flash("You cannot start a task that was not assigned to you!", "error")
    else:
        th = TaskHistory(task_id=id, prev_status=0, new_status=1)
        db.session.add(th)
        db.session.commit()

        task.status = 1
        db.session.add(task)
        db.session.commit()

        flash("Task '%s' has been started!" % task.title, "success")

        if task.requester.options.task_start_email_alert:
            subject = "%s Has Started Task '%s'" % (task.doer.username, task.title)
            email_body = render_template("mail/task_started.html", task=task)

            mailer.send_mail(task.requester.email, subject, email_body)

    return redirect(url_for("view_task", id=id))


@app.route("/task/complete/<int:id>", methods=['GET', 'POST'])
@login_required
def task_complete(id):

    task = Task.query.filter_by(id=id).first()

    if task is None:
        flash("No such task!", "error")
        return redirect(url_for("index"))

    if TASK_STATUSES[task.status] != "Started":
        flash("You can't complete a task that has a status of '%s'" % TASK_STATUSES[task.status], "error")
    elif g.user.id != task.doer_id:
        flash("You can't complete a task that was not assigned to you!", "error")
    else:

        completed = datetime.utcnow()
        th = TaskHistory(task_id=id, prev_status=1, new_status=2, timestamp=completed)
        db.session.add(th)
        db.session.commit()

        task.status = 2
        task.completed = completed
        db.session.add(task)
        db.session.commit()

        flash("Task '%s' completed!", "success")

        if task.requester.options.task_complete_email_alert:
            subject = "Awaiting Your Approval: %s Has Completed Task '%s'" % (task.doer.username, task.title)
            email_body = render_template("mail/task_doer_completed.html", task=task)
            mailer.send_mail(task.requester.email, subject, email_body)

    return redirect(url_for("view_task", id=id))


@app.route("/task/accept/<int:id>", methods=['GET', 'POST'])
@login_required
def task_accept(id):

    task = Task.query.filter_by(id=id).first()

    if task is None:
        flash("No such task!", "error")
        return redirect(url_for("index"))

    if TASK_STATUSES[task.status] != "Completed, not yet accepted":
        flash("You cannot accept a task that has not been completed (and awaiting acceptance)!", "error")
    elif g.user.id != task.requester_id:
        flash("You cannot accept a task that you did not assign!", "error")
    else:
        th = TaskHistory(task_id=id, prev_status=2, new_status=3)
        db.session.add(th)
        db.session.commit()

        task.status = 3
        pt = task.points.first()

        pt.awarded = pt.points

        db.session.add(task)
        db.session.add(pt)
        db.session.commit()

        flash("Task '%s' accepted!" % task.title, "success")

        if task.doer.options.task_accept_reject_email_alert:
            subject = "%s Has Accepted Task '%s'!" % (task.requester.username, task.title)
            email_body = render_template("mail/task_accepted.html", task=task)
            mailer.send_mail(task.doer.email, subject, email_body)

    return redirect(url_for("view_task", id=id))


@app.route("/task/reject/<int:id>", methods=['GET', 'POST'])
@login_required
def task_reject(id):
    task = Task.query.filter_by(id=id).first()

    if task is None:
        flash("No such task!", "error")
        return redirect(url_for("index"))

    if TASK_STATUSES[task.status] != "Completed, not yet accepted":
        flash("You cannot reject a task that has not been completed (and awaiting acceptance)!", "error")
    elif g.user.id != task.requester_id:
        flash("You cannot reject a task that you did not assign!", "error")
    else:
        th = TaskHistory(task_id=id, prev_status=2, new_status=4)
        db.session.add(th)
        db.session.commit()

        task.status = 4
        db.session.add(task)
        db.session.commit()

        flash("Task rejected! How about a punishment task for %s?" % task.doer.username, "success")

        if task.doer.options.task_accept_reject_email_alert:
            subject = "%s Has Rejected Task '%s'!" % (task.requester.username, task.title)
            email_body = render_template("mail/task_rejected.html", task=task)
            mailer.send_mail(task.doer.email, subject, email_body)

    return redirect(url_for("view_task", id=id))


@app.route("/task/edit/<int:id>", methods=['GET', 'POST'])
@login_required
def update_task(id):

    task = Task.query.filter_by(id=id).first()
    if task is None:
        flash("Task not found!", "error")
        return redirect(url_for("index"))

    if g.user.id != task.requester_id:
        flash("You can't edit the description for this task because you didn't assign it.", "error")
        return redirect(url_for("view_task", id=id))

    form = UpdateTaskForm()

    if form.validate_on_submit():

        title = form.title.data
        description = form.description.data

        task.description = description
        task.title = title
        task.privacy = form.privacy.data

        db.session.add(task)
        db.session.commit()

        flash("Task updated!", "success")

        if task.doer.options.task_edit_email_alert:
            email_body = render_template("mail/task_edit.html", task=task)
            subject = "%s Has Edited The Task '%s'" % (g.user.username, task.title)
            mailer.send_mail(task.doer.email, subject, email_body)

        return redirect(url_for("view_task", id=id))

    else:
        form.title.data = task.title
        form.description.data = task.description
        form.privacy.data = task.privacy
        return render_template("view_task.html", edit=True, form=form, task=task)


@app.route("/friends/send_request/<int:id>", methods=['GET', 'POST'])
@login_required
def send_friend_request(id):
    user = User.query.filter(User.id == id).first()

    if user is None:
        flash("Unable to find that user", "error")
        return redirect(url_for('index'))

    if g.user.is_friend(id):
        flash("You're already friends with %s!" % user.username, "warning")
        return redirect(url_for('profile_page', id=id))

    fr = FriendRequest(user_id=g.user.id, friend_id=id)
    db.session.add(fr)
    db.session.commit()

    if user.options.friend_request_email_alert:
        subject = "Friend Request From %s" % g.user.username
        email_body = render_template("mail/friend_request.html", user=user)
        mailer.send_mail(user.email, subject, email_body)

    flash("Friend request sent!", "success")
    return redirect(url_for('profile_page', id=id))


@app.route("/friends", methods=['GET', 'POST'])
@login_required
def friends():
    friend_request_page = int(request.values.get("friend_request_page", 1))
    friend_page = int(request.values.get("friend_page", 1))

    friend_requests = g.user.users_sending_friend_requests.paginate(friend_request_page, NUM_FRIENDS_PER_PAGE, False)
    friends = g.user.friends.paginate(friend_page, NUM_FRIENDS_PER_PAGE, False)
    return render_template("friends.html", friends=friends, friend_requests=friend_requests)


@app.route("/friends/accept/<int:id>", methods=['GET', 'POST'])
@login_required
def accept_friend_request(id):
    user = User.query.filter(User.id == id).first()

    if user is None:
        flash("Unable to find that user", "error")
        return redirect(url_for("friends"))

    request = FriendRequest.query.filter_by(user_id=user.id).filter_by(friend_id=g.user.id).first()

    if request is None:
        flash("Unable to find a friend request to you from %s" % user.username, "error")
        return redirect(url_for("friends"))

    db.session.delete(request)

    f1 = Friend(user_id=g.user.id, friend_id=user.id)
    f2 = Friend(user_id=user.id, friend_id=g.user.id)

    db.session.add(f1)
    db.session.add(f2)

    db.session.commit()

    if user.options.friend_request_accept_email_alert:
        subject = "%s Accepted Your Friend Request!" % g.user.username
        email_body = render_template("mail/friend_request_accepted.html", user=user)
        mailer.send_mail(user.email, subject, email_body)

    flash("Friend request accepted!", "success")
    return redirect(url_for("friends"))


@app.route("/friends/reject/<int:id>", methods=['GET', 'POST'])
@login_required
def reject_friend_request(id):
    user = User.query.filter(User.id == id).first()

    if user is None:
        flash("Unable to find that user", "error")
        return redirect(url_for("friends"))

    request = FriendRequest.query.filter_by(user_id=user.id).filter_by(friend_id=g.user.id).first()

    if request is None:
        flash("Unable to find a friend request to you from %s" % user.username, "error")
        return redirect(url_for("friends"))

    db.session.delete(request)
    db.session.commit()

    flash("Friend request from %s rejected (don't worry, they won't know a thing)." % user.username, "success")
    return redirect(url_for("friends"))


@app.route("/unfriend/<int:id>", methods=['GET', 'POST'])
@login_required
def unfriend(id):
    friend = User.query.filter_by(id=id).first()

    if friend is None:
        flash("No such user found!", "error")
        return redirect(url_for("index"))

    if not g.user.is_friend(friend.id):
        flash("That user is not your friend, so you can't unfriend them!", "error")
        return redirect(url_for('profile_page', id=friend.id))

    f1 = Friend.query.filter_by(user_id=friend.id).first()
    f2 = Friend.query.filter_by(friend_id=friend.id).first()

    db.session.delete(f1)
    db.session.delete(f2)
    db.session.commit()

    flash("%s is no longer your friend." % friend.username, "success")
    return redirect(url_for('profile_page', id=id))


@app.route("/reset", methods=['GET', 'POST'])
@login_required
def reset_password():
    form = ResetPasswordForm()

    if form.validate_on_submit():
        current_password = form.password.data
        new_password = form.new_password.data

        if bcrypt.check_password_hash(g.user.pw_hash, current_password):
            g.user.pw_hash = bcrypt.generate_password_hash(new_password)
            db.session.add(g.user)
            db.session.commit()

            flash("Your password has been successfully changed!", "success")
            return redirect(url_for("profile_page", id=g.user.id))
        else:
            flash("Your current password is incorrect. Please try again.", "success")

    return render_template("reset_password.html", form=form)


@app.route("/recover_username", methods=['GET', 'POST'])
def recover_username():
    if g.user.get_id():
        flash("Why are you trying to recover your username, when you're logged in?!", "warning")
        return redirect(url_for("index"))

    email = request.values.get("email")

    if email is None:
        return render_template("recover_username.html")
    else:
        user = User.query.filter_by(email=email).first()

        if user is None:
            flash("No user found with an email address of %s" % email, "error")
            return redirect(url_for("index"))

        email_body = render_template("mail/recover_username.html", user=user)
        mailer.send_mail(email, "Username Recovery", email_body)
        flash("Username recovery email sent!", "success")
        return redirect(url_for("index"))


@app.route("/reset_from_email_no_username", methods=['GET', 'POST'])
def reset_from_email_no_username():
    username = request.values.get("username")

    if username is None:
        return render_template("reset_from_email_no_username.html")
    else:
        user = User.query.filter_by(username=username).first()

        if user is None:
            flash("No user found with a username of '%s'" % username, "error")
            return render_template("reset_from_email_no_username.html")
        else:
            return redirect(url_for('reset_password_from_email', username=username))


@app.route("/reset_from_email_no_token/<username>", methods=['GET', 'POST'])
def reset_password_from_email(username):

    user = User.query.filter_by(username=username).first()

    if user is None:
        flash("User '%s' not found" % username, "error")
        return redirect(url_for("index"))

    token = str(uuid.uuid4())
    expiration = datetime.utcnow() + timedelta(1)
    user.password_reset_token = token
    user.password_reset_token_expiration = expiration
    db.session.add(user)
    db.session.commit()

    url = url_for('reset_password_from_email_with_token', token=token, _external=True)

    email_body = render_template("/mail/reset_password.html", user=user, url=url)
    subject = "Reset Your Kinkstruction Password"

    mailer.send_mail(user.email, subject, email_body)

    pw_reset_flash_msg = r'Email sent! Check your email for instructions on how to change your password.'
    flash(pw_reset_flash_msg, "success")
    return redirect(url_for('index'))


@app.route("/reset_from_email", methods=['GET', 'POST'])
def reset_password_from_email_with_token():

    token = request.values.get("token")

    form = ResetPasswordFromEmailForm()

    if token is None:
        flash("No token provided!", "error")
        return redirect(url_for("index"))
    else:
        user = User.query.filter_by(password_reset_token=token).first()
        if user is None:
            flash("No user found with token '%s'" & token, "error")
            return redirect(url_for("index"))
        else:
            delta = user.password_reset_token_expiration - datetime.utcnow()
            if delta < timedelta(1) and delta >= timedelta(0):
                if form.validate_on_submit():
                    user.pw_hash = bcrypt.generate_password_hash(form.password.data)
                    db.session.add(user)
                    db.session.commit()
                    g.user = user
                    login_user(g.user)
                    flash("Your password was successfully changed!", "success")
                    return redirect(url_for("index"))
                else:
                    return render_template("reset_password_from_email.html", form=form)
            else:
                flash("Token has expired!", "warning")
                return redirect(url_for("index"))


@app.route("/login", methods=['GET', 'POST'])
def login(user=None):
    if g.user is not None and g.user.is_authenticated():
        return redirect("/")

    form = LoginForm()
    if form.validate_on_submit():
        remember_me = form.remember_me.data
        username = form.username.data
        password = form.password.data

        g.user = User.query.filter_by(username=username).first()

        if g.user is None or not bcrypt.check_password_hash(g.user.pw_hash, password):
            flash("Your username or password is incorrect.", "error")
            return redirect("/login")

        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        login_user(g.user, remember=remember_me)
        flash("Authentication Successful!", "success")
        return redirect("/")

    return render_template("login.html", title="Log In", form=form)


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/profile/<int:id>")
@login_required
def profile_page(id):

    user = User.query.filter_by(id=id).first()

    if user is None:
        flash("No such user!", "error")
        return redirect(url_for("index"))

    if g.user.can_view_profile(user):
        return render_template("profile.html", user=user, title=user.username + " - Kinkstruction")

    flash("You are not allowed to view that!", "error")
    return redirect(url_for("index"))


@app.route("/profile/edit", methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        form_data = dict(form.data)

        for attr in form_data:
            if form_data[attr] and form_data[attr] != getattr(g.user, attr):
                setattr(g.user, attr, form_data[attr])

        db.session.add(g.user)
        db.session.commit()

        flash("Your changes have been saved!", "success")
        return redirect(url_for('profile_page', id=g.user.id))
    else:
        # TODO: There has *got* to be a better way...
        # Iterating through form doesn't seem to do it, though, for reasons
        # I don't understand.
        form.username.data = g.user.username
        form.email.data = g.user.email
        form.age.data = g.user.age if g.user.age is not None else ""
        form.gender.data = g.user.gender if g.user.gender is not None else ""
        form.role.data = g.user.role if g.user.role is not None else ""
        form.orientation.data = g.user.orientation if g.user.orientation is not None else ""
        form.bio.data = g.user.bio if g.user.bio is not None else ""

        return render_template('edit_profile.html', form=form)


@app.route("/sign_up", methods=['GET', 'POST'])
def sign_up():
    if g.user is not None and g.user.is_authenticated():
        return redirect("/")

    form = SignUpForm()
    if form.validate_on_submit():
        form_data = form.data
        form_data.pop("confirm_password")
        form_data.pop("remember_me")
        form_data["pw_hash"] = bcrypt.generate_password_hash(form_data.pop("password"))

        username = form_data["username"]
        email = form_data["email"]

        # Before we go any farther, we have to find out if the username and email aren't being
        # currently used.

        if User.query.filter_by(username=username).count():
            flash("Sorry, but the username '%s' is taken" % username, "error")
            form.data.pop("username")
            return render_template("sign_up.html", form=form, title="Kinkstruction Registration")

        if User.query.filter_by(email=email).count():
            message = Markup('Sorry, but there seems to already be a user with an email address of \'%s\'. If this is you, then please <a href="/login">log in!</a>' % email)
            flash(message, "error")
            form.data.pop("email")
            return render_template("sign_up.html", form=form, title="Kinkstruction Registration")

        # If we haven't seen the username or password before, then we're golden!

        u = User(**form_data)
        options = UserOptions(user_id=u.id)
        db.session.add(u)
        db.session.add(options)
        db.session.commit()

        # Re-query to get the full user object (id, etc).
        u = User.query.filter_by(username=username).first()

        g.user = u
        current_user = g.user

        url = url_for("verify_email", _external=True, signed_username=signer.sign(username))
        email_body = render_template("mail/verification.html", user=g.user, url=url)
        subject = "Kinkstruction Confirmation"

        mailer.send_mail(g.user.email, subject, email_body)

        logout_user()

        flash(Markup(verify_flash_msg), "info")
        return redirect(url_for('index'))

    return render_template("sign_up.html", form=form, title="Kinkstruction Registration")


@app.route("/resend_verification_email", methods=['GET', 'POST'])
def resend_verification_email():
    # Again, guard against sending emails for static asset requests...
    # Also, don't send email if we don't know who the hell we're sending it to
    if not re.match("^/static/", request.path) and g.user.get_id():
        # I'm not completely certain, but I believe we need this assignment so that
        # g.user doesn't get clobbered in the thread within mailer.send_mail()

        url = url_for("verify_email", _external=True, signed_username=signer.sign(g.user.username))
        email_body = render_template("mail/verification.html", user=g.user, url=url)
        subject = "Kinkstruction Confirmation"

        mailer.send_mail(g.user.email, subject, email_body)

        flash(Markup("Verification email resent to <i>%s</i>. If you still can't find it, check your spam folder" % g.user.email), "success")

    return redirect(url_for("index"))


@app.route("/verify_email", methods=['GET', 'POST'])
def verify_email():
    signed_username = request.values.get("signed_username")

    username = signer.unsign(signed_username)

    user = User.query.filter_by(username=username).first()

    if user is not None and not user.is_validated:
        g.user = user
        g.user.is_validated = True
        db.session.add(g.user)
        db.session.commit()
        login_user(g.user)
        flash("Email validation successful!", "success")
    elif user is not None and user.is_authenticated():
        flash("You've already validated. Log in!", "info")
    else:
        flash(Markup("Sorry, but email validation failed for some reason. <a href=\"/resend_verification_email\">Click here to resend the email</a>."), "warning")

    return render_template("index.html")


@app.route("/messages", methods=['GET', 'POST'])
@login_required
def messages():
    inbox_page = int(request.values.get("inbox", 1))
    outbox_page = int(request.values.get("outbox", 1))
    view = request.values.get("view", "inbox")

    if view != "outbox":
        view = "inbox"

    inbox_messages = g.user.inbox_messages().paginate(inbox_page, NUM_MESSAGES_PER_PAGE, False)
    outbox_messages = g.user.outbox_messages().paginate(outbox_page, NUM_MESSAGES_PER_PAGE, False)

    return render_template("messages.html", inbox_messages=inbox_messages, outbox_messages=outbox_messages, view=view)


@app.route("/message/<int:id>", methods=['GET', 'POST'])
@login_required
def view_message(id):
    message = Message.query.filter_by(id=id).first()
    if message is None:
        flash("Unable to display that message.", "error")
        return redirect(url_for('index'))

    # Set the message to read, but only if it's sent to g.user
    if not message.is_read and message.to_user().id == g.user.id:
        message.is_read = True
        db.session.add(message)
        db.session.commit()

    return render_template('view_message.html', message=message)


@app.route("/message/send/<int:id>", methods=['GET', 'POST'])
@login_required
def new_message(id):
    user = User.query.filter_by(id=id).first()

    if user is None:
        flash("You cannot send a message to that user.", "error")
        return redirect(url_for("index"))

    form = NewMessageForm()
    if form.validate_on_submit():
        message = Message(
            from_user_id=g.user.id,
            to_user_id=id,
            title=form.title.data,
            body=form.body.data
        )

        db.session.add(message)
        db.session.commit()

        if user.options.message_new_email_alert:
            email_body = render_template("mail/new_message.html", user=user, message=message)
            mailer.send_mail(user.email, "New message from %s at Kinkstruction" % g.user.username, email_body)

        flash("Message sent!", "success")
        return redirect(url_for('messages'))
    else:
        user = User.query.filter_by(id=id).first()
        if user is None:
            flash("Unable to send a message to that user.", "error")
            return redirect(url_for('index'))
        else:
            return render_template('new_message.html', user=user, form=form)


@app.route("/message/reply/<int:id>", methods=['GET', 'POST'])
@login_required
def message_reply(id):
    original = Message.query.filter_by(id=id).first()
    if original is None:
        flash("Unable to reply to that message: no such message found!", "error")
        return redirect(url_for('index'))

    form = NewMessageForm()

    if form.validate_on_submit():
        message = Message(
            from_user_id=g.user.id,
            to_user_id=original.from_user().id,
            title=form.title.data,
            body=form.body.data
        )

        db.session.add(message)
        db.session.commit()

        user = original.from_user()

        if user.options.message_new_email_alert:
            email_body = render_template("mail/new_message.html", user=user, message=message)

            mailer.send_mail(user.email, "New message from %s at Kinkstruction" % g.user.username, email_body)

        flash("Message sent!", "success")
        return redirect(url_for('messages'))
    else:
        new_title = "Re:" + original.title
        if len(new_title) > 256:
            new_title = new_title[0:256]
        form.title.data = new_title

        return render_template("new_message.html", user=original.from_user(), form=form)


# 500 error handler
@app.errorhandler(500)
def server_error(e):
    return render_template("500.html", poem=choice(HTTP_500_POEMS)), 500


# To test the 500 page
@app.route("/500", methods=['GET', 'POST'])
def five_hundred():
    return render_template("500.html", poem=choice(HTTP_500_POEMS))

from app import app, db, lm
from flask import render_template, g, url_for, session, flash, redirect, request
from flask.ext.login import login_user, logout_user, current_user, login_required
from app.models import User, Task
from forms import *


@lm.user_loader
def loadUser(id):
    return User.query.get(int(id))


@app.before_request
def beforeRequest():
    g.user = current_user


@app.route("/index", methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
    if g.user is not None and g.user.is_authenticated():
        return render_template("index.html")
    else:
        return redirect("/login")


@app.route("/login", methods=['GET', 'POST'])
def login(user=None):
    if g.user is not None and g.user.is_authenticated():
        return redirect("/")

    form = LoginRegisterForm()
    if form.validate_on_submit():
        remember_me = form.remember_me.data
        username = form.username.data
        password = form.password.data

        g.user = User.query.filter_by(username=username).first()

        if g.user is None or g.user.password != password:
            flash("Your username or password is incorrect.")
            return redirect("/login")

        login_user(g.user, remember=remember_me)
        flash("Authentication Successful!")
        return redirect("/")

    return render_template("login.html", title="Log In", form=form)


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect("/login")


@app.route("/check_username", methods=['POST'])
def check_username():
    username = request.values.get("username")
    print "IN CHECK_USERNAME: " + username
    return User.query.filter_by(username=username).count()


@app.route("/register", methods=['GET', 'POST'])
def register():
    if g.user is not None and g.user.is_authenticated():
        return redirect("/")

    form = LoginRegisterForm()
    print "built form"
    if form.validate_on_submit():
        remember_me = form.remember_me.data
        username = form.username.data
        password = form.password.data

        u = User(username=username, password=password)
        db.session.add(u)
        db.session.commit()

        # Re-query to get the full user object (id, etc).
        u = User.query.filter_by(username=username).first()
        login_user(u, remember=remember_me)
        flash("Account successfully created!")
        flash("Login successful!")

        g.user = u

        return render_template("index.html")

    return render_template("register.html", form=form, title="Kinkstruction Registration")

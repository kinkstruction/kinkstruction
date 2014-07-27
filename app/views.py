from app import app, db, lm, bcrypt, verificationMailer
from flask import render_template, g, url_for, session, flash, redirect, request
from flask.ext.login import login_user, logout_user, current_user, login_required, AnonymousUserMixin
from app.models import User, Task
from forms import *


@lm.user_loader
def loadUser(id):
    return User.query.get(int(id))


@app.before_request
def beforeRequest():
    g.user = current_user
    try:
        if not g.user.is_validated:
            flash(r"You need to verify your email address to continue. Please look for an email from <code>verifications@kinkstruction.com</code>. \
                <a href=\"/resend_verification_email\">Click here to resend the email</a>.")
    except:
        pass


@app.route("/index", methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")


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
            flash("Your username or password is incorrect.")
            return redirect("/login")

        login_user(g.user, remember=remember_me)
        flash("Authentication Successful!")
        return redirect("/")

    return render_template("login.html", title="Log In", form=form)


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/check_username", methods=['POST'])
def check_username():
    username = request.values.get("username")
    return User.query.filter_by(username=username).count()


@app.route("/sign_up", methods=['GET', 'POST'])
def sign_up():
    if g.user is not None and g.user.is_authenticated():
        return redirect("/")

    form = SignUpForm()
    if form.validate_on_submit():
        remember_me = form.remember_me.data
        username = form.username.data
        pw_hash = bcrypt.generate_password_hash(form.password.data)
        email = form.email.data

        u = User(username=username, pw_hash=pw_hash, email=email)
        db.session.add(u)
        db.session.commit()

        # Re-query to get the full user object (id, etc).
        u = User.query.filter_by(username=username).first()

        g.user = u

        verificationMailer.send_mail(u)

        return render_template("index.html")

    return render_template("sign_up.html", form=form, title="Kinkstruction Registration")


@app.route("/resend_verification_email", methods=['GET', 'POST'])
def resend_verification_email():
    verificationMailer.send_mail(g.user)
    return render_template("index.html")


@app.route("/verify_email", methods=['GET', 'POST'])
def verify_email():
    signed_username = request.values("signed_username")
    if verificationMailer.check_signed_username(g.user, signed_username):
        g.user.is_validated = True
        db.session.add(g.user)
        db.session.commit()
        flash("Email validation successful!")
    else:
        flash("Sorry, but email validation failed for some reason. <a href=\"/resend_verification_email\">Click here to resend the email</a>.")

    return render_template("index.html")

from app import app, db, lm, bcrypt, verificationMailer
from flask import render_template, g, url_for, session, flash, redirect, request, Markup
from flask.ext.login import login_user, logout_user, current_user, login_required, AnonymousUserMixin
from app.models import User, Task
from forms import *
import re

verify_flash_msg = r'You need to verify your email address to continue. Please look for an email from <i>verifications@kinkstruction.com</i>. <a href="/resend_verification_email">Click here to resend the email</a>.'


@lm.user_loader
def loadUser(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user

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
        current_user = g.user

        verificationMailer.send_mail(u.username, u.email)

        logout_user()

        flash(Markup(verify_flash_msg))
        return render_template("index.html")

    return render_template("sign_up.html", form=form, title="Kinkstruction Registration")


@app.route("/resend_verification_email", methods=['GET', 'POST'])
def resend_verification_email():
    # Again, guard against sending emails for static asset requests...
    # Also, don't send email if we don't know who the hell we're sending it to
    if not re.match("^/static/", request.path) and g.user.get_id():
        # I'm not completely certain, but I believe we need this assignment so that
        # g.user doesn't get clobbered in the thread within verificationMailer.send_mail()
        u = g.user

        verificationMailer.send_mail(u.username, u.email)
        flash(Markup("Verification email resent to <i>%s</i>. If you still can't find it, check your spam folder" % g.user.email))

    return redirect(url_for("index"))


@app.route("/verify_email", methods=['GET', 'POST'])
def verify_email():
    signed_username = request.values.get("signed_username")

    username = verificationMailer.signer.unsign(signed_username)

    user = User.query.filter_by(username=username).first()

    if user is not None and not user.is_validated:
        g.user = user
        g.user.is_validated = True
        db.session.add(g.user)
        db.session.commit()
        login_user(g.user)
        flash("Email validation successful!")
    elif user is not None and user.is_authenticated():
        flash("You've already validated. Log in!")
    else:
        flash(Markup("Sorry, but email validation failed for some reason. <a href=\"/resend_verification_email\">Click here to resend the email</a>."))

    return render_template("index.html")

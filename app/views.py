from app import app
from flask import render_template, g, url_for


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route("/test")
def test():
	return "testing testing..."

@app.route("/test2")
def test2():
	return "Does this work??"

from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from forms import UserForm, LoginForm
from werkzeug.exceptions import Unauthorized

import os

username = os.environ['PGUSER']
password = os.environ['PGPASSWORD']
secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

app = Flask(__name__)

app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{username}:{password}@localhost:5432/flask-feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

@app.route('/')
def homepage():
    return redirect('/register')

@app.route('/register', methods=['GET','POST'])
def register_user():

    if 'username' in session:
        return redirect(f"/users/{session['username']}")
    
    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username, password, email, first_name, last_name)

        db.session.commit()

        session['username'] = user.username

        return redirect(f"/users/{user.username}")
    else:
        return render_template("users/register.html", form = form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():

    if "username" in session:
        return redirect(f"/users/{session['username']}")
    
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            return redirect(f"/secret/{user.username}")
        else:
            form.username.errors = ["Invalid username/password."]
            return render_template("users/login.html", form = form)
        
    return render_template("users/login.html", form = form)

@app.route('/logout')
def logout_user():
    session.pop("username")
    return redirect("/login")

@app.route('/users/<username>')
def show_user(username):

    if 'username' not in session or username != session['username']:
        raise Unauthorized()
    
    user = User.query.get_or_404(username)
    print(user.email)

    return render_template("users/show.html", user=user)
    



    

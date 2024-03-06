# imports
from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from werkzeug.exceptions import abort
import json, datetime
import sqlite3

# app config/db configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'LD449VaAKb'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# loads users
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# user table for users (id, username, password, email, userPosts (int))
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    created = db.Column(db.Date, nullable=False, default=datetime.datetime.now())
    isTeacher = db.Column(db.Boolean, nullable=False, default=False)
    userPosts = db.Column(db.Integer, default=0)
    courses = db.relationship('Course', backref=db.backref('course'))

# post table for posts (id, user, date created, location, email)
class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    courseName = db.Column(db.String(50), nullable=False)
    authorName = db.Column(db.String(20), nullable=False, unique=False)
    summary = db.Column(db.String(50))
    dateCreated = db.Column(db.String(100), nullable=False, unique=False, default=datetime.datetime.now())
    course_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    chapters = db.relationship('Chapter', backref=db.backref('chapter'))

class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapterName = db.Column(db.String(50), nullable=True)
    summaryText = db.Column(db.String(250))
    dateCreated = db.Column(db.String(100), nullable=False, unique=False, default=datetime.datetime.now())
    chapter_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    
# class register form (takes username, password, and email parameters)
class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    
    email = PasswordField(validators=[
                             InputRequired(), Length(min=10, max=40)], render_kw={"placeholder": "Email"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

# login form class (takes username, password and email)
class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

# route for homepage
@app.route('/')
def home():
    return render_template('home.html')

# route to login
@app.route('/login', methods=['GET', 'POST'])
def login():
    global user
    form = LoginForm()
    
    if request.method == "POST":
        # validates the form
        print(request.data)

        """
        
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
        """
    return render_template('login.html', form=form)

# route to dashboard (kind of like homepage)
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    courses = Course.query.all()
    print(courses)
    return render_template('dashboard.html', user=user, courses=courses)

# route for 404 error handling
# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404
# route to logout
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# route to register
@ app.route('/register', methods=['GET', 'POST'])
def register():
    # creates form
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password, email=form.email.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# route to edit account information
@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        User.username = username
        User.password = password
        User.email = email
        db.session.commit()

        return redirect(url_for('dashboard', user=user))

    return render_template('editAccount.html')

@app.route('/courses', methods=['GET', 'POST'])
@login_required
def courses():
    if request.method == 'POST':
        courseName = request.form['name']
        authorName = user.username
        print(authorName)
        summary = request.form['summary']

        newCourse = Course(courseName=courseName, summary=summary, authorName=authorName)
        db.session.add(newCourse)
        db.session.commit()

        return redirect(url_for('chapters', user=user))

    return render_template('courses.html')

@app.route('/chapters', methods=['GET', 'POST'])
@login_required
def chapters():
    if request.method == 'POST':
        chapterName = request.form['name']
        summary = request.form['summary']

        newChapter = Chapter(chapterName=chapterName, summaryText=summary)
        db.session.add(newChapter)
        db.session.commit()

        return redirect(url_for('dashboard', user=user))

    return render_template('chapters.html')

# route for about page
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True)

#test commit

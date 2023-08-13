import os

from flask import Flask, render_template, request, redirect, flash, url_for
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, LoginManager, current_user, login_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from forms import user_login, sign_up

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
login_manager = LoginManager()
login_manager.init_app(app)
bootstrap = Bootstrap5(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///all.db"
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), primary_key=False)
    email = db.Column(db.String(250), primary_key=False)
    password = db.Column(db.String(250), primary_key=False)
    tasks = db.relationship('AcTasks', back_populates="users")


class AcTasks(db.Model):
    __tablename__ = "active_tasks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tasks = db.Column(db.String(250), primary_key=False)
    users = db.relationship('User', back_populates="tasks")
    active_tasks = db.relationship("DiTasks", back_populates="disabled_tasks")


class DiTasks(db.Model):
    __tablename__ = "disabled_tasks"
    id = db.Column(db.Integer, primary_key=True)
    tasks = db.Column(db.String(250), primary_key=False)
    tasks_id = db.Column(db.Integer, db.ForeignKey('active_tasks.id'))
    disabled_tasks = db.relationship("AcTasks", back_populates="active_tasks")


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def home():
    thing = AcTasks.query.all()
    return render_template('index.html', logged=current_user, data=thing)


@app.route("/add")
def add_task():
    return render_template('add_task.html', logged=current_user)


@app.route("/register", methods=['POST', 'GET'])
def register():
    form = sign_up()
    if form.validate_on_submit():
        new_user = User()
        new_user.name = request.form['name']
        new_user.email = request.form['email']
        new_user.password = generate_password_hash(
            password=request.form['password'],
            method="pbkdf2:sha256",
            salt_length=8
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html', form=form, logged=current_user)


@app.route("/login", methods=['POST', 'GET'])
def login():
    form = user_login()
    if form.validate_on_submit():
        email = form.email.data
        password = form.email.data
        new_user = User.query.filter_by(email=email).first()
        if not new_user:
            flash("This email doesn't exist")
            return redirect(url_for('login'))
        elif not check_password_hash(new_user.password, password):
            flash("Password incorrect, Please try again.")
            return redirect(url_for('login'))
        else:
            login_user(new_user)
            return redirect(url_for('home'))
    return render_template('login.html', form=form, logged=current_user)


if __name__ == "__main__":
    app.run(debug=True)

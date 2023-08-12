import os

from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, LoginManager, current_user, login_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash
from wtforms import StringField, EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
login_manager = LoginManager()
login_manager.init_app(app)
bootstrap = Bootstrap5(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///all.db"
db = SQLAlchemy(app)

with app.app_context():
    db.create_all()


class sign_up(FlaskForm):
    name = StringField(validators=[DataRequired()])
    email = EmailField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField(validators=[DataRequired()])


class user_login(FlaskForm):
    email = EmailField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField(validators=[DataRequired()])


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), primary_key=False)
    email = db.Column(db.String(250), primary_key=False)
    password = db.Column(db.String(250), primary_key=False)
    lists = db.relationship('AcTasks', back_populates="users")


class AcTasks(db.Model):
    __tablename__ = "active_tasks"
    id = db.Column(db.Integer, primary_key=True)
    tasks = db.Column(db.String(250), primary_key=False)
    users = db.relationship('User', primary_key=False, back_populates="lists")
    deactasks = db.relationship("DiTasks", back_populates="active_tasks")


class DiTasks(db.Model):
    __tablename__ = "disabled_tasks"
    id = db.Column(db.Integer, primary_key=True)
    tasks = db.Column(db.String(250), primary_key=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def home():
    return render_template('index.html', logged=current_user)


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
        return redirect('/')
    return render_template('register.html', form=form, logged=current_user)


@app.route("/login")
def login():
    form = user_login()
    return render_template('login.html', form=form)


if __name__ == "__main__":
    app.run(debug=True)

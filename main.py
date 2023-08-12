from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from wtforms import StringField, EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
bootstrap = Bootstrap5(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///all.db"
db = SQLAlchemy(app)


class sign_up(FlaskForm):
    name = StringField(validators=[DataRequired()])
    email = EmailField(validators=[DataRequired()])
    passw = PasswordField(validators=[DataRequired()])
    submit = SubmitField


class login(FlaskForm):
    email = EmailField(validators=[DataRequired()])
    passw = PasswordField(validators=[DataRequired()])
    submit = SubmitField


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    email = db.Column(db.String(250))
    password = db.Column(db.String(250))
    lists = db.relationship('active_tasks', back_populates="users")


class AcTasks(db.Model):
    __tablename__ = "active_tasks"
    id = db.Column(db.Integer, primary_key=True)
    tasks = db.Column(db.String(250))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def home():
    return render_template('index.html', logged=current_user)


@app.route("/login")
def login():
    return render_template('login.html', form=login)


if __name__ == "__main__":
    app.run(debug=True)

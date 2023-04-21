from flask import Flask, request, g, Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, LoginManager, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, PasswordField
from werkzeug.exceptions import abort
from flask_sqlalchemy import SQLAlchemy
from satr import usr_db

bp = Blueprint('login_mgr', __name__)
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
##
@bp.route('/login', methods=['GET'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    else:
        return render_template('login.html', title='Sign In')

@bp.route('/login', methods=['POST'])
def login():
    form = LoginForm(request.form)
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    form = LoginForm(request.form)
    if form.username.data and form.password.data:
        g.user=form.username.data
        g.password=form.password.data
        user=User.query.filter_by(username=g.user).first()
        if user:
            pass
        else:
            flash('Invalid username or password')
            return redirect(url_for('.index'))
    else:
        flash('Invalid username or password')
        return redirect(url_for('.index'))

    if user.is_authenticated and user.is_active and g.user==user.username and g.password==user.password:
        login_user(user)
        return redirect(url_for('home.index'))
    else:
        flash('Invalid username or password')
        return redirect(url_for('.index'))
##

@bp.route('/login/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

class User(usr_db.Model):
    __tablename__ = 'users'
    usr_id = usr_db.Column(usr_db.Integer(), primary_key=True)
    username = usr_db.Column(usr_db.String(255), nullable=False)
    password = usr_db.Column(usr_db.String(255), nullable=False)

    def is_authenticated(self):
        return True
        #return true if user is authenticated, provided credentials

    def is_active(self):
        return True
        #return true if user is activte and authenticated

    def is_annonymous(self):
        return False
        #return true if annon, actual user return false

    def get_id(self):
        return str(self.usr_id)



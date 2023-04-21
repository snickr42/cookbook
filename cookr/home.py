from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, Flask
)
#from werkzeug.exceptions import abort
#from flask_login import current_user, login_user, logout_user, login_required

bp = Blueprint('home', __name__)

@bp.route('/')
@bp.route('/home')
def index():
    return render_template(
      'home.html',
    )

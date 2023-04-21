import os
from flask import Flask
from flask_login import (current_user, LoginManager, login_user, logout_user, login_required)
from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate

usr_db = SQLAlchemy()

def create_app(test_config=None):
# create and configure the app
    app=Flask(__name__)
    app.config.from_object('config.Config')
    print(app.config) #debug

#home
    from . import home
    app.register_blueprint(home.bp)    
#database
    from . import db
    db.init_app(app)
#    usr_db = SQLAlchemy()
    usr_db.init_app(app)
#tol
    from . import tol
    app.register_blueprint(tol.bp)
#tests
    from . import st_lib
    app.register_blueprint(st_lib.bp)
#login
    from . import login_mgr
    app.register_blueprint(login_mgr.bp)
    login_mgr.login_manager.init_app(app)
    login_mgr.login_manager.login_view = 'login_mgr.login'
#upld
    from . import upld
    app.register_blueprint(upld.bp)

    app.add_url_rule('/', endpoint='index')
    return app


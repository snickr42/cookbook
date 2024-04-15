import os
from flask import Flask
#from flask_login import (current_user, LoginManager, login_user, logout_user, login_required)
#from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate

#usr_db = SQLAlchemy()

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
#recipe
    from . import recipe
    app.register_blueprint(recipe.bp)
#upld
    from . import upld
    app.register_blueprint(upld.bp)
#mod
    from . import modify
    app.register_blueprint(modify.bp)

    app.add_url_rule('/', endpoint='index')
    return app


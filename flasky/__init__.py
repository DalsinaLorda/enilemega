from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
#import flask_whooshalchemy as wa
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os
from flask_migrate import Migrate

app=Flask(__name__)
app.config['SECRET_KEY']='4bfdec5b4ca75b093634d43a07b2520a'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
#app.config['WHOOSH_BASE']='whoosh'


db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
migrate = Migrate(app, db)
with app.app_context():
    if db.engine.url.drivername=="sqlite":
        migrate.init_app(app, db, render_as_bash = True)
    else:
        migrate.init_app(app, db)
login_manager=LoginManager(app)
login_manager.login_view='login'

from flasky import routes

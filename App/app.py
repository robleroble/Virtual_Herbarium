import requests, random
import os
from flask import Flask, render_template, redirect, flash, request, session, Blueprint
from models import (
    db,
    connect_db,
    User,
    Specimen,
    Details,
    Taxonomy,
    Collection,
    CollectionSpecimen,
)
from forms import (
    SignupForm,
    LoginForm,
    SpecimenImageForm,
    TaxonomyForm,
    CollectionDetailsForm,
    EditUserForm,
    CollectionForm,
    AddSpecimenToCollectionForm,
)
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from extra_funcs import clear_specimen_session, upload_img

# Blueprints
from auth_bp.auth import auth_bp
from users_bp.users import users_bp
from specimens_bp.specimens import specimens_bp
from collections_bp.collections import collections_bp

app = Flask(__name__)

app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(specimens_bp)
app.register_blueprint(collections_bp)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL', "postgres:///virtual_herbarium")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'hellosecret1')
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
# app.config["ImgurKey"] = os.environ.get('IMGUR_KEY")


connect_db(app)
db.create_all()

###############################
# flask_login

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """Returns user based on user_id"""
    return User.query.get(int(user_id))


@app.route("/")
def home_page():
    """Returns the homepage of website"""

    return render_template("home.html")
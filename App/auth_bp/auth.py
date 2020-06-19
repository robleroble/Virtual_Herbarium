from flask import Flask, render_template, redirect, flash, session, Blueprint
from models import (
    db,
    User,
)
from forms import (
    SignupForm,
    LoginForm,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from flask_login import (
    login_user,
    login_required,
    logout_user,
)

auth_bp = Blueprint('auth_bp', __name__, template_folder='templates', static_folder='static')


# SIGNUP route
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """Displays form to sign up a new user"""
    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                bio=form.bio.data,
                location=form.location.data,
                profile_pic=form.img_url.data or User.profile_pic.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", "danger")
            return redirect("/signup")

        login_user(user)
        flash(f"Welcome {user.username}!", "success")
        return redirect(f"/profile/{user.id}")
    else:
        return render_template("signup.html", form=form)


# LOGIN route
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Displays form to login user"""
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            login_user(user)
            flash(f"Hi {user.username}. You are logged in", "success")
            return redirect(f"/user/{user.id}")

        flash("Incorrect username or password", "danger")

    return render_template("login.html", form=form)

# LOGOUT route
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You are now logged out.", "success")
    return redirect("/")
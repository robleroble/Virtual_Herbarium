from flask import Flask, render_template, redirect, flash, request, session, Blueprint
from models import (
    db,
    User,
    Specimen,
    Collection,
)
from forms import (
    EditUserForm,
)
from flask_login import (
    login_required,
    current_user,
)

users_bp = Blueprint('users_bp', __name__, template_folder='templates', static_folder='static')

##################################################
# user routes

# DISPLAY USER PROFILE
@users_bp.route("/user/<int:user_id>")
def profile(user_id):
    """Displays user profile page"""

    user = User.query.get_or_404(user_id)
    collections = Collection.query.filter_by(user_id=user_id).all()
    collection_count = Collection.query.filter_by(user_id=user_id).count()
    specimens = Specimen.query.filter_by(user_id=user_id).all()
    specimen_count = Specimen.query.filter_by(user_id=user_id).count()

    return render_template(
        "user.html",
        user=user,
        specimens=specimens,
        collections=collections,
        collection_count=collection_count,
        specimen_count=specimen_count,
    )


# EDIT USER
@users_bp.route("/user/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def edit_profile(user_id):
    """Displays form for user to edit user details (GET) and submits form (POST)"""

    if current_user.id == user_id:
        user = User.query.get_or_404(user_id)
        form = EditUserForm(obj=user)

        if form.validate_on_submit():
            user.username = form.username.data
            user.bio = form.bio.data
            user.location = form.location.data
            if form.img_url.data == "":
                db.session.commit()
                flash("Profile changes saved!", "success")
                return redirect(f"/user/{user.id}")
            else:
                user.profile_pic = form.img_url.data

            db.session.commit()

            flash("Profile changes saved!", "success")
            return redirect(f"/user/{user.id}")

        else:
            return render_template("edituser.html", form=form)
    else:
        return ("", 403)


# DELETE USER
@users_bp.route("/user/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_profile(user_id):
    """Route deletes current_user"""

    if current_user.id == user_id:
        user = User.query.get_or_404(user_id)

        logout_user()

        db.session.delete(user)
        db.session.commit()

        flash("Account deleted!", "success")
        return redirect("/")
    else:
        return ("", 403)


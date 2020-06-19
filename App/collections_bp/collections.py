from flask import Flask, render_template, redirect, flash, request, session, Blueprint
from models import (
    db,
    connect_db,
    User,
    Specimen,
    Collection,
    CollectionSpecimen,
)
from forms import (
    CollectionForm,
)
from flask_login import (
    login_required,
    current_user,
)

collections_bp = Blueprint('collections_bp', __name__, template_folder='templates', static_folder='static')

#############################
# Collection routes


@collections_bp.route("/collection/new", methods=["POST", "GET"])
@login_required
def create_collection():
    """Displays form to create collection (GET), and submits it (POST)"""
    form = CollectionForm()

    if form.validate_on_submit():
        name = form.name.data
        info = form.info.data

        new_collection = Collection(name=name, info=info, user_id=current_user.id)
        db.session.add(new_collection)
        db.session.commit()

        flash(f"{name} collection created!", "success")
        return redirect(f"/user/{current_user.id}")

    else:
        return render_template("newcollection.html", form=form)


@collections_bp.route("/collection/<int:collection_id>")
def view_collection(collection_id):
    """View all specimens in a collection"""

    collection = Collection.query.get_or_404(collection_id)
    specimens_in_collection = [specimen for specimen in collection.specimens]
    num_specimens = len(specimens_in_collection)
    user = User.query.get_or_404(collection.user_id)

    return render_template(
        "displaycollection.html",
        collection=collection,
        num_specimens=num_specimens,
        user=user,
        specimens_in_collection=specimens_in_collection,
    )


@collections_bp.route("/collection/<int:collection_id>/edit", methods=["POST", "GET"])
@login_required
def edit_specimen(collection_id):
    """Displays form to edit collection info (GET) and submits it (POST)"""

    collection = Collection.query.filter_by(id=collection_id).first()
    form = CollectionForm(obj=collection)

    if current_user.id == collection.user_id:
        if form.validate_on_submit():
            collection.name = form.name.data
            collection.info = form.info.data

            db.session.commit()

            flash(f"{collection.name} edited!", "success")
            return redirect(f"/collection/{collection.id}")

        else:
            return render_template(
                "editcollection.html", form=form, collection=collection
            )
    else:
        return ("", 403)


@collections_bp.route("/collection/<int:collection_id>/delete", methods=["POST"])
@login_required
def delete_collection(collection_id):
    collection = Collection.query.get_or_404(collection_id)

    db.session.delete(collection)
    db.session.commit()

    flash(f"{collection.name} collection deleted", "success")
    return redirect(f"/user/{current_user.id}")


@collections_bp.route("/collection/<int:collection_id>/remove_specimen/<int:specimen_id>", methods=["POST"])
@login_required
def remove_specimen_from_collection(collection_id, specimen_id):
    """Clicking button removes specimen from collection"""
    collection_specimen = CollectionSpecimen.query.filter(
        CollectionSpecimen.collection_id == collection_id,
        CollectionSpecimen.specimen_id == specimen_id,
    ).first()

    specimen = Specimen.query.get_or_404(specimen_id)
    collection = Collection.query.get_or_404(collection_id)

    if current_user.id == collection.user_id == specimen.user_id:
        db.session.delete(collection_specimen)
        db.session.commit()

        flash(
            f"{specimen.taxonomy.common_name} successfully removed from {collection.name}!",
            "success",
        )
        return redirect(f"/collection/{collection_id}")
    else:
        return ("", 403)
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

specimens_bp = Blueprint('specimens_bp', __name__, template_folder='templates', static_folder='static')

@specimens_bp.route("/specimens")
def all_specimens():
    """Page with all specimens and collections - returns list of items in random order"""

    specimens = Specimen.query.order_by(func.random()).all()
    collections = Collection.query.order_by(func.random()).all()
    return render_template(
        "allspecimens.html", specimens=specimens, collections=collections
    )

#######################################################
# Specimen routes


@specimens_bp.route("/specimen/new/image", methods=["GET", "POST"])
@login_required
def create_specimen_image():
    """First form to create specimen - upload image"""

    clear_specimen_session()
    # STEP 1: UPLOAD IMAGE
    form = SpecimenImageForm()
    if form.validate_on_submit():
        if request.files:
            image = request.files["image"]
            # converts img to binary file (apparently)
            img = image.read()
            upload = upload_img(img)
            session["link"] = upload.get("data").get("link")

            return redirect("/specimen/new/taxonomy")
    else:
        return render_template("newspecimen.html", form=form, step="image")


@specimens_bp.route("/specimen/new/taxonomy", methods=["GET", "POST"])
@login_required
def create_specimen_taxonomy():
    """Second form to create specimen - enter name and species"""

    form = TaxonomyForm()
    if session.get("link") is not None:
        if form.validate_on_submit():
            session["common_name"] = (
                form.common_name.data or Taxonomy.common_name.default.arg
            )
            session["species"] = form.species.data or Taxonomy.species.default.arg
            session["genus"] = form.genus.data or Taxonomy.genus.default.arg
            session["family"] = form.family.data or Taxonomy.family.default.arg
            session["order"] = form.order.data or Taxonomy.order.default.arg
            session["phylum"] = form.phylum.data or Taxonomy.phylum.default.arg
            session["kingdom"] = form.kingdom.data or Taxonomy.kingdom.default.arg
            session["authorship"] = (
                form.authorship.data or Taxonomy.authorship.default.arg
            )

            return redirect("/specimen/new/details")

        else:
            return render_template(
                "newspecimen.html", form=form, step="taxonomy"
            )
    else:
        return ("", 403)


@specimens_bp.route("/specimen/new/details", methods=["GET", "POST"])
@login_required
def create_specimen_details():
    """Last form to create specimen - enter site details"""

    form = CollectionDetailsForm()

    if session.get("link") is not None and session.get("species") is not None:
        if form.validate_on_submit():
            session["date"] = form.date.data
            session["location"] = form.location.data
            session["county"] = form.county.data
            session["state"] = form.state.data
            session["habitat"] = form.habitat.data
            session["notes"] = form.notes.data

            user_id = current_user.id
            new_image = Specimen(link=session["link"], user_id=user_id)

            db.session.add(new_image)
            db.session.commit()

            specimen = Specimen.query.filter_by(link=session["link"]).first()

            new_specimen_taxonomy = Taxonomy(
                common_name=session["common_name"],
                specimen_id=specimen.id,
                species=session["species"],
                genus=session["genus"],
                family=session["family"],
                order=session["order"],
                phylum=session["phylum"],
                kingdom=session["kingdom"],
                authorship=session["authorship"],
            )

            new_specimen_details = Details(
                specimen_id=specimen.id,
                date=session["date"],
                location=session["location"],
                habitat=session["habitat"],
                county=session["county"],
                state=session["state"],
                notes=session["notes"],
            )

            db.session.add(new_specimen_taxonomy)
            db.session.add(new_specimen_details)
            db.session.commit()

            clear_specimen_session()

            flash(f"{specimen.taxonomy.common_name} specimen created!", "success")
            return redirect(f"/specimen/{specimen.id}")

        else:
            return render_template(
                "newspecimen.html", form=form, step="collection_details"
            )
    else:
        return ("", 403)


# DISPLAY SPECIMEN
@specimens_bp.route("/specimen/<int:specimen_id>", methods=["POST", "GET"])
def display_specimen(specimen_id):
    """Full page display of specimen with all info
    Includes form in modal popup with ability to edit specimen data (not the image)"""

    specimen = Specimen.query.get_or_404(specimen_id)

    return render_template("displayspecimen.html", specimen=specimen)


# DELETE SPECIMEN
@specimens_bp.route("/specimen/<int:specimen_id>/delete", methods=["POST"])
@login_required
def delete_specimen(specimen_id):
    """Allows specimen creator to delete a specimen"""

    specimen = Specimen.query.get_or_404(specimen_id)

    if current_user.id == specimen.user_id:

        db.session.delete(specimen)
        db.session.commit()

        flash("Specimen deleted!", "success")
        return redirect(f"/user/{current_user.id}")
    else:
        return ("", 403)


# EDIT SPECIMEN - IMAGE
@specimens_bp.route("/specimen/<int:specimen_id>/edit_image", methods=["GET", "POST"])
@login_required
def edit_image(specimen_id):
    """Edit the image of plant specimen"""

    form = SpecimenImageForm()
    specimen = Specimen.query.get_or_404(specimen_id)
    if specimen.user_id == current_user.id:
        if form.validate_on_submit():
            if request.files:
                image = request.files["image"]
                img = image.read()
                upload = upload_img(img)

                specimen.link = upload.get("data").get("link")
                db.session.commit()

                return redirect(f"/specimen/{specimen_id}")

        else:
            return render_template(
                "editspecimen.html", form=form, specimen=specimen, step="image"
            )
    else:
        return ("", 403)


# EDIT SPECIMEN - TAXONOMY
@specimens_bp.route("/specimen/<int:specimen_id>/edit_taxonomy", methods=["GET", "POST"])
@login_required
def edit_taxonomy(specimen_id):
    """Edit the image of plant specimen"""
    specimen = Taxonomy.query.filter_by(specimen_id=specimen_id).first()
    form = TaxonomyForm(obj=specimen)

    if current_user.id == specimen.specimens.user_id:
        if form.validate_on_submit():
            specimen.common_name = form.common_name.data
            specimen.species = form.species.data
            specimen.genus = form.genus.data
            specimen.family = form.family.data
            specimen.order = form.order.data
            specimen.phylum = form.phylum.data
            specimen.kingdom = form.kingdom.data
            specimen.authorship = form.authorship.data

            db.session.commit()

            return redirect(f"/specimen/{specimen_id}")

        else:
            return render_template(
                "editspecimen.html",
                form=form,
                specimen=specimen,
                step="taxonomy",
            )
    else:
        return ("", 403)


# EDIT SPECIMEN - DETAILS
@specimens_bp.route("/specimen/<int:specimen_id>/edit_details", methods=["GET", "POST"])
@login_required
def edit_details(specimen_id):
    """Edit the image of plant specimen"""
    specimen = Details.query.filter_by(specimen_id=specimen_id).first()
    form = CollectionDetailsForm(obj=specimen)

    if current_user.id == specimen.specimens.user_id:
        if form.validate_on_submit():
            specimen.date = form.date.data
            specimen.location = form.location.data
            specimen.county = form.county.data
            specimen.state = form.state.data
            specimen.habitat = form.habitat.data
            specimen.notes = form.notes.data

            db.session.commit()

            return redirect(f"/specimen/{specimen_id}")

        else:
            return render_template(
                "editspecimen.html",
                form=form,
                specimen=specimen,
                step="details",
            )
    else:
        return ("", 403)


# ADD SPECIMEN TO A COLLECTION
@specimens_bp.route("/specimen/<int:specimen_id>/add_to_collection", methods=["GET", "POST"])
@login_required
def add_specimen_to_collection(specimen_id):
    """Displays form to add specimen to a collection"""

    specimen = Specimen.query.get_or_404(specimen_id)
    form = AddSpecimenToCollectionForm()

    not_in_collection = [collection.id for collection in specimen.collections]
    form.collection.choices = (
        db.session.query(Collection.id, Collection.name)
        .filter(Collection.id.notin_(not_in_collection))
        .all()
    )

    if form.validate_on_submit():
        new_collection_specimen = CollectionSpecimen(
            collection_id=form.collection.data, specimen_id=specimen_id
        )

        db.session.add(new_collection_specimen)
        db.session.commit()
        flash(f"{specimen.taxonomy.common_name} added to collection!", "success")
        return redirect(f"/collection/{form.collection.data}")

    return render_template(
        "addspecimentocollection.html", form=form, specimen=specimen
    )

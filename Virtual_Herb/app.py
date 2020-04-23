import requests, random
from flask import Flask, render_template, redirect, flash, request, session
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
from imgurkeys import client_id

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///virtual_herbarium"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "SECRET!"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False


connect_db(app)
db.create_all()
# debug = DebugToolbarExtension(app)


###############################
# flask_login routes

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


@app.route("/specimens")
def all_specimens():
    """Page with all specimens and collections - returns list of items in random order"""

    specimens = Specimen.query.order_by(func.random()).all()
    collections = Collection.query.order_by(func.random()).all()
    return render_template(
        "allspecimens.html", specimens=specimens, collections=collections
    )


# SIGNUP route
@app.route("/signup", methods=["GET", "POST"])
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
        return render_template("user/signup.html", form=form)


# LOGIN route
@app.route("/login", methods=["GET", "POST"])
def login():
    """Displays form to login user"""
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            login_user(user)
            flash(f"Hi {user.username}. You are logged in", "success")
            return redirect(f"/profile/{user.id}")

        flash("Incorrect username or password", "danger")

    return render_template("user/login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You are now logged out.", "success")
    return redirect("/")


##################################################
# profile routes

# DISPLAY USER PROFILE
@app.route("/profile/<int:user_id>")
def profile(user_id):
    """Displays user profile page"""

    user = User.query.get_or_404(user_id)
    collections = Collection.query.filter_by(user_id=user_id).all()
    collection_count = Collection.query.filter_by(user_id=user_id).count()
    specimens = Specimen.query.filter_by(user_id=user_id).all()
    specimen_count = Specimen.query.filter_by(user_id=user_id).count()

    return render_template(
        "user/profile.html",
        user=user,
        specimens=specimens,
        collections=collections,
        collection_count=collection_count,
        specimen_count=specimen_count,
    )


# EDIT USER
@app.route("/profile/<int:user_id>/edit", methods=["GET", "POST"])
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
                return redirect(f"/profile/{user.id}")
            else:
                user.profile_pic = form.img_url.data

            db.session.commit()

            flash("Profile changes saved!", "success")
            return redirect(f"/profile/{user.id}")

        else:
            return render_template("user/edituser.html", form=form)
    else:
        return ("", 403)


# DELETE USER
@app.route("/profile/<int:user_id>/delete", methods=["POST"])
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


#######################################################
# Specimen routes


@app.route("/specimen/new/image", methods=["GET", "POST"])
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
        return render_template("specimen/newspecimen.html", form=form, step="image")


@app.route("/specimen/new/taxonomy", methods=["GET", "POST"])
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
                "specimen/newspecimen.html", form=form, step="taxonomy"
            )
    else:
        return ("", 403)


@app.route("/specimen/new/details", methods=["GET", "POST"])
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
                "specimen/newspecimen.html", form=form, step="collection_details"
            )
    else:
        return ("", 403)


# DISPLAY SPECIMEN
@app.route("/specimen/<int:specimen_id>", methods=["POST", "GET"])
def display_specimen(specimen_id):
    """Full page display of specimen with all info
    Includes form in modal popup with ability to edit specimen data (not the image)"""

    specimen = Specimen.query.get_or_404(specimen_id)

    return render_template("specimen/displayspecimen.html", specimen=specimen)


# DELETE SPECIMEN
@app.route("/specimen/<int:specimen_id>/delete", methods=["POST"])
@login_required
def delete_specimen(specimen_id):
    """Allows specimen creator to delete a specimen"""

    specimen = Specimen.query.get_or_404(specimen_id)

    if current_user.id == specimen.user_id:

        db.session.delete(specimen)
        db.session.commit()

        flash("Specimen deleted!", "success")
        return redirect(f"/profile/{current_user.id}")
    else:
        return ("", 403)


# EDIT SPECIMEN - IMAGE
@app.route("/specimen/<int:specimen_id>/edit_image", methods=["GET", "POST"])
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
                "specimen/editspecimen.html", form=form, specimen=specimen, step="image"
            )
    else:
        return ("", 403)


# EDIT SPECIMEN - TAXONOMY
@app.route("/specimen/<int:specimen_id>/edit_taxonomy", methods=["GET", "POST"])
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
                "specimen/editspecimen.html",
                form=form,
                specimen=specimen,
                step="taxonomy",
            )
    else:
        return ("", 403)


# EDIT SPECIMEN - DETAILS
@app.route("/specimen/<int:specimen_id>/edit_details", methods=["GET", "POST"])
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
                "specimen/editspecimen.html",
                form=form,
                specimen=specimen,
                step="details",
            )
    else:
        return ("", 403)


# ADD SPECIMEN TO A COLLECTION
@app.route("/specimen/<int:specimen_id>/add_to_collection", methods=["GET", "POST"])
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
        "specimen/addspecimentocollection.html", form=form, specimen=specimen
    )


#############################
# Collection routes


@app.route("/collection/new", methods=["POST", "GET"])
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
        return redirect(f"/profile/{current_user.id}")

    else:
        return render_template("collection/newcollection.html", form=form)


@app.route("/collection/<int:collection_id>")
def view_collection(collection_id):
    """View all specimens in a collection"""

    collection = Collection.query.get_or_404(collection_id)
    specimens_in_collection = [specimen for specimen in collection.specimens]
    num_specimens = len(specimens_in_collection)
    user = User.query.get_or_404(collection.user_id)

    return render_template(
        "collection/displaycollection.html",
        collection=collection,
        num_specimens=num_specimens,
        user=user,
        specimens_in_collection=specimens_in_collection,
    )


@app.route("/collection/<int:collection_id>/edit", methods=["POST", "GET"])
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
                "collection/editcollection.html", form=form, collection=collection
            )
    else:
        return ("", 403)


@app.route("/collection/<int:collection_id>/delete", methods=["POST"])
@login_required
def delete_collection(collection_id):
    collection = Collection.query.get_or_404(collection_id)

    db.session.delete(collection)
    db.session.commit()

    flash(f"{collection.name} collection deleted", "success")
    return redirect(f"/profile/{current_user.id}")


@app.route(
    "/collection/<int:collection_id>/remove_specimen/<int:specimen_id>",
    methods=["POST"],
)
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

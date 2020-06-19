from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """connect to database"""

    db.app = app
    db.init_app(app)


class User(UserMixin, db.Model):
    """User"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    bio = db.Column(db.Text)
    location = db.Column(db.String)
    profile_pic = db.Column(
        db.Text,
        default="https://cdn.mos.cms.futurecdn.net/BwL2586BtvBPywasXXtzwA-320-80.jpeg",
    )

    specimens = db.relationship("Specimen", backref="users", cascade="delete")

    @classmethod
    def signup(cls, username, password, bio, location, profile_pic):
        """signs up new user, hashes PW, and adds user"""

        hashed_pw = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(
            username=username,
            password=hashed_pw,
            bio=bio,
            location=location,
            profile_pic=profile_pic,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Finds user with username and password"""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


###########################
# Specimen Tables(s)
class Specimen(db.Model):
    """Specimen Image
    Creates a new specimen ID and adds imgur image link from the upload"""

    __tablename__ = "specimens"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    link = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    details = db.relationship(
        "Details", uselist=False, cascade="delete", backref="specimens"
    )
    taxonomy = db.relationship(
        "Taxonomy", uselist=False, cascade="delete", backref="specimens"
    )
    collections = db.relationship(
        "Collection", secondary="collection_specimens", backref="specimens"
    )


class Taxonomy(db.Model):
    """Creates the taxonomy and authorship information of a specimen"""

    __tablename__ = "taxonomy"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    specimen_id = db.Column(
        db.Integer, db.ForeignKey("specimens.id"), nullable=False, unique=True
    )
    common_name = db.Column(db.Text, default="Unknown")
    species = db.Column(db.Text, default="Unknown")
    genus = db.Column(db.Text, default="Unknown")
    family = db.Column(db.Text, default="Unknown")
    order = db.Column(db.Text, default="Unknown")
    phylum = db.Column(db.Text, default="Unknown")
    kingdom = db.Column(db.Text, default="Unknown")
    authorship = db.Column(db.Text, default="Unknown")


class Details(db.Model):
    """Creates collection details of a specimen"""

    __tablename__ = "details"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    specimen_id = db.Column(
        db.Integer, db.ForeignKey("specimens.id"), nullable=False, unique=True
    )
    date = db.Column(db.Text)
    location = db.Column(db.Text)
    habitat = db.Column(db.Text)
    county = db.Column(db.Text)
    state = db.Column(db.Text)
    notes = db.Column(db.Text)


###########################
# Collection Table(s)
class Collection(db.Model):
    """Collection"""

    __tablename__ = "collections"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String, nullable=False)
    info = db.Column(db.Text)
    # image = db.Column(db.Text)

    # specimens = db.relationship("Specimen", secondary="collection_specimens", backref="collections")


class CollectionSpecimen(db.Model):
    """Maps collection to a song"""

    __tablename__ = "collection_specimens"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    collection_id = db.Column(
        db.Integer, db.ForeignKey("collections.id"), nullable=False
    )
    specimen_id = db.Column(db.Integer, db.ForeignKey("specimens.id"), nullable=False)

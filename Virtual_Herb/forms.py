from flask_wtf import FlaskForm
from flask_wtf.html5 import URLField

from flask_wtf.file import FileAllowed, FileRequired
from wtforms import (
    StringField,
    PasswordField,
    TextAreaField,
    BooleanField,
    FileField,
    DateField,
    SelectField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    InputRequired,
    Optional,
    Required,
    url,
)


class SignupForm(FlaskForm):
    """Form to create a new user"""

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=4, message="Username must be at least 4 characters."),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6, message="Password must be at least 6 characters."),
        ],
    )
    bio = TextAreaField("About (Optional)")
    location = StringField("Location (Optional)")
    img_url = URLField("Profile Picture (Optional)", validators=[Optional(), url()])


class EditUserForm(FlaskForm):
    """Form to edit user details"""

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=4, message="Username must be at least 4 characters."),
        ],
    )
    bio = TextAreaField("About")
    location = StringField("Location")
    img_url = URLField("Profile Picture", validators=[Optional(), url()])


class LoginForm(FlaskForm):
    """Form to login existing user"""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


class SpecimenImageForm(FlaskForm):
    """Form to upload image"""

    image = FileField(
        "Image",
        validators=[
            FileRequired(),
            FileAllowed(["jpg", "png"], "Only .jpg and .png images allowed!"),
        ],
    )


class TaxonomyForm(FlaskForm):
    """Form for taxonomy information"""

    common_name = StringField("Common Name")
    species = StringField("Species")
    genus = StringField("Genus")
    family = StringField("Family")
    order = StringField("Order")
    phylum = StringField("Phylum")
    kingdom = StringField("Kingdom")
    authorship = StringField("Authorship")


class CollectionDetailsForm(FlaskForm):
    """Form for collection details"""

    date = StringField("Date Collected")
    location = StringField("Location")
    habitat = StringField("Habitat")
    county = StringField("County")
    state = StringField("State")
    notes = TextAreaField("Notes")


class CollectionForm(FlaskForm):
    """Form for collection"""

    name = StringField("Name of Collection", validators=[DataRequired()])
    info = TextAreaField("About this Collection")


class AddSpecimenToCollectionForm(FlaskForm):
    """Form dropdown with available collections to add it to"""

    collection = SelectField("Add to collection?", coerce=int)

# import os
from unittest import TestCase
from sqlalchemy import exc
from app import app

from models import (
    db,
    User,
    Specimen,
    Taxonomy,
    Details,
    Collection,
    CollectionSpecimen,
)

# os.environ["DATABASE_URL"] = "postgresql:///herbarium_test"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///herbarium_test"

app.config["SQLALCHEMY_ECHO"] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.drop_all()
db.create_all()


class TestSpecimenModel(TestCase):
    """Create specimen, taxonomy, details and check if they all work"""

    def setUp(self):
        """create test user and specimens"""

        # db.session.close()
        db.session.close()
        db.drop_all()
        db.create_all()

        user1 = User.signup("tester1", "password1", None, None, None)
        user1id = 11
        user1.id = user1id

        specimen1 = Specimen(link="https://i.imgur.com/pMkflKn.jpg", user_id=11,)
        specimen1id = 12
        specimen1.id = specimen1id

        specimen1taxonomy = Taxonomy(
            common_name="Red Oak",
            specimen_id=12,
            species="Quercus rubra",
            genus="Quercus",
            family="Fagaceae",
            order="Fagales",
            phylum="Tracheophyta",
            kingdom="Plantae",
            authorship="L.",
        )

        specimen1details = Details(
            specimen_id=12,
            date="3-12-2019",
            location="Rock Bridge State Park",
            habitat="NE-facing slope",
            county="Boone",
            state="Missouri",
            notes="No Notes",
        )

        specimen2 = Specimen(link="https://i.imgur.com/pMkflKn.jpg", user_id=11,)
        specimen2id = 13
        specimen2.id = specimen2id

        specimen2taxonomy = Taxonomy(
            common_name=None,
            specimen_id=13,
            species=None,
            genus=None,
            family=None,
            order=None,
            phylum=None,
            kingdom=None,
            authorship=None,
        )

        specimen2details = Details(
            specimen_id=13,
            date="3-12-2019",
            location=None,
            habitat="",
            county=None,
            state=None,
            notes=None,
        )

        db.session.add_all(
            [
                specimen1,
                specimen1taxonomy,
                specimen1details,
                specimen2,
                specimen2taxonomy,
                specimen2details,
            ]
        )

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback
        return resp

    def test_specimen_model(self):
        specimen = Specimen.query.get(12)
        self.assertEqual(specimen.link, "https://i.imgur.com/pMkflKn.jpg")
        self.assertEqual(specimen.id, 12)
        self.assertEqual(specimen.taxonomy.species, "Quercus rubra")
        self.assertEqual(specimen.details.county, "Boone")

    def test_specimen_defaults(self):
        """Test default values and nullable columns"""
        specimen = Specimen.query.get(13)
        self.assertEqual(specimen.link, "https://i.imgur.com/pMkflKn.jpg")
        self.assertEqual(specimen.taxonomy.common_name, "Unknown")
        self.assertEqual(specimen.details.location, None)

    def test_no_link_fields(self):
        """Test entering no info on non-nullable fields (image link)"""
        specimen3 = Specimen(link=None, user_id=11,)
        specimen3id = 14
        specimen3.id = specimen3id

        specimen3taxonomy = Taxonomy(
            common_name=None,
            specimen_id=14,
            species=None,
            genus=None,
            family=None,
            order=None,
            phylum=None,
            kingdom=None,
            authorship=None,
        )

        specimen3details = Details(
            specimen_id=14,
            date="3-12-2019",
            location=None,
            habitat="",
            county=None,
            state=None,
            notes=None,
        )

        db.session.add_all(
            [specimen3, specimen3taxonomy, specimen3details,]
        )

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

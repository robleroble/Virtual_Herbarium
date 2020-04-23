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

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///herbarium_test"


app.config["SQLALCHEMY_ECHO"] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.drop_all()
db.create_all()


class CollectionModelTestCase(TestCase):
    """Test creation of model"""

    def setUp(self):
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

        collection1 = Collection(
            user_id=11,
            name="Test Collection",
            info="Here is some generic test text about this collection.",
        )

        collection1id = 13
        collection1.id = collection1id

        db.session.add_all(
            [specimen1, specimen1taxonomy, specimen1details, collection1]
        )

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback
        return resp

    def test_collection_model(self):

        collection = Collection.query.get(13)
        self.assertEqual(collection.id, 13)
        self.assertEqual(collection.name, "Test Collection")
        self.assertIn("Here is some", collection.info)

    def test_collection_empty_no_name(self):
        """Test collection when no name is inputted (name - non-nullable)"""
        collection2 = Collection(user_id=11, name=None, info=None)
        db.session.add(collection2)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_collection_specimen(self):
        """Add a specimen (ID 12) to a collection
        Doesn't seem to work unless you are referencing a collection object (can't just use a number)"""
        collection = Collection.query.get(13)
        coll_spec1 = CollectionSpecimen(specimen_id=12, collection_id=collection.id)
        coll_spec1id = 3
        coll_spec1.id = coll_spec1id
        db.session.add(coll_spec1)

        collspec = CollectionSpecimen.query.get(3)
        self.assertEqual(collspec.specimen_id, 12)
        self.assertEqual(collspec.collection_id, 13)

    def test_collection_specimen_wrong_specID(self):
        """Add specimen w/non-existent ID to a collection"""
        collection = Collection.query.get(13)
        coll_spec2 = CollectionSpecimen(specimen_id=99, collection_id=collection.id)
        coll_spec2id = 2
        coll_spec2.id = coll_spec2id
        db.session.add(coll_spec2)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

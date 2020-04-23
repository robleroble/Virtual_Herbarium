from unittest import TestCase
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
app.config["WTF_CSRF_ENABLED"] = False

db.drop_all()
db.create_all()


class TestAnonymousUserSpecimenViews(TestCase):
    """Tests to make sure anonymous user can't create/edit/delete collections"""

    def setUp(self):
        """Creates test user and specimens"""

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
        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_specimen_page_anon(self):
        """Test view specimen page for no "add to collection" btn for anon user"""
        with app.test_client() as client:
            resp = client.get("/specimen/12")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Quercus", html)
            self.assertNotIn("Add to collection", html)

    def test_profile_page_anon(self):
        """Tests to be sure there is no 'Create Collection' button for anon user"""
        with app.test_client() as client:
            resp = client.get("/profile/11")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("tester1", html)
            self.assertNotIn(">Create<br/>Collection", html)

    def test_create_collection_page_anon(self):
        """Tests if anon user can go to create collection page"""
        with app.test_client() as client:
            resp = client.get("/collection/new")

            self.assertEqual(resp.status_code, 401)

    def test_collection_edit_page_anon(self):
        """Tests collection page for anon user"""
        with app.test_client() as client:
            resp = client.get("/collection/13")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test Collection", html)
            self.assertNotIn("Delete Collection", html)
            self.assertNotIn("Edit Collection", html)

    def test_edit_collection_anon(self):
        """Test if anon user can access edit collection page"""
        with app.test_client() as client:
            resp = client.get("/collection/13/edit")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 401)

    def test_post_edit_collection_anon(self):
        """Test if anon user can edit a collection"""
        with app.test_client() as client:
            resp = client.post(
                "/collection/13/edit", data={"name": "Not a test collection"}
            )
            collection = Collection.query.get(13)

            self.assertEqual(collection.name, "Test Collection")
            self.assertEqual(resp.status_code, 401)

    def test_delete_collection_anon(self):
        """Test if anonymous user can delete a collection"""
        with app.test_client() as client:
            resp = client.post("/collection/13/delete")

            self.assertEqual(resp.status_code, 401)


class TestLoggedInUserSpecimenViews(TestCase):
    """Tests to make sure anonymous user can't create/edit/delete collections"""

    def setUp(self):
        """Creates test user and specimens"""

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
        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_specimen_page_logged_in(self):
        """Test view specimen page for "add to collection" btn for logged-in user"""
        with app.test_client() as client:
            client.post(
                "/login",
                data={"username": "tester1", "password": "password1"},
                follow_redirects=True,
            )
            resp = client.get("/specimen/12")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Quercus", html)
            self.assertIn("Add to collection", html)

    def test_profile_page_logged_in(self):
        """Tests to be sure there is 'Create Collection' button for logged-in user"""
        with app.test_client() as client:
            client.post(
                "/login",
                data={"username": "tester1", "password": "password1"},
                follow_redirects=True,
            )
            resp = client.get("/profile/11")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("tester1", html)
            self.assertIn("Create<br/>Collection", html)

    def test_create_collection_page_logged_in(self):
        """Tests if logged-in user can go to create collection page"""
        with app.test_client() as client:
            client.post(
                "/login",
                data={"username": "tester1", "password": "password1"},
                follow_redirects=True,
            )
            resp = client.get("/collection/new")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Create a new collection!", html)

    def test_collection_edit_page_logged_in(self):
        """Tests collection page for logged-in (should have edit and delete collection btns)"""
        with app.test_client() as client:
            client.post(
                "/login",
                data={"username": "tester1", "password": "password1"},
                follow_redirects=True,
            )
            resp = client.get("/collection/13")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test Collection", html)
            self.assertIn("Delete Collection", html)
            self.assertIn("Edit Collection", html)

    def test_edit_collection_logged_in(self):
        """Test if logged-in user can access edit collection page"""
        with app.test_client() as client:
            client.post(
                "/login",
                data={"username": "tester1", "password": "password1"},
                follow_redirects=True,
            )
            resp = client.get("/collection/13/edit")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Edit collection", html)

    def test_post_edit_collection_logged_in(self):
        """Test if logged-in user can edit a collection"""
        with app.test_client() as client:
            client.post(
                "/login",
                data={"username": "tester1", "password": "password1"},
                follow_redirects=True,
            )
            resp = client.post(
                "/collection/13/edit",
                data={"name": "Not a test collection"},
                follow_redirects=True,
            )
            collection = Collection.query.get(13)

            self.assertEqual(collection.name, "Not a test collection")
            self.assertEqual(resp.status_code, 200)

    def test_delete_collection_logged_in(self):
        """Test if logged-in user can delete a collection"""
        with app.test_client() as client:
            client.post(
                "/login",
                data={"username": "tester1", "password": "password1"},
                follow_redirects=True,
            )
            resp = client.post("/collection/13/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            collections = Collection.query.filter_by(user_id=11).all()
            self.assertEqual(len(collections), 0)
            self.assertIn("You don't have any collections", html)
            self.assertEqual(resp.status_code, 200)

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
    """Test to make sure anonymous users can't create/edit/delete specimens"""

    def setUp(self):
        """create test user and specimens"""

        # db.session.close()
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

        db.session.add_all([specimen1, specimen1taxonomy, specimen1details])
        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_specimen_page_anon(self):
        """test the /specimen/<id> page for anon user"""
        with app.test_client() as client:
            resp = client.get("/specimen/12")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Quercus", html)
            self.assertNotIn("Edit", html)

    def test_edit_specimen_img_anon(self):
        """Test if anonymous user can access edit specimen image page (they shouldn't)"""
        with app.test_client() as client:
            resp = client.get("/specimen/12/edit_image")

            self.assertEqual(resp.status_code, 401)

    def test_edit_specimen_taxonomy_anon(self):
        """Test if anonymous user can access edit specimen taxonomy page (they shouldn't)"""
        with app.test_client() as client:
            resp = client.get("/specimen/12/edit_taxonomy")

            self.assertEqual(resp.status_code, 401)

    def test_edit_specimen_details_anon(self):
        """Test if anonymous user can access edit specimen details page (they shouldn't)"""
        with app.test_client() as client:
            resp = client.get("/specimen/12/edit_details")

            self.assertEqual(resp.status_code, 401)

    # # Need to figure out how to test file input forms
    # def test_edit_specimen_link_anon(self):
    #     """Test if anon user can post a change to the image url"""

    def test_edit_specimen_taxonomy_species_anon(self):
        """Test if anon user can edit a specimens species name (they shouldn't)"""
        with app.test_client() as client:
            resp = client.post(
                "/specimen/12/edit_taxonomy", data={"species": "Notquercus rubra"}
            )
            specimen = Specimen.query.get(12)

            self.assertEqual(specimen.taxonomy.species, "Quercus rubra")
            self.assertEqual(resp.status_code, 401)

    def test_edit_specimen_details_notes_anon(self):
        """Test if anon user can edit a specimen's collection notes (they shouldn't)"""
        with app.test_client() as client:
            resp = client.post(
                "/specimen/12/edit_details", data={"notes": "Now we have notes!"}
            )

            specimen = Specimen.query.get(12)

            self.assertNotEqual(specimen.details.notes, "Now we have notes!")
            self.assertEqual(resp.status_code, 401)

    def test_delete_specimen_anon(self):
        """Test if anon user can delete a specimen"""
        with app.test_client() as client:
            resp = client.post("/specimen/12/delete")

            self.assertEqual(resp.status_code, 401)


class TestLoggedInUserSpecimenViews(TestCase):
    """Create specimen, taxonomy, details and check if they all work"""

    def setUp(self):
        """create test user and specimens"""

        # db.session.close()
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

        db.session.add_all([specimen1, specimen1taxonomy, specimen1details])
        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_specimen_page_logged_in(self):
        """test the /specimen/<id> page for logged-in user"""
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
            self.assertIn("Edit", html)

    def test_edit_specimen_img_logged_in(self):
        """Test if logged-in user can access edit specimen image page"""
        with app.test_client() as client:
            client.post(
                "/login",
                data={"username": "tester1", "password": "password1"},
                follow_redirects=True,
            )
            resp = client.get("/specimen/12/edit_image")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Upload a new image of your specimen", html)

    def test_edit_specimen_taxonomy_logged_in(self):
        """Test if logged-in user can access edit specimen taxonomy page"""
        with app.test_client() as client:
            client.post(
                "/login",
                data={"username": "tester1", "password": "password1"},
                follow_redirects=True,
            )
            resp = client.get("/specimen/12/edit_taxonomy")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Edit specimen name and taxonomy information", html)

    def test_edit_specimen_details_anon(self):
        """Test if anonymous user can access edit specimen details page (they shouldn't)"""
        with app.test_client() as client:
            client.post(
                "/login",
                data={"username": "tester1", "password": "password1"},
                follow_redirects=True,
            )
            resp = client.get("/specimen/12/edit_details")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Edit collection details", html)

    # # Need to figure out how to test file input forms
    # def test_edit_specimen_link_anon(self):
    #     """Test if anon user can post a change to the image url"""

    def test_edit_specimen_taxonomy_species_logged_in(self):
        """Test if logged-in user can edit a specimens species name"""
        with app.test_client() as client:
            client.post(
                "/login",
                data={"username": "tester1", "password": "password1"},
                follow_redirects=True,
            )
            resp = client.post(
                "/specimen/12/edit_taxonomy",
                data={"species": "Notquercus rubra"},
                follow_redirects=True,
            )
            html = resp.get_data(as_text=True)
            specimen = Specimen.query.get(12)

            self.assertEqual(specimen.taxonomy.species, "Notquercus rubra")
            self.assertIn("Notquercus rubra", html)
            self.assertEqual(resp.status_code, 200)

    def test_edit_specimen_details_notes_logged_in(self):
        """Test if logged-in user can edit a specimen's collection notes"""
        with app.test_client() as client:
            client.post(
                "/login",
                data={"username": "tester1", "password": "password1"},
                follow_redirects=True,
            )
            resp = client.post(
                "/specimen/12/edit_details",
                data={"notes": "Now we have notes!"},
                follow_redirects=True,
            )
            html = resp.get_data(as_text=True)

            specimen = Specimen.query.get(12)

            self.assertEqual(specimen.details.notes, "Now we have notes!")
            self.assertIn("Now we have notes!", html)
            self.assertEqual(resp.status_code, 200)

    def test_delete_specimen_logged_in(self):
        """Test if logged-in user can delete a specimen"""
        with app.test_client() as client:
            client.post(
                "/login",
                data={"username": "tester1", "password": "password1"},
                follow_redirects=True,
            )
            resp = client.post("/specimen/12/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            specimens = Specimen.query.filter_by(user_id=11).all()

            self.assertEqual(len(specimens), 0)
            self.assertIn("You don't have any specimens", html)
            self.assertEqual(resp.status_code, 200)

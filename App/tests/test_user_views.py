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


class AnonymousUserTestViews(TestCase):
    """Test user page views."""

    def setUp(self):
        """Create some test users"""

        db.drop_all()
        db.create_all()

        user1 = User.signup("tester1", "password1", None, None, None)
        user1id = 11
        user1.id = user1id

        newuser = User.signup(
            username="testuser",
            password="password",
            bio=None,
            location=None,
            profile_pic=None,
        )
        userid = 22
        newuser.id = userid

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_homepage(self):
        """checks for signup/login in navbar for anon user"""
        with app.test_client() as client:
            resp = client.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Sign Up", html)
            self.assertIn("Log In", html)
            self.assertIn("The Herbarium", html)
            self.assertNotIn("Log Out", html)
            self.assertNotIn("Profile", html)

    def test_profile_page_not_logged_in(self):
        """checks if profile page for tester1/user1 is correct page"""
        with app.test_client() as client:
            resp = client.get("/profile/11")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("tester1", html)
            self.assertNotIn("Edit", html)

    def test_edit_profile(self):
        """checks if anonymous user gets 401 for edit user route"""
        with app.test_client() as client:
            resp = client.get("/profile/11/edit")

            self.assertEqual(resp.status_code, 401)

    def test_edit_profile_username(self):
        """checks edit user route with sending edited username"""
        with app.test_client() as client:
            resp = client.post("/profile/11/edit", data={"username": "newtester1"})

            self.assertEqual(resp.status_code, 401)

    def test_delete_profile(self):
        """checks if anon user gets 401 for delete user route"""
        with app.test_client() as client:
            resp = client.post("/profile/11/delete")

            self.assertEqual(resp.status_code, 401)

    def test_login(self):
        """logs in newuser"""
        with app.test_client() as client:
            resp = client.post(
                "/login",
                data={"username": "testuser", "password": "password"},
                follow_redirects=True,
            )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser", html)


class LoggedInUserTestViews(TestCase):
    """test cases for logged in user"""

    def setUp(self):
        """Create some test users"""

        db.session.close()
        db.drop_all()
        db.create_all()

        app.config["LOGIN_DISABLED"] = True

        user1 = User.signup("tester1", "password1", None, None, None)
        user1id = 11
        user1.id = user1id

        self.newuser = User.signup(
            username="testuser",
            password="password",
            bio=None,
            location=None,
            profile_pic=None,
        )
        self.newuserid = 22
        self.newuser.id = self.newuserid

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_homepage(self):
        """check homepage for authenticated user"""
        with app.test_client() as client:
            client.post(
                "/login",
                data={"username": "testuser", "password": "password"},
                follow_redirects=True,
            )

            resp = client.get("/")

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Log Out", html)

    def test_delete_profile_logged_in(self):
        """tests delete user if logged in"""
        with app.test_client() as client:
            client.post(
                "/login",
                data={"username": "testuser", "password": "password"},
                follow_redirects=True,
            )

            resp = client.post("/profile/22/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("BioBlitz", html)
            self.assertIn("Log In", html)

    def test_delete_another_profile_while_logged_in(self):
        """tests if a logged in user can delete another user's profile"""
        with app.test_client() as client:
            client.post(
                "/login",
                data={"username": "testuser", "password": "password"},
                follow_redirects=True,
            )

            resp = client.post("/profile/11/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 403)

    def test_display_editform_user_logged_in(self):
        """tests if edit form is displayed for logged in user"""
        with app.test_client() as client:
            client.post(
                "/login",
                data={"username": "testuser", "password": "password"},
                follow_redirects=True,
            )

            resp = client.get("/profile/22/edit")

            self.assertEqual(resp.status_code, 200)

    def test_edit_user_logged_in(self):
        """tests editing user details for logged in user"""
        with app.test_client() as client:
            client.post(
                "/login",
                data={"username": "testuser", "password": "password"},
                follow_redirects=True,
            )

            resp = client.post(
                "/profile/22/edit",
                data={"username": "newtester1"},
                follow_redirects=True,
            )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("newtester1", html)

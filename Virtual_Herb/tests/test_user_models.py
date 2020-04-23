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


class UserModelTestCase(TestCase):
    """Test models for users"""

    def setUp(self):
        """create test users"""
        db.session.close()
        db.drop_all()
        db.create_all()

        user1 = User.signup("tester1", "password1", None, None, None)
        user1id = 11
        user1.id = user1id

        db.session.commit()

        self.user1 = user1
        self.user1id = user1id

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback
        return resp

    def test_user_model(self):
        user = User(
            username="testuser",
            password="password",
            bio="I'm not real! I'm a test! Help me!",
            location=None,
        )

        db.session.add(user)
        db.session.commit()

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.password, "password")
        self.assertEqual(user.bio, "I'm not real! I'm a test! Help me!")
        self.assertEqual(user.location, None)

    def test_valid_signup(self):
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

        get_user = User.query.get(userid)
        self.assertIsNotNone(get_user)
        self.assertEqual(get_user.username, "testuser")
        self.assertNotEqual(get_user.password, "password")
        self.assertIsNone(get_user.bio)
        self.assertIsNone(get_user.location)
        self.assertIsNotNone(get_user.profile_pic)
        self.assertEqual(
            get_user.profile_pic,
            "https://cdn.mos.cms.futurecdn.net/BwL2586BtvBPywasXXtzwA-320-80.jpeg",
        )
        self.assertTrue(get_user.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        """Signup without a username"""
        invalid = User.signup(None, "password", None, None, None)
        uid = 123456789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_duplicate_username_signup(self):
        """Tests to make sure signup doesn't work with a non-unique username"""
        invalid = User.signup("tester1", "password", None, None, None)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        """Signup without a password"""
        with self.assertRaises(ValueError) as context:
            User.signup("userrrrrr", None, None, None, None)

    ### Authentication Tests

    def test_valid_authentication(self):
        """Log in tester1"""
        user = User.authenticate(self.user1.username, "password1")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.user1id)

    def test_invalid_username(self):
        """Use incorrect username on login"""
        self.assertFalse(User.authenticate("tester22", "password1"))

    def test_wrong_password(self):
        """User incorrect password on login"""
        self.assertFalse(User.authenticate(self.user1.username, "password22"))

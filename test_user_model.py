"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
# db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test model for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_following_other(self):
        """Is one user following another?"""

        u1 = User(
            email="test1@test.com",
            username="test1",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="test2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        u2.followers.append(u1)
        self.assertEqual(len(u2.followers), 1)

        # is_following should return 1 for u1=>u2
        self.assertEqual(User.is_following(u1, u2), 1)

        # is_following should return 0 for u2=>u1
        self.assertEqual(User.is_following(u2, u1), 0)

        # is_followed_by should return 1 for u2=>u1
        self.assertEqual(User.is_followed_by(u2, u1), 1)

        # is_following should return 0 for u2=>u1
        self.assertEqual(User.is_followed_by(u1, u2), 0)

    def test_user_add_valid(self):
        """Does User.signup work when given valid parameters?"""

        User.signup(username="testuser",
                    email="test@test.com", password="HASHED_PASSWORD", image_url="")
        u = User.query.filter_by(username="testuser").all()
        self.assertEqual(len(u), 1)

    def test_user_add_invalid(self):
        """Does User.signup work when given invalid parameters?"""

        with self.assertRaises(ValueError):
            User.signup(username="testuser", email="test@test.com",
                        password="", image_url="")

    def test_user_authenticate_valid(self):
        """Does User.authenticate return a user when passed valid parameters?"""

        User.signup(username="testuser",
                    email="test@test.com", password="HASHED_PASSWORD", image_url="")

        self.assertIsInstance(User.authenticate(
            "testuser", "HASHED_PASSWORD"), User)

    def test_user_auth_invalid_params(self):
        """Does User.authenticate fail to return a user when the
        username or password is invalid?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        self.assertFalse(User.authenticate("test", "HASHED_PASSWORD"))
        self.assertFalse(User.authenticate("tesuser", "password"))

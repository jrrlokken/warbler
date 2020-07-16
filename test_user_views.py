# User view tests

from unittest import TestCase
from app import app, do_login, CURR_USER_KEY
from models import db, connect_db, User, Message, Follows

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///warbler-test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True


class UserViewsTestCase(TestCase):
    """Tests for user views."""

    def setUp(self):
        """Setup data for tests."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser_id = 5555
        self.testuser.id = self.testuser_id
        self.u1 = User.signup("abc", "test1@test.com", "password", None)
        self.u1_id = 778
        self.u1.id = self.u1_id
        self.u2 = User.signup("efg", "test2@test.com", "password", None)
        self.u2_id = 889
        self.u2.id = self.u2_id
        self.u3 = User.signup("hij", "test3@test.com", "password", None)
        self.u4 = User.signup("testing", "test4@test.com", "password", None)

        db.session.commit()

    def tearDown(self):
        """Clean up."""

        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_list_view(self):
        """Test the main users view."""

        with self.client as client:
            res = client.get("/users")

            self.assertIn("@testuser", str(res.data))
            self.assertIn("@abc", str(res.data))
            self.assertIn("@efg", str(res.data))
            self.assertIn("@hij", str(res.data))
            self.assertIn("@testing", str(res.data))

    def test_user_search(self):
        """Test user search."""

        with self.client as client:
            res = client.get("/users?q=test")

            self.assertIn("@testuser", str(res.data))
            self.assertIn("@testing", str(res.data))

            self.assertNotIn("@efg", str(res.data))
            self.assertNotIn("@hij", str(res.data))
            self.assertNotIn("@abc", str(res.data))

    def test_user_show(self):
        """Test user detail view."""

        with self.client as client:
            res = client.get(f"/users/{self.testuser_id}")

            self.assertEqual(res.status_code, 200)
            self.assertIn("@testuser", str(res.data))

    def setup_likes(self):
        m1 = Message(text="new warble", user_id=self.testuser_id)
        m2 = Message(text="lunch warble", user_id=self.testuser_id)
        m3 = Message(id=9876, text="likable warble", user_id=self.u1_id)
        db.session.add_all([m1, m2, m3])

# User view tests

from unittest import TestCase
from app import app, do_login, CURR_USER_KEY
from models import db, connect_db, User, Message, Follows, Likes

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

    def setup_likes(self):
        m1 = Message(text="new warble", user_id=self.testuser_id)
        m2 = Message(text="lunch warble", user_id=self.testuser_id)
        m3 = Message(id=9876, text="likable warble", user_id=self.u1_id)
        db.session.add_all([m1, m2, m3])
        db.session.commit()

        like = Likes(user_id=self.testuser_id, message_id=9876)

        db.session.add(like)
        db.session.commit()

    def setup_followers(self):
        f1 = Follows(user_being_followed_id=self.u1_id, user_following_id=self.testuser_id)
        f2 = Follows(user_being_followed_id=self.u2_id, user_following_id=self.testuser_id)
        f3 = Follows(user_being_followed_id=self.testuser_id, user_following_id=self.u1_id)

        db.session.add_all([f1, f2, f3])
        db.session.commit()

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

    def test_add_like(self):
        m = Message(id=1988, text="Scary pumpkins abound!", user_id=self.u1_id)
        db.session.add(m)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            res = client.post("/users/add_like/1988", follow_redirects=True)
            self.assertEqual(res.status_code, 200)

            likes = Likes.query.filter(Likes.message_id == 1988).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.testuser_id)

    def test_remove_like(self):
        self.setup_likes()

        m = Message.query.filter(Message.text == "likable warble").one()

        self.assertIsNotNone(m)
        self.assertNotEqual(m.user_id, self.testuser_id)

        l = Likes.query.filter(Likes.user_id == self.testuser_id and Likes.message_id == m.id).first()

        self.assertIsNotNone(l)

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            res = client.post(f"/users/add_like/{m.id}", follow_redirects=True)
            self.assertEqual(res.status_code, 200)

            likes = Likes.query.filter(Likes.message_id == m.id).all()
            self.assertEqual(len(likes), 0)

    def test_show_following(self):

        self.setup_followers()
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            res = client.get(f"/users/{self.testuser_id}/following")
            self.assertEqual(res.status_code, 200)
            self.assertIn("@abc", str(res.data))
            self.assertIn("@efg", str(res.data))
            self.assertNotIn("@hij", str(res.data))
            self.assertNotIn("@testing", str(res.data))

    def test_show_followers(self):

        self.setup_followers()
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            res = client.get(f"/users/{self.testuser_id}/followers")

            self.assertIn("@abc", str(res.data))
            self.assertNotIn("@efg", str(res.data))
            self.assertNotIn("@hij", str(res.data))
            self.assertNotIn("@testing", str(res.data))

    def test_unauthorized_access(self):
        """Test access to following, followers, likes without authorization."""

        self.setup_followers()
        self.setup_likes()

        with self.client as client:
            res_following = client.get(f"/users/{self.testuser_id}/following", follow_redirects=True)
            self.assertEqual(res_following.status_code, 200)
            self.assertIn("Unauthorized access.", str(res_following.data))

            res_followers = client.get(f"/users/{self.testuser_id}/followers", follow_redirects=True)
            self.assertEqual(res_followers.status_code, 200)
            self.assertIn("Unauthorized access.", str(res_following.data))

            res_likes = client.get(f"/users/{self.testuser_id}/likes", follow_redirects=True)
            self.assertEqual(res_likes.status_code, 200)
            self.assertIn("Unauthorized access.", str(res_following.data))

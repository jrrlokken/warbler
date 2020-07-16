"""Message View tests."""

from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser_id = 9999
        self.testuser.id = self.testuser_id

        db.session.commit()

    def tearDown(self):
        """Clean up after oneself."""

        res = super().tearDown()
        db.session.rollback()
        return res

    def test_show_message(self):
        """Message show view."""

        m = Message(
            id=9998,
            text="Aragorn!",
            user_id=self.testuser_id
        )

        db.session.add(m)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = client.get("/messages/9998")

            self.assertEqual(res.status_code, 200)

    def test_add_message(self):
        """Can a user add a message?"""

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = client.post("/messages/new", data={"text": "Do they, Gandalf?"})

            self.assertEqual(res.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Do they, Gandalf?")

    def test_show_message_invalid(self):
        """Message detail view for an invalid message id."""

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = client.get("/messages/12345678")

            self.assertEqual(res.status_code, 404)

    def test_message_delete(self):
        """Delete message."""

        m = Message(
            id=9998,
            text="Aragorn!",
            user_id=self.testuser_id
        )

        db.session.add(m)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = client.post("/messages/9998/delete", follow_redirects=True)

            self.assertEqual(res.status_code, 200)

    def test_delete_message_noauth(self):
        """Attempt to delete a message without authorization."""

        m = Message(
            id=9998,
            text="Aragorn!",
            user_id=self.testuser_id
        )

        db.session.add(m)
        db.session.commit()

        with self.client as client:
            res = client.post("/messages/9998/delete", follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Unauthorized access.", str(res.data))

            m = Message.query.get(9998)
            self.assertIsNotNone(m)

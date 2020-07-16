"""Message model tests."""

from app import app
import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

db.drop_all()
db.create_all()


class MessageModelTestCase(TestCase):
    """Test model for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_message_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        m = Message(
            text="HOLLA!",
            user_id=u.id
        )

        db.session.add(m)
        db.session.commit()

        # User should have 1 message
        self.assertEqual(len(user.messages), 1)

    def test_add_message_invalid(self):
        """Does creating a message fail with invalid params?"""

        m = Message(
            text="HOLLA!",
            user_id=99123
        )

        db.session.add(m)

        with self.assertRaises(IntegrityError):
            db.session.commit()

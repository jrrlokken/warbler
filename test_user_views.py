# User view tests

from unittest import TestCase
from app import app, do_login
from models import db, connect_db, User, Message, Follows

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///warbler-test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True

db.drop_all()
db.create_all()


class UserViewsTestCase(TestCase):
    """Tests for user views."""

    def setUp(self):
        """Setup data for tests."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.user_id = u.id

    def tearDown(self):
        """Clean up."""

        db.session.rollback()

    def test_user_list_view(self):
        """Test the main users view."""

        user = User.query.get(self.user_id)

        with app.test_client() as client:
            res = client.get("/users")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(f"@{user.username}", html)

    def test_user_detail_view(self):
        """Test user detail view."""

        user = User.query.get(self.user_id)

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["curr_user"] = user.id

            res = client.get(f"/users/{self.user_id}")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(f"@{user.username}", html)

from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTests(TestCase):
    def test_user_creation(self):
        # Create a new user
        user = User.objects.create_user(email="test@example.com", username="testuser", password="securepassword")

        # Check if the user was created correctly
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.check_password("securepassword"))

    def test_user_creation_without_username(self):
        # Create a user without a username
        user = User.objects.create_user(email="test2@example.com", password="securepassword")

        # Check if the user was created correctly
        self.assertEqual(user.email, "test2@example.com")
        self.assertIsNone(user.username)  # Ensure the username can be None (based on your model)

    def test_user_creation_with_duplicate_email(self):
        # Create a user with a unique email
        User.objects.create_user(email="unique@example.com", username="user1", password="securepassword")

        # Try to create a user with the same email, which should raise an IntegrityError
        with self.assertRaises(Exception):  # IntegrityError, handled by Django's default DB backends
            User.objects.create_user(email="unique@example.com", username="user2", password="anotherpassword")

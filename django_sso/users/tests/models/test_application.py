from unittest.mock import patch

from django.contrib.auth.hashers import check_password
from django.db import IntegrityError

# django
from django.test import TestCase

# local
from django_sso.users.models import Application


class ApplicationModelTest(TestCase):
    def setUp(self):
        self.app_data = {
            "name": "Test App",
            "redirect_uris": "https://example.com/callback\nhttps://example.org/return",
            "allowed_scopes": "openid email profile custom-scope",
        }

    def test_client_id_and_secret_auto_generated(self):
        app = Application.objects.create(**self.app_data)
        self.assertTrue(app.client_id)
        self.assertTrue(app.client_secret)
        self.assertNotEqual(app.client_secret, getattr(app, "_raw_client_secret", None))

    def test_client_secret_is_hashed(self):
        app = Application.objects.create(**self.app_data)
        raw_secret = app._raw_client_secret  # Saved during `save()`
        self.assertTrue(check_password(raw_secret, app.client_secret))

    def test_get_redirect_uris_parsing(self):
        app = Application.objects.create(**self.app_data)
        expected_uris = ["https://example.com/callback", "https://example.org/return"]
        self.assertEqual(app.get_redirect_uris(), expected_uris)

    def test_get_allowed_scopes_parsing(self):
        app = Application.objects.create(**self.app_data)
        expected_scopes = ["openid", "email", "profile", "custom-scope"]
        self.assertEqual(app.get_allowed_scopes(), expected_scopes)

    def test_str_representation(self):
        app = Application.objects.create(**self.app_data)
        self.assertEqual(str(app), "Test App")

    def test_generate_unique_client_id_is_unique(self):
        _ = Application.objects.create(**self.app_data)
        with patch("django_sso.users.models.Application._generate_unique_client_id") as mock_generator:
            mock_generator.return_value = "unique-id-123"
            app2 = Application(name="App2", redirect_uris="uri")
            app2.save()
            self.assertEqual(app2.client_id, "unique-id-123")


class ApplicationModelNegativeTest(TestCase):
    def setUp(self):
        self.valid_data = {
            "name": "Negative Test App",
            "redirect_uris": "https://example.com/callback",
            "allowed_scopes": "openid email",
        }

    def test_empty_name_fails_validation(self):
        del self.valid_data["name"]
        app = Application(name="", **self.valid_data)
        with self.assertRaises(Exception):
            app.full_clean()

    def test_duplicate_client_id_raises_integrity_error(self):
        app1 = Application.objects.create(**self.valid_data)
        app2 = Application(name="Another", redirect_uris="https://test.com", allowed_scopes="openid")

        app2.client_id = app1.client_id
        app2.client_secret = "manuallysetsecret"
        with self.assertRaises(IntegrityError):
            app2.save()

    def test_duplicate_client_secret_raises_integrity_error(self):
        app1 = Application.objects.create(**self.valid_data)
        app2 = Application(name="Another", redirect_uris="https://test.com", allowed_scopes="openid")

        app2.client_secret = app1.client_secret
        app2.client_id = "some-unique-id"
        with self.assertRaises(IntegrityError):
            app2.save()

    def test_get_redirect_uris_with_blank_value_returns_empty_list(self):
        app = Application.objects.create(name="Blank Redirects", redirect_uris="", allowed_scopes="openid")
        self.assertEqual(app.get_redirect_uris(), [])

    def test_get_allowed_scopes_with_blank_value_returns_empty_list(self):
        app = Application.objects.create(name="Blank Scopes", redirect_uris="https://x.com", allowed_scopes="")
        self.assertEqual(app.get_allowed_scopes(), [])

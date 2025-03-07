""" test for app action functionality """
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.template.response import TemplateResponse
from django.test import TestCase
from django.test.client import RequestFactory

from bookwyrm import models, views


class PasswordViews(TestCase):
    """view user and edit profile"""

    def setUp(self):
        """we need basic test data and mocks"""
        self.factory = RequestFactory()
        with patch("bookwyrm.suggested_users.rerank_suggestions_task.delay"), patch(
            "bookwyrm.activitystreams.populate_stream_task.delay"
        ):
            self.local_user = models.User.objects.create_user(
                "mouse@local.com",
                "mouse@mouse.com",
                "password",
                local=True,
                localname="mouse",
            )
        self.anonymous_user = AnonymousUser
        self.anonymous_user.is_authenticated = False
        models.SiteSettings.objects.create(id=1)

    def test_password_reset_request(self):
        """there are so many views, this just makes sure it LOADS"""
        view = views.PasswordResetRequest.as_view()
        request = self.factory.get("")
        request.user = self.local_user

        result = view(request)
        self.assertIsInstance(result, TemplateResponse)
        result.render()
        self.assertEqual(result.status_code, 200)

    def test_password_reset_request_post(self):
        """send 'em an email"""
        request = self.factory.post("", {"email": "aa@bb.ccc"})
        request.user = self.anonymous_user
        view = views.PasswordResetRequest.as_view()
        resp = view(request)
        self.assertEqual(resp.status_code, 200)
        resp.render()

        request = self.factory.post("", {"email": "mouse@mouse.com"})
        request.user = self.anonymous_user
        with patch("bookwyrm.emailing.send_email.delay"):
            resp = view(request)
        resp.render()

        self.assertEqual(models.PasswordReset.objects.get().user, self.local_user)

    def test_password_reset(self):
        """there are so many views, this just makes sure it LOADS"""
        view = views.PasswordReset.as_view()
        code = models.PasswordReset.objects.create(user=self.local_user)
        request = self.factory.get("")
        request.user = self.anonymous_user
        result = view(request, code.code)
        self.assertIsInstance(result, TemplateResponse)
        result.render()
        self.assertEqual(result.status_code, 200)

    def test_password_reset_post(self):
        """reset from code"""
        view = views.PasswordReset.as_view()
        code = models.PasswordReset.objects.create(user=self.local_user)
        request = self.factory.post("", {"password": "hi", "confirm-password": "hi"})
        with patch("bookwyrm.views.password.login"):
            resp = view(request, code.code)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(models.PasswordReset.objects.exists())

    def test_password_reset_wrong_code(self):
        """reset from code"""
        view = views.PasswordReset.as_view()
        models.PasswordReset.objects.create(user=self.local_user)
        request = self.factory.post("", {"password": "hi", "confirm-password": "hi"})
        resp = view(request, "jhgdkfjgdf")
        resp.render()
        self.assertTrue(models.PasswordReset.objects.exists())

    def test_password_reset_mismatch(self):
        """reset from code"""
        view = views.PasswordReset.as_view()
        code = models.PasswordReset.objects.create(user=self.local_user)
        request = self.factory.post("", {"password": "hi", "confirm-password": "hihi"})
        resp = view(request, code.code)
        resp.render()
        self.assertTrue(models.PasswordReset.objects.exists())

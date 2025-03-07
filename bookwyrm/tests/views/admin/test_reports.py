""" test for app action functionality """
import json
from unittest.mock import patch

from django.template.response import TemplateResponse
from django.test import TestCase
from django.test.client import RequestFactory

from bookwyrm import forms, models, views
from bookwyrm.tests.validate_html import validate_html


class ReportViews(TestCase):
    """every response to a get request, html or json"""

    def setUp(self):
        """we need basic test data and mocks"""
        self.factory = RequestFactory()
        with patch("bookwyrm.suggested_users.rerank_suggestions_task.delay"), patch(
            "bookwyrm.activitystreams.populate_stream_task.delay"
        ):
            self.local_user = models.User.objects.create_user(
                "mouse@local.com",
                "mouse@mouse.mouse",
                "password",
                local=True,
                localname="mouse",
            )
            self.rat = models.User.objects.create_user(
                "rat@local.com",
                "rat@mouse.mouse",
                "password",
                local=True,
                localname="rat",
            )
        models.SiteSettings.objects.create()

    def test_reports_page(self):
        """there are so many views, this just makes sure it LOADS"""
        view = views.Reports.as_view()
        request = self.factory.get("")
        request.user = self.local_user
        request.user.is_superuser = True

        result = view(request)
        self.assertIsInstance(result, TemplateResponse)
        validate_html(result.render())
        self.assertEqual(result.status_code, 200)

    def test_reports_page_with_data(self):
        """there are so many views, this just makes sure it LOADS"""
        view = views.Reports.as_view()
        request = self.factory.get("")
        request.user = self.local_user
        request.user.is_superuser = True
        models.Report.objects.create(reporter=self.local_user, user=self.rat)

        result = view(request)
        self.assertIsInstance(result, TemplateResponse)
        validate_html(result.render())
        self.assertEqual(result.status_code, 200)

    def test_report_page(self):
        """there are so many views, this just makes sure it LOADS"""
        view = views.Report.as_view()
        request = self.factory.get("")
        request.user = self.local_user
        request.user.is_superuser = True
        report = models.Report.objects.create(reporter=self.local_user, user=self.rat)

        result = view(request, report.id)

        self.assertIsInstance(result, TemplateResponse)
        validate_html(result.render())
        self.assertEqual(result.status_code, 200)

    def test_report_comment(self):
        """comment on a report"""
        view = views.Report.as_view()
        request = self.factory.post("", {"note": "hi"})
        request.user = self.local_user
        request.user.is_superuser = True
        report = models.Report.objects.create(reporter=self.local_user, user=self.rat)

        view(request, report.id)

        comment = models.ReportComment.objects.get()
        self.assertEqual(comment.user, self.local_user)
        self.assertEqual(comment.note, "hi")
        self.assertEqual(comment.report, report)

    def test_make_report(self):
        """a user reports another user"""
        form = forms.ReportForm()
        form.data["reporter"] = self.local_user.id
        form.data["user"] = self.rat.id
        request = self.factory.post("", form.data)
        request.user = self.local_user

        views.make_report(request)

        report = models.Report.objects.get()
        self.assertEqual(report.reporter, self.local_user)
        self.assertEqual(report.user, self.rat)

    def test_resolve_report(self):
        """toggle report resolution status"""
        report = models.Report.objects.create(reporter=self.local_user, user=self.rat)
        self.assertFalse(report.resolved)
        request = self.factory.post("")
        request.user = self.local_user
        request.user.is_superuser = True

        # resolve
        views.resolve_report(request, report.id)
        report.refresh_from_db()
        self.assertTrue(report.resolved)

        # un-resolve
        views.resolve_report(request, report.id)
        report.refresh_from_db()
        self.assertFalse(report.resolved)

    @patch("bookwyrm.suggested_users.rerank_suggestions_task.delay")
    @patch("bookwyrm.activitystreams.populate_stream_task.delay")
    @patch("bookwyrm.suggested_users.remove_user_task.delay")
    def test_suspend_user(self, *_):
        """toggle whether a user is able to log in"""
        self.assertTrue(self.rat.is_active)
        request = self.factory.post("")
        request.user = self.local_user
        request.user.is_superuser = True

        # de-activate
        views.suspend_user(request, self.rat.id)
        self.rat.refresh_from_db()
        self.assertFalse(self.rat.is_active)

        # re-activate
        views.unsuspend_user(request, self.rat.id)
        self.rat.refresh_from_db()
        self.assertTrue(self.rat.is_active)

    @patch("bookwyrm.suggested_users.rerank_suggestions_task.delay")
    @patch("bookwyrm.suggested_users.remove_user_task.delay")
    def test_delete_user(self, *_):
        """toggle whether a user is able to log in"""
        self.assertTrue(self.rat.is_active)
        request = self.factory.post("", {"password": "password"})
        request.user = self.local_user
        request.user.is_superuser = True

        # de-activate
        with patch("bookwyrm.models.activitypub_mixin.broadcast_task.delay") as mock:
            views.moderator_delete_user(request, self.rat.id)
        self.assertEqual(mock.call_count, 1)
        activity = json.loads(mock.call_args[0][1])
        self.assertEqual(activity["type"], "Delete")

        self.rat.refresh_from_db()
        self.assertFalse(self.rat.is_active)
        self.assertEqual(self.rat.deactivation_reason, "moderator_deletion")

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from store.models import Organization, OrgMembership, ROLE_ADMIN
from django.urls import reverse

User = get_user_model()

class TenantMiddlewareTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.org = Organization.objects.create(name="Elysian", slug="elysian")
        self.user = User.objects.create_user(username="u1", password="pass12345")
        OrgMembership.objects.create(org=self.org, user=self.user, role=ROLE_ADMIN)

    def test_tenant_via_query(self):
        self.client.login(username="u1", password="pass12345")
        resp = self.client.get(reverse("store:dashboard") + "?tenant=elysian")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Elysian")

    def test_tenant_missing_redirects_to_org_switch(self):
        self.client.login(username="u1", password="pass12345")
        resp = self.client.get(reverse("store:dashboard"))
        self.assertEqual(resp.status_code, 302)

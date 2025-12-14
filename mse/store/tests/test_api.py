from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from store.models import Organization, OrgMembership, ROLE_ADMIN, Plan

User = get_user_model()

class ApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.org = Organization.objects.create(name="Elysian", slug="elysian")
        self.user = User.objects.create_user(username="u1", password="pass12345")
        OrgMembership.objects.create(org=self.org, user=self.user, role=ROLE_ADMIN)
        Plan.objects.create(code="basic", name="Basic", monthly_price_usd=19, stripe_price_id="price_x")

    def test_plans_public(self):
        resp = self.client.get("/store/api/plans/")
        self.assertEqual(resp.status_code, 200)

    def test_tenant_me_requires_auth_and_tenant(self):
        self.client.login(username="u1", password="pass12345")
        resp = self.client.get("/store/api/tenant/", **{"HTTP_X_TENANT":"elysian"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("org", resp.json())

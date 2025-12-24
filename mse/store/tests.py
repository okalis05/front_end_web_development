from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Organization, Membership, Product


# Create your tests here.
User = get_user_model()

class TenantIsolationTests(TestCase):
    def setUp(self):
        self.u = User.objects.create_user(username="u1", password="pass12345")
        self.org1 = Organization.objects.create(name="Org One", slug="org-one")
        self.org2 = Organization.objects.create(name="Org Two", slug="org-two")
        Membership.objects.create(user=self.u, org=self.org1, role=Membership.OWNER)

        Product.objects.create(org=self.org1, name="P1", slug="p1", price="10.00", accent="purple")
        Product.objects.create(org=self.org2, name="P2", slug="p2", price="20.00", accent="gold")

    def test_user_cannot_access_unowned_tenant(self):
        self.client.login(username="u1", password="pass12345")

        # try to set tenant to org2 (should not resolve)
        resp = self.client.get(reverse("store:catalog") + "?org=org-two", follow=True)
        # should redirect to org_switch because tenant selection rejected
        self.assertContains(resp, "Select an organization", status_code=200)

    def test_user_can_access_owned_tenant(self):
        self.client.login(username="u1", password="pass12345")
        resp = self.client.get(reverse("store:catalog") + "?org=org-one")
        self.assertContains(resp, "Catalog", status_code=200)
        self.assertContains(resp, "P1")
        self.assertNotContains(resp, "P2")

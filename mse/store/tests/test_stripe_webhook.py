from django.test import TestCase
from django.conf import settings

class StripeWebhookConfigTest(TestCase):
    def test_webhook_secret_exists_in_settings_for_prod(self):
        # This is a “guardrail” test. In dev you can skip enforcing it.
        # Keep it simple: just ensure attribute exists.
        self.assertTrue(hasattr(settings, "STRIPE_WEBHOOK_SECRET"))

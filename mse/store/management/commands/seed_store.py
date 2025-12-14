from django.core.management.base import BaseCommand
from store.models import Plan, PLAN_BASIC, PLAN_STANDARD, PLAN_PREMIUM

class Command(BaseCommand):
    help = "Seed default SaaS plans for store app"

    def handle(self, *args, **kwargs):
        defaults = [
            (PLAN_BASIC, "Basic", "Elegant essentials for solo founders.", 19, 1, True, False),
            (PLAN_STANDARD, "Standard", "A refined tier for growing teams.", 49, 5, True, True),
            (PLAN_PREMIUM, "Premium", "The full Elysian experience.", 99, 20, True, True),
        ]
        for code, name, desc, price, seats, api, sup in defaults:
            Plan.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": desc,
                    "monthly_price_usd": price,
                    "seats_included": seats,
                    "api_access": api,
                    "priority_support": sup,
                    "is_active": True,
                },
            )
        self.stdout.write(self.style.SUCCESS("Seeded plans. Add Stripe price IDs in admin."))

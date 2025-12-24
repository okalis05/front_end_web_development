from django.core.management.base import BaseCommand
from decimal import Decimal
from django.utils.text import slugify

from store.models import Plan, Organization, Product

class Command(BaseCommand):
    help = "Seed plans and demo products."

    def handle(self, *args, **options):
        plans = [
            ("Luxe Violet", "luxe-violet", Decimal("49.00"), Decimal("499.00"), 1),
            ("Imperial Gold", "imperial-gold", Decimal("149.00"), Decimal("1499.00"), 2),
            ("Crimson Reserve", "crimson-reserve", Decimal("399.00"), Decimal("3999.00"), 3),
        ]
        for name, code, m, a, tier in plans:
            Plan.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "monthly_price": m,
                    "annual_price": a,
                    "tier": tier,
                    "is_public": True,
                    "is_active": True,
                    "description": f"{name}: executive-grade fintech storefront capabilities.",
                },
            )

        # demo org (optional)
        org, _ = Organization.objects.get_or_create(name="Elysian Fintech Atelier", slug="elysian-fintech")
        Product.objects.get_or_create(
            org=org,
            slug="violet-quant-bundle",
            defaults={
                "name": "Violet Quant Bundle",
                "description": "Luxury analytics add-on pack with executive dashboards.",
                "price": Decimal("199.00"),
                "currency": "USD",
                "accent": "purple",
                "image_url": "https://images.pexels.com/photos/669365/pexels-photo-669365.jpeg",
                "is_active": True,
            },
        )
        Product.objects.get_or_create(
            org=org,
            slug="imperial-risk-suite",
            defaults={
                "name": "Imperial Risk Suite",
                "description": "Fintech risk & audit suite with premium reporting.",
                "price": Decimal("499.00"),
                "currency": "USD",
                "accent": "gold",
                "image_url": "https://images.pexels.com/photos/1441977/pexels-photo-1441977.jpeg",
                "is_active": True,
            },
        )
        Product.objects.get_or_create(
            org=org,
            slug="crimson-ledger-pro",
            defaults={
                "name": "Crimson Ledger Pro",
                "description": "Executive ledger & compliance console with immaculate UX.",
                "price": Decimal("799.00"),
                "currency": "USD",
                "accent": "red",
                "image_url": "https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg",
                "is_active": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("Seeded plans + demo org/products."))
        self.stdout.write("Tip: Create Memberships for your user in admin for 'elysian-fintech'.")

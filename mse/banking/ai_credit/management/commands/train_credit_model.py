from django.core.management.base import BaseCommand
from banking.ai_credit.services import train_credit_model

class Command(BaseCommand):
    help = "Train AI Credit model from LendingClub CSV"

    def add_arguments(self, parser):
        parser.add_argument("--csv", required=True)
        parser.add_argument("--version", default="v1")

    def handle(self, *args, **opts):
        artifact = train_credit_model(csv_path=opts["csv"], version=opts["version"])
        self.stdout.write(self.style.SUCCESS(f"Trained {artifact.version} metrics={artifact.metrics}"))

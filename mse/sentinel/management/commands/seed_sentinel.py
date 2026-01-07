from django.core.management.base import BaseCommand
from django.utils import timezone
import random

from sentinel.models import Metric, Event
from sentinel.industry.registry import list_industries, get_industry_config

class Command(BaseCommand):
    help = "Seed Sentinel with baseline metric history for all industries."

    def handle(self, *args, **options):
        if Metric.objects.exists():
            self.stdout.write(self.style.WARNING("Sentinel already seeded (metrics exist). Skipping."))
            return

        for ind in list_industries():
            cfg = get_industry_config(ind["key"])
            for kpi in cfg["kpis"]:
                base = float(kpi["baseline"])
                for _ in range(20):
                    jitter = random.uniform(-0.03, 0.03) * base
                    Metric.objects.create(
                        industry_key=cfg["key"],
                        kpi_key=kpi["key"],
                        value=max(0.0, base + jitter),
                        ts=timezone.now()
                    )

            Event.objects.create(
                industry_key=cfg["key"],
                event_type="info",
                severity=1,
                title=f"{cfg['label']} world initialized",
                body=f"Sentinel is now monitoring {len(cfg['kpis'])} KPIs for {cfg['label']}.",
                kpi_key="",
                value=0.0,
                ts=timezone.now()
            )

        self.stdout.write(self.style.SUCCESS("Seeded Sentinel baselines + initialization events."))

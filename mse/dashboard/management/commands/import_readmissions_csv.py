import csv
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from dashboard.models import Facility, ReadmissionObservation


def parse_date(value: str):
    if not value:
        return None
    # CMS often uses YYYY-MM-DD
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None


def parse_float(value: str):
    if value is None:
        return None
    v = str(value).strip()
    if v in ("", "Not Available", "Not Applicable"):
        return None
    try:
        return float(v)
    except ValueError:
        return None


def parse_int(value: str):
    if value is None:
        return None
    v = str(value).strip()
    if v in ("", "Not Available", "Not Applicable"):
        return None
    try:
        return int(float(v))
    except ValueError:
        return None


class Command(BaseCommand):
    help = "Import CMS Hospital Readmissions CSV (fields used as-is)."

    def add_arguments(self, parser):
        parser.add_argument("--path", required=True, help="Path to the downloaded CMS CSV file")
        parser.add_argument("--limit", type=int, default=0, help="Optional limit for rows (0 = all)")

    def handle(self, *args, **options):
        path = options["path"]
        limit = options["limit"]

        try:
            f = open(path, "r", encoding="utf-8-sig", newline="")
        except OSError as e:
            raise CommandError(f"Unable to open file: {e}")

        created_facilities = 0
        created_obs = 0

        with f:
            reader = csv.DictReader(f)

            required = {
                "End Date",
                "Excess Readmission Ratio",
                "Expected Readmission Rate",
                "Facility Name",
                "Facility ID",
                "Measure Name",
                "Number of Discharges",
                "Number of Readmissions",
                "Predicted Readmission Rate",
                "Start Date",
                "State",
            }

            missing = required - set(reader.fieldnames or [])
            if missing:
                raise CommandError(f"CSV missing required columns: {sorted(missing)}")

            for i, row in enumerate(reader, start=1):
                if limit and i > limit:
                    break

                facility_id = (row.get("Facility ID") or "").strip()
                facility_name = (row.get("Facility Name") or "").strip()
                state = (row.get("State") or "").strip()

                if not facility_id or not facility_name or not state:
                    continue

                facility, created = Facility.objects.get_or_create(
                    facility_id=facility_id,
                    defaults={"name": facility_name, "state": state},
                )
                if created:
                    created_facilities += 1
                else:
                    # keep facility name/state fresh
                    if facility.name != facility_name or facility.state != state:
                        facility.name = facility_name
                        facility.state = state
                        facility.save(update_fields=["name", "state"])

                obs = ReadmissionObservation.objects.create(
                    facility=facility,
                    measure_name=(row.get("Measure Name") or "").strip(),
                    start_date=parse_date(row.get("Start Date") or ""),
                    end_date=parse_date(row.get("End Date") or ""),
                    excess_readmission_ratio=parse_float(row.get("Excess Readmission Ratio") or ""),
                    expected_readmission_rate=parse_float(row.get("Expected Readmission Rate") or ""),
                    predicted_readmission_rate=parse_float(row.get("Predicted Readmission Rate") or ""),
                    number_of_discharges=parse_int(row.get("Number of Discharges") or ""),
                    number_of_readmissions=parse_int(row.get("Number of Readmissions") or ""),
                )
                created_obs += 1

        self.stdout.write(self.style.SUCCESS(
            f"Import complete. Facilities created: {created_facilities}. Observations created: {created_obs}."
        ))

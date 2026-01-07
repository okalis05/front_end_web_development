from django.db import models

# Create your models here.
class Facility(models.Model):
    facility_id = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    state = models.CharField(max_length=2, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["state", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.state})"


class ReadmissionObservation(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="observations")
    measure_name = models.CharField(max_length=255, db_index=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    excess_readmission_ratio = models.FloatField(null=True, blank=True)
    expected_readmission_rate = models.FloatField(null=True, blank=True)
    predicted_readmission_rate = models.FloatField(null=True, blank=True)

    number_of_discharges = models.IntegerField(null=True, blank=True)
    number_of_readmissions = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["measure_name"]),
            models.Index(fields=["start_date", "end_date"]),
            models.Index(fields=["facility"]),
        ]
        ordering = ["-end_date", "facility__state", "facility__name"]


    @property
    def state_sort(self):
        return self.facility.state

    def __str__(self) -> str:
        return f"{self.facility} - {self.measure_name}"

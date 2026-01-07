from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Metric",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("industry_key", models.CharField(db_index=True, max_length=32)),
                ("kpi_key", models.CharField(db_index=True, max_length=64)),
                ("value", models.FloatField()),
                ("ts", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("industry_key", models.CharField(db_index=True, max_length=32)),
                ("event_type", models.CharField(db_index=True, max_length=64)),
                ("severity", models.PositiveSmallIntegerField(default=1)),
                ("title", models.CharField(max_length=160)),
                ("body", models.TextField()),
                ("kpi_key", models.CharField(blank=True, default="", max_length=64)),
                ("value", models.FloatField(blank=True, default=0.0)),
                ("ts", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
        ),
        migrations.AddIndex(
            model_name="metric",
            index=models.Index(fields=["industry_key", "kpi_key", "-ts"], name="sentinel_m_ind_kpi_ts"),
        ),
        migrations.AddIndex(
            model_name="event",
            index=models.Index(fields=["industry_key", "-ts"], name="sentinel_e_ind_ts"),
        ),
        migrations.AddIndex(
            model_name="event",
            index=models.Index(fields=["event_type", "-ts"], name="sentinel_e_type_ts"),
        ),
    ]

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("jobs", "0004_contactinquiry"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SavedJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("saved_at", models.DateTimeField(auto_now_add=True)),
                ("job", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="saved_by", to="jobs.job")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="saved_jobs", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-saved_at",)},
        ),
        migrations.AddConstraint(
            model_name="savedjob",
            constraint=models.UniqueConstraint(fields=("user", "job"), name="unique_saved_job_per_user"),
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160)),
                ("message", models.TextField(max_length=2000)),
                ("target_url", models.CharField(blank=True, max_length=500)),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="portal_notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="Interview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("scheduled_at", models.DateTimeField()),
                ("location_or_link", models.CharField(blank=True, max_length=500)),
                ("notes", models.TextField(blank=True, max_length=3000)),
                ("status", models.CharField(choices=[("scheduled", "Scheduled"), ("completed", "Completed"), ("cancelled", "Cancelled")], default="scheduled", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("application", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="interviews", to="jobs.application")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_interviews", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("scheduled_at",)},
        ),
    ]

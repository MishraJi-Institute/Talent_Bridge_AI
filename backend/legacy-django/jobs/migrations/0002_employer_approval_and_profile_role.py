from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ("jobs", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AddField(
            model_name="company",
            name="owner",
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="owned_company", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="company",
            name="is_approved",
            field=models.BooleanField(default=False, help_text="Only approved employers may publish jobs."),
        ),
        migrations.AddField(
            model_name="profile",
            name="role",
            field=models.CharField(choices=[("job_seeker", "Job Seeker"), ("employer", "Employer")], default="job_seeker", max_length=20),
        ),
        migrations.AddField(
            model_name="profile",
            name="phone",
            field=models.CharField(blank=True, max_length=30),
        ),
    ]

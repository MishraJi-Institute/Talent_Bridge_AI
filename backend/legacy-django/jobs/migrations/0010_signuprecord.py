# Generated for TalentBridgeAI signup uniqueness and admin audit trail.
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jobs", "0009_resumedraft"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SignupRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("signup_method", models.CharField(choices=[("email_password", "Email and password"), ("google", "Google")], max_length=20)),
                ("role", models.CharField(blank=True, max_length=20)),
                ("email_verified", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="signup_record", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",), "verbose_name": "Signup record", "verbose_name_plural": "Signup records"},
        ),
    ]

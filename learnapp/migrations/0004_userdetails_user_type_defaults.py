from django.db import migrations, models


def normalize_user_types(apps, schema_editor):
    UserDetails = apps.get_model("learnapp", "UserDetails")
    UserDetails.objects.filter(user_type="user").update(user_type="USER")
    UserDetails.objects.filter(user_type="vender").update(user_type="VENDER")


def restore_legacy_user_types(apps, schema_editor):
    UserDetails = apps.get_model("learnapp", "UserDetails")
    UserDetails.objects.filter(user_type="USER").update(user_type="user")
    UserDetails.objects.filter(user_type="VENDER").update(user_type="vender")


class Migration(migrations.Migration):
    dependencies = [
        ("learnapp", "0003_userdetails_user_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userdetails",
            name="user_type",
            field=models.CharField(
                choices=[("USER", "User"), ("VENDER", "Vendor")],
                default="USER",
                max_length=10,
            ),
        ),
        migrations.RunPython(normalize_user_types, restore_legacy_user_types),
    ]

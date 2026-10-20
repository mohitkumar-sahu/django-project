from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("foods", "0010_vendor_products_and_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="foodcustomizationoption",
            name="option_type",
            field=models.CharField(
                choices=[
                    ("SAUCE", "Sauce"),
                    ("TOPPING", "Topping"),
                    ("FLAVOR", "Flavor / variant"),
                ],
                max_length=10,
            ),
        ),
    ]

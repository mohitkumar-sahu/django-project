from django.db import migrations, models


def categorize_legacy_pasta(apps, schema_editor):
    FoodItems = apps.get_model("foods", "FoodItems")
    FoodItems.objects.filter(name__iexact="Pasta", categories="1").update(
        categories="PASTA"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("foods", "0008_orderdetails_delete_order_details"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fooditems",
            name="categories",
            field=models.CharField(
                choices=[
                    ("PIZZA", "Pizza"),
                    ("BURGER", "Burger"),
                    ("PASTA", "Pasta"),
                    ("FRENCH FRIES", "French Fries"),
                    ("DESSERT", "Dessert"),
                    ("BREVERAGES", "Beverages"),
                ],
                max_length=100,
            ),
        ),
        migrations.RunPython(categorize_legacy_pasta, migrations.RunPython.noop),
    ]

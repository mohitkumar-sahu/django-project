from django.db import models
catogeories=[
    ('PIZZA','Pizza'),
    ('BURGER','Burger'),
    ('FRENCH FRIES','French Fries'),
    ('DESSERT','Dessart'),
    ('BREVERAGES','Braverages')
]

# Create your models here.
class FoodItems(models.Model):
    name=models.CharField( max_length=100)
    price=models.FloatField()
    rating=models.FloatField()
    food_img=models.ImageField(upload_to='foodimg/',blank=True,null=True)
    description=models.TextField()
    categories=models.CharField(max_length=100,choices=catogeories)
    
    def __str__(self):
        return self.name

class SizeChart(models.Model):
    size_type=models.CharField(max_length=50)
    size_in_cm=models.CharField(max_length=50)
    price=models.IntegerField()

class Basetype(models.Model):
    basename=models.CharField(max_length=50)
    base_img=models.ImageField()

class Toppings(models.Model):
    name=models.CharField(max_length=50)
    qty=models.IntegerField()
    price=models.IntegerField()
    topping_img=models.ImageField()

class sau(models.Model):
    sname=models.CharField(max_length=50)
    simage=models.ImageField(upload_to=None)
    price=models.IntegerField()

class customized_options(models.Model):
    food_type = models.CharField(max_length=100,choices=catogeories)
    size_type = models.ForeignKey(SizeChart,related_name="sizecharts",on_delete=models.CASCADE)
    base_type = models.ForeignKey(Basetype,related_name="basetypes",on_delete=models.CASCADE)
    toppings_type = models.ForeignKey(Toppings,related_name="toppings",on_delete=models.CASCADE)
    sau_type = models.ForeignKey(sau,related_name="saus",on_delete=models.CASCADE)

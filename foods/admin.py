from django.contrib import admin
from foods.models import FoodItems,SizeChart,Basetype,Toppings,sauces,customized_options,OrderDetails

# Register your models here.

admin.site.register(FoodItems)
admin.site.register(SizeChart)
admin.site.register(Basetype)
admin.site.register(Toppings)
admin.site.register(sauces)
admin.site.register(customized_options)
admin.site.register(OrderDetails)
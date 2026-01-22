from django.contrib import admin
from foods.models import FoodItems,SizeChart,Basetype,Toppings,sau,customized_options

# Register your models here.

admin.site.register(FoodItems)
admin.site.register(SizeChart)
admin.site.register(Basetype)
admin.site.register(Toppings)
admin.site.register(sau)
admin.site.register(customized_options)
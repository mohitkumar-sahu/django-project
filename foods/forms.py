from django import forms
from foods.models import FoodItems
class AddFoodForm(forms.ModelForm):
    class Meta:
        model= FoodItems
        fields='__all__'
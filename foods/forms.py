from django import forms
from foods.models import FoodItems
class AddFoodForm(forms.ModelForm):
    class Meta:
        model= FoodItems
        fields='__all__'


class CustomizeFoodForm(forms.Form):
    sauce = forms.ChoiceField(label="Sauce", required=False, choices=())
    toppings = forms.MultipleChoiceField(
        label="Toppings",
        required=False,
        choices=(),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, sauce_choices=(), topping_choices=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sauce"].choices = sauce_choices
        self.fields["toppings"].choices = topping_choices

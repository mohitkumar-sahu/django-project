from django import forms
from foods.models import FoodItems, FoodCustomizationOption
class AddFoodForm(forms.ModelForm):
    class Meta:
        model= FoodItems
        fields=['name', 'price', 'rating', 'food_img', 'description', 'categories']


class FoodCustomizationOptionForm(forms.ModelForm):
    class Meta:
        model = FoodCustomizationOption
        fields = ['option_type', 'name', 'price']
        widgets = {
            'price': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
        }

    def __init__(self, *args, option_type_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        if option_type_choices is not None:
            self.fields['option_type'].choices = option_type_choices


class CustomizeFoodForm(forms.Form):
    sauce = forms.ChoiceField(label="Sauce", required=False, choices=())
    toppings = forms.MultipleChoiceField(
        label="Toppings",
        required=False,
        choices=(),
        widget=forms.CheckboxSelectMultiple,
    )
    variant = forms.ChoiceField(label="Flavor / variant", required=False, choices=())

    def __init__(
        self,
        *args,
        sauce_choices=(),
        topping_choices=(),
        variant_choices=(),
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.fields["sauce"].choices = sauce_choices
        self.fields["toppings"].choices = topping_choices
        self.fields["variant"].choices = variant_choices
        self.fields["variant"].required = len(variant_choices) > 1

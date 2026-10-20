from functools import wraps
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from foods.forms import AddFoodForm, CustomizeFoodForm, FoodCustomizationOptionForm
from foods.models import (
    FoodCustomizationOption,
    FoodItems,
    OrderDetails,
    Toppings,
    sau,
)
from learnapp.models import UserDetails


def vendor_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        is_vendor = UserDetails.objects.filter(
            user=request.user,
            user_type='VENDER',
        ).exists()
        if not is_vendor:
            return HttpResponseForbidden('Vendor access only.')
        return view_func(request, *args, **kwargs)

    return never_cache(login_required(wrapped_view, login_url='login'))


def get_vendor_food_or_404(request, food_id):
    return get_object_or_404(FoodItems, pk=food_id, vendor=request.user)


def customization_type_choices_for(food):
    if food.categories.upper() in {'BREVERAGES', 'BEVERAGES', 'BEVERAGE', 'DRINKS'}:
        return [(FoodCustomizationOption.FLAVOR, 'Flavor / variant')]
    return [
        (FoodCustomizationOption.SAUCE, 'Sauce'),
        (FoodCustomizationOption.TOPPING, 'Topping'),
    ]

@never_cache
@login_required(login_url='login')
def Food_details(request, id):
    fooditem = get_object_or_404(FoodItems, id=id)
    return render(request, "foods/foods_details.html", {'fooditem': fooditem})

@never_cache
@login_required(login_url='login')
def allfood(request):
    fooditem = FoodItems.objects.all()
    categories = FoodItems._meta.get_field('categories').choices
    selected_category = request.GET.get('category', '').upper()
    query = request.GET.get('q', '').strip()
    category_labels = dict(categories)

    if selected_category in category_labels:
        fooditem = fooditem.filter(categories=selected_category)
    else:
        selected_category = ''

    if query:
        fooditem = fooditem.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    return render(request, "foods/allfood.html", {
        'fooditem': fooditem,
        'categories': categories,
        'selected_category': selected_category,
        'selected_category_label': category_labels.get(selected_category, ''),
        'query': query,
    })

@never_cache
@login_required(login_url='login')
def customize(request, id):
    fooditem = get_object_or_404(FoodItems, id=id)
    product_options = list(fooditem.customization_options.all())

    sauces_by_value = {}
    toppings_by_value = {}
    variants_by_value = {}
    category = fooditem.categories.upper()
    food_name = fooditem.name.casefold()
    is_beverage = category in {'BREVERAGES', 'BEVERAGES', 'BEVERAGE', 'DRINKS'}
    is_tea = 'tea' in food_name or 'chai' in food_name

    if is_beverage:
        # Beverage items use drink flavors only. This prevents savory toppings
        # such as olives and mushrooms appearing on tea or other drinks.
        tea_flavors = [
            item for item in product_options
            if item.option_type == FoodCustomizationOption.FLAVOR
        ]
        if tea_flavors:
            variants_by_value = {
                f"option:{item.pk}": {'name': item.name, 'price': float(item.price)}
                for item in tea_flavors
            }
        elif is_tea:
            variants_by_value = {
                'preset:masala-tea': {'name': 'Masala Tea', 'price': 0},
                'preset:ginger-tea': {'name': 'Ginger Tea', 'price': 0},
                'preset:elaichi-tea': {'name': 'Elaichi Tea', 'price': 0},
            }
    elif product_options:
        sauces_by_value = {
            f"option:{item.pk}": {'name': item.name, 'price': float(item.price)}
            for item in product_options
            if item.option_type == FoodCustomizationOption.SAUCE
        }
        toppings_by_value = {
            f"option:{item.pk}": {'name': item.name, 'price': float(item.price)}
            for item in product_options
            if item.option_type == FoodCustomizationOption.TOPPING
        }
        variants_by_value = {
            f"option:{item.pk}": {'name': item.name, 'price': float(item.price)}
            for item in product_options
            if item.option_type == FoodCustomizationOption.FLAVOR
        }
    else:
        # Legacy products use category-appropriate defaults. Tea is a single
        # flavor choice; savory foods keep the shared sauce and topping lists.
        if category in {'PIZZA', 'BURGER', 'PASTA', 'FRENCH FRIES'}:
            sauce_items = list(sau.objects.order_by('sname'))
            topping_items = list(Toppings.objects.order_by('name'))
            sauces_by_value = {
                f"sauce:{item.pk}": {'name': item.sname, 'price': item.price}
                for item in sauce_items
            }
            toppings_by_value = {
                f"topping:{item.pk}": {'name': item.name, 'price': item.price}
                for item in topping_items
            }

            if not sauces_by_value:
                sauces_by_value = {
                    'preset:tomato-ketchup': {'name': 'Tomato ketchup', 'price': 10},
                    'preset:mayonnaise': {'name': 'Mayonnaise', 'price': 15},
                    'preset:peri-peri': {'name': 'Peri-peri sauce', 'price': 20},
                }
            if not toppings_by_value:
                toppings_by_value = {
                    'preset:extra-cheese': {'name': 'Extra cheese', 'price': 40},
                    'preset:olives': {'name': 'Olives', 'price': 20},
                    'preset:mushrooms': {'name': 'Mushrooms', 'price': 25},
                    'preset:jalapenos': {'name': 'Jalapeños', 'price': 20},
                }

    sauce_choices = [('', 'No sauce')] + [
        (value, f"{item['name']} (+₹{item['price']})")
        for value, item in sauces_by_value.items()
    ]
    topping_choices = [
        (value, f"{item['name']} (+₹{item['price']})")
        for value, item in toppings_by_value.items()
    ]
    variant_choices = [('', 'Choose a flavor')] + [
        (value, f"{item['name']} (+₹{item['price']})")
        for value, item in variants_by_value.items()
    ]

    customization_prices = {
        **{value: item['price'] for value, item in sauces_by_value.items()},
        **{value: item['price'] for value, item in toppings_by_value.items()},
        **{value: item['price'] for value, item in variants_by_value.items()},
    }

    if request.method == 'POST':
        form = CustomizeFoodForm(
            request.POST,
            sauce_choices=sauce_choices,
            topping_choices=topping_choices,
            variant_choices=variant_choices,
        )
        if form.is_valid():
            sauce = sauces_by_value.get(form.cleaned_data['sauce'])
            toppings = [
                toppings_by_value[value]
                for value in form.cleaned_data['toppings']
            ]
            variant = variants_by_value.get(form.cleaned_data['variant'])
            selected_toppings = [item['name'] for item in toppings]
            price = float(fooditem.price) + sum(
                float(item['price']) for item in toppings
            )
            if sauce:
                price += float(sauce['price'])
            if variant:
                price += float(variant['price'])

            cart = request.session.get('cart', {})
            cart[str(uuid.uuid4())] = {
                'name': fooditem.name,
                'price': price,
                'qty': 1,
                'img': fooditem.food_img.url if fooditem.food_img else '',
                'rating': fooditem.rating,
                'sauce': sauce['name'] if sauce else '',
                'sauce_price': float(sauce['price']) if sauce else 0,
                'variant': variant['name'] if variant else '',
                'variant_price': float(variant['price']) if variant else 0,
                'toppings': selected_toppings,
                'topping_prices': toppings,
            }
            request.session['cart'] = cart
            return redirect('cart')
    else:
        form = CustomizeFoodForm(
            sauce_choices=sauce_choices,
            topping_choices=topping_choices,
            variant_choices=variant_choices,
        )

    return render(request, 'foods/customize.html', {
        'fooditem': fooditem,
        'form': form,
        'customization_prices': customization_prices,
        'has_sauce_options': bool(sauces_by_value),
        'has_topping_options': bool(toppings_by_value),
        'has_variant_options': bool(variants_by_value),
    })

@never_cache
@login_required(login_url='login')
def addtocart(request, id):
    food = FoodItems.objects.get(id=id)
    cart = request.session.get('cart', {})

    if str(id) in cart:
        cart[str(id)]['qty'] += 1
    else:
        cart[str(id)] = {
            'name': food.name,
            'price': food.price,
            'qty': 1,
            'img': food.food_img.url if food.food_img else '',
            'rating': food.rating
        }

    request.session['cart'] = cart
    return redirect('cart')

@vendor_required
def vendor_dashboard(request):
    food_items = FoodItems.objects.filter(vendor=request.user).prefetch_related(
        'customization_options'
    )
    return render(request, 'foods/vendor_products.html', {'food_items': food_items})


@vendor_required
def addnewfood(request):
    if request.method == "POST":
        form = AddFoodForm(request.POST, request.FILES)
        if form.is_valid():
            food = form.save(commit=False)
            food.vendor = request.user
            food.save()
            messages.success(request, f'{food.name} was added to your products.')
            return redirect('vendor_dashboard')
    else:
        form = AddFoodForm()
    return render(request, 'foods/vendor_product_form.html', {
        'form': form,
        'page_title': 'Add a food item',
        'submit_label': 'Add food item',
    })


@vendor_required
def edit_vendor_food(request, food_id):
    food = get_vendor_food_or_404(request, food_id)
    if request.method == 'POST':
        form = AddFoodForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            form.save()
            messages.success(request, f'{food.name} was updated.')
            return redirect('vendor_dashboard')
    else:
        form = AddFoodForm(instance=food)
    return render(request, 'foods/vendor_product_form.html', {
        'form': form,
        'page_title': f'Edit {food.name}',
        'submit_label': 'Save changes',
    })


@vendor_required
@require_POST
def delete_vendor_food(request, food_id):
    food = get_vendor_food_or_404(request, food_id)
    food_name = food.name
    food.delete()
    messages.success(request, f'{food_name} was removed from your products.')
    return redirect('vendor_dashboard')


@vendor_required
def manage_customization_options(request, food_id):
    food = get_vendor_food_or_404(request, food_id)
    option_type_choices = customization_type_choices_for(food)
    if request.method == 'POST':
        form = FoodCustomizationOptionForm(
            request.POST,
            option_type_choices=option_type_choices,
        )
        if form.is_valid():
            option = form.save(commit=False)
            option.food = food
            option.save()
            messages.success(request, f'{option.name} was added as a priced option.')
            return redirect('manage_customization_options', food_id=food.id)
    else:
        form = FoodCustomizationOptionForm(
            option_type_choices=option_type_choices,
        )
    return render(request, 'foods/vendor_customization_options.html', {
        'food': food,
        'form': form,
        'options': food.customization_options.all(),
    })


@vendor_required
def edit_customization_option(request, food_id, option_id):
    food = get_vendor_food_or_404(request, food_id)
    option = get_object_or_404(
        FoodCustomizationOption,
        pk=option_id,
        food=food,
    )
    option_type_choices = customization_type_choices_for(food)
    if option.option_type not in dict(option_type_choices):
        option_type_choices = [
            (option.option_type, option.get_option_type_display()),
            *option_type_choices,
        ]
    if request.method == 'POST':
        form = FoodCustomizationOptionForm(
            request.POST,
            instance=option,
            option_type_choices=option_type_choices,
        )
        if form.is_valid():
            form.save()
            messages.success(request, f'{option.name} was updated.')
            return redirect('manage_customization_options', food_id=food.id)
    else:
        form = FoodCustomizationOptionForm(
            instance=option,
            option_type_choices=option_type_choices,
        )
    return render(request, 'foods/vendor_option_form.html', {
        'food': food,
        'option': option,
        'form': form,
    })


@vendor_required
@require_POST
def delete_customization_option(request, food_id, option_id):
    food = get_vendor_food_or_404(request, food_id)
    option = get_object_or_404(
        FoodCustomizationOption,
        pk=option_id,
        food=food,
    )
    option_name = option.name
    option.delete()
    messages.success(request, f'{option_name} was removed from {food.name}.')
    return redirect('manage_customization_options', food_id=food.id)

@never_cache
@login_required(login_url='login')
def cart(request):
    cart = request.session.get('cart', {})
    total_price = sum(item['price'] * item['qty'] for item in cart.values())
    return render(request, 'foods/addtocart.html', {
        'cart': cart,
        'total_price': total_price
    })

@never_cache
@login_required(login_url='login')
def increase_qty(request, id):
    cart = request.session.get('cart', {})
    cart[id]['qty'] += 1
    request.session['cart'] = cart
    return redirect('cart')

@never_cache
@login_required(login_url='login')
def decrease_qty(request, id):
    cart = request.session.get('cart', {})
    if id in cart:
        if cart[id]['qty'] > 1:
            cart[id]['qty'] -= 1
        else:
            del cart[id]
    request.session['cart'] = cart
    return redirect('cart')

@never_cache
@login_required(login_url='login')
def remove_item(request, id):
    cart = request.session.get('cart', {})
    if id in cart:
        del cart[id]
        request.session['cart'] = cart
    return redirect('cart')

@never_cache
@login_required(login_url='login')
def make_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')

    total_price = 0
    total_qty = 0
    food_summary = []

    for item in cart.values():
        total_price += item['price'] * item['qty']
        total_qty += item['qty']
        description = f"{item['name']} x {item['qty']}"
        if item.get('sauce'):
            description += (
                f" (sauce: {item['sauce']} +₹{item.get('sauce_price', 0)})"
            )
        if item.get('variant'):
            description += (
                f" (variant: {item['variant']} +₹{item.get('variant_price', 0)})"
            )
        if item.get('topping_prices'):
            topping_details = ', '.join(
                f"{topping['name']} +₹{topping['price']}"
                for topping in item['topping_prices']
            )
            description += f" (toppings: {topping_details})"
        elif item.get('toppings'):
            description += f" (toppings: {', '.join(item['toppings'])})"
        food_summary.append(description)

    order = OrderDetails.objects.create(
        user=request.user,
        food_details=", ".join(food_summary),
        total_qty=total_qty,
        total_price=total_price
    )

    # clear cart AFTER saving
    request.session.pop('cart', None)

    return redirect('order_success', order_id=order.id)


@never_cache
@login_required(login_url='login')
def order_success(request, order_id):
    order = get_object_or_404(OrderDetails, id=order_id, user=request.user)

    return render(request, 'foods/order_success.html', {
        'orderid': order.id,
        'order_date': order.created_at if hasattr(order, 'created_at') else timezone.now(),
        'food_details': order.food_details,
        'total_price': order.total_price,
        'total_quantity': order.total_qty,
    })

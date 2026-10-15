from django.shortcuts import render, redirect
from foods.models import FoodItems, OrderDetails, Toppings, sau
from foods.forms import AddFoodForm, CustomizeFoodForm
from django.contrib.auth.decorators import login_required
import uuid

def Food_details(request, id):
    fooditem = FoodItems.objects.get(id=id)
    return render(request, "foods/foods_details.html", {'fooditem': fooditem})

def allfood(request):
    fooditem = FoodItems.objects.all()
    categories = FoodItems._meta.get_field('categories').choices
    selected_category = request.GET.get('category', '').upper()
    category_labels = dict(categories)

    if selected_category in category_labels:
        fooditem = fooditem.filter(categories=selected_category)
    else:
        selected_category = ''

    return render(request, "foods/allfood.html", {
        'fooditem': fooditem,
        'categories': categories,
        'selected_category': selected_category,
        'selected_category_label': category_labels.get(selected_category, ''),
    })

def customize(request, id):
    fooditem = FoodItems.objects.get(id=id)
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

    if sauces_by_value:
        sauce_choices = [('', 'No sauce')] + [
            (value, f"{item['name']} (+₹{item['price']})")
            for value, item in sauces_by_value.items()
        ]
    else:
        sauces_by_value = {
            'preset:tomato-ketchup': {'name': 'Tomato ketchup', 'price': 10},
            'preset:mayonnaise': {'name': 'Mayonnaise', 'price': 15},
            'preset:peri-peri': {'name': 'Peri-peri sauce', 'price': 20},
        }
        sauce_choices = [('', 'No sauce')] + [
            (value, f"{item['name']} (+₹{item['price']})")
            for value, item in sauces_by_value.items()
        ]

    if toppings_by_value:
        topping_choices = [
            (value, f"{item['name']} (+₹{item['price']})")
            for value, item in toppings_by_value.items()
        ]
    else:
        toppings_by_value = {
            'preset:extra-cheese': {'name': 'Extra cheese', 'price': 40},
            'preset:olives': {'name': 'Olives', 'price': 20},
            'preset:mushrooms': {'name': 'Mushrooms', 'price': 25},
            'preset:jalapenos': {'name': 'Jalapeños', 'price': 20},
        }
        topping_choices = [
            (value, f"{item['name']} (+₹{item['price']})")
            for value, item in toppings_by_value.items()
        ]

    customization_prices = {
        **{value: item['price'] for value, item in sauces_by_value.items()},
        **{value: item['price'] for value, item in toppings_by_value.items()},
    }

    if request.method == 'POST':
        form = CustomizeFoodForm(
            request.POST,
            sauce_choices=sauce_choices,
            topping_choices=topping_choices,
        )
        if form.is_valid():
            sauce = sauces_by_value.get(form.cleaned_data['sauce'])
            toppings = [
                toppings_by_value[value]
                for value in form.cleaned_data['toppings']
            ]
            selected_toppings = [item['name'] for item in toppings]
            price = float(fooditem.price) + sum(
                float(item['price']) for item in toppings
            )
            if sauce:
                price += float(sauce['price'])

            cart = request.session.get('cart', {})
            cart[str(uuid.uuid4())] = {
                'name': fooditem.name,
                'price': price,
                'qty': 1,
                'img': fooditem.food_img.url if fooditem.food_img else '',
                'rating': fooditem.rating,
                'sauce': sauce['name'] if sauce else '',
                'sauce_price': sauce['price'] if sauce else 0,
                'toppings': selected_toppings,
                'topping_prices': toppings,
            }
            request.session['cart'] = cart
            return redirect('cart')
    else:
        form = CustomizeFoodForm(
            sauce_choices=sauce_choices,
            topping_choices=topping_choices,
        )

    return render(request, 'foods/customize.html', {
        'fooditem': fooditem,
        'form': form,
        'customization_prices': customization_prices,
    })

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
            'img': food.food_img.url,
            'rating': food.rating
        }

    request.session['cart'] = cart
    return redirect('cart')

def addnewfood(request):
    if request.method == "POST":
        form = AddFoodForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('allfood')
    else:
        form = AddFoodForm()
    return render(request, "foods/addnewfood.html", {'form': form})

def cart(request):
    cart = request.session.get('cart', {})
    total_price = sum(item['price'] * item['qty'] for item in cart.values())
    return render(request, 'foods/addtocart.html', {
        'cart': cart,
        'total_price': total_price
    })

def increase_qty(request, id):
    cart = request.session.get('cart', {})
    cart[id]['qty'] += 1
    request.session['cart'] = cart
    return redirect('cart')

def decrease_qty(request, id):
    cart = request.session.get('cart', {})
    if id in cart:
        if cart[id]['qty'] > 1:
            cart[id]['qty'] -= 1
        else:
            del cart[id]
    request.session['cart'] = cart
    return redirect('cart')

def remove_item(request, id):
    cart = request.session.get('cart', {})
    if id in cart:
        del cart[id]
        request.session['cart'] = cart
    return redirect('cart')

@login_required
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


from django.shortcuts import get_object_or_404
from django.utils import timezone

@login_required
def order_success(request, order_id):
    order = get_object_or_404(OrderDetails, id=order_id, user=request.user)

    return render(request, 'foods/order_success.html', {
        'orderid': order.id,
        'order_date': order.created_at if hasattr(order, 'created_at') else timezone.now(),
        'food_details': order.food_details,
        'total_price': order.total_price,
        'total_quantity': order.total_qty,
    })

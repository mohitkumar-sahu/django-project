from django.shortcuts import render, redirect
from foods.models import FoodItems, OrderDetails
from foods.forms import AddFoodForm
from django.contrib.auth.decorators import login_required
import uuid

def Food_details(request, id):
    fooditem = FoodItems.objects.get(id=id)
    return render(request, "foods/foods_details.html", {'fooditem': fooditem})

def allfood(request):
    fooditem = FoodItems.objects.all()
    return render(request, "foods/allfood.html", {'fooditem': fooditem})

def customize(request, id):
    fooditem = FoodItems.objects.get(id=id)
    return render(request, 'foods/customize.html', {'fooditem': fooditem})

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
        food_summary.append(f"{item['name']} x {item['qty']}")

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
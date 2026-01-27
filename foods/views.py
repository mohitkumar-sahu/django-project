from django.shortcuts import render,redirect
from foods.models import FoodItems
from foods.forms import AddFoodForm

# Create your views here.
def Food_details(request,id):
    # Take the single food item details based on the id
    fooditem=FoodItems.objects.get(id=id)
    return render(request,"foods/foods_details.html",{'fooditem':fooditem})

def allfood(request):
    fooditem=FoodItems.objects.all()
    return render(request,"foods/allfood.html",{'fooditem':fooditem})

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
            'rating':food.rating
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

    total_price = 0
    for item in cart.values():
        total_price += item['price'] * item['qty']

    context = {
        'cart': cart,
        'total_price': total_price
    }
    return render(request, 'foods/addtocart.html', context)

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
            del cart[id]   # remove item if qty becomes 0

    request.session['cart'] = cart
    return redirect('cart')


def remove_item(request, id):
    cart = request.session.get('cart', {})
    del cart[id]
    request.session['cart'] = cart
    return redirect('cart')
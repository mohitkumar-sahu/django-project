from django.shortcuts import render,redirect
from foods.models import FoodItems
from foods.forms import AddFoodForm

# Create your views here.
def Food_details(request,id=0):
    # Take the single food item details based on the id
    fooditem=FoodItems.objects.get(id=id)
    return render(request,"foods/foods_details.html",{'fooditem':fooditem})

def allfood(request):
    fooditem=FoodItems.objects.all()
    return render(request,"foods/allfood.html",{'fooditem':fooditem})

def customize(request):
    return render(request,'foods/customize.html',{})

def addtocart(request):
    return render(request,'foods/addtocart.html',{})

def addnewfood(request):
    if request.method == "POST":
        form = AddFoodForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('allfood')
    else:
        form = AddFoodForm()

    return render(request, "foods/addnewfood.html", {'form': form})

from django.shortcuts import render, redirect
from learnapp.forms import UserForm, UserProfileForm, userUpdateForm, userProfileUpdate
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from foods.models import FoodItems
from foods.forms import AddFoodForm

# Create your views here.
def registration(request):
    registered=False
    if request.method=='POST':
        form1=UserForm(request.POST)
        form2=UserProfileForm(request.POST,request.FILES)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()

            profile=form2.save(commit=False)
            profile.user=user
            profile.save()
            registered=True
    else:
        form1=UserForm()
        form2=UserProfileForm()

    context={'form1':form1,'form2':form2,'registered':registered} 
    return render(request,'registration.html',context)


def user_login(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']

        user=authenticate(username=username,password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect('home')
            else:
                return HttpResponse('User is not active ')
        else:
            return HttpResponse('Please check your creds .. ')
    return render(request,'login.html')


@login_required(login_url='login')
def home(request):
    allfoods=FoodItems.objects.all()
    return render(request,'home.html',{'allfoods':allfoods})

@login_required(login_url='login')
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def profile(request):
    return render(request,'profile.html',{})

@login_required(login_url='login')
def userupdate(request):
    if request.method == 'POST':
        form=userUpdateForm(request.POST,instance=request.user)
        form1=userProfileUpdate(request.POST,request.FILES,instance=request.user.userdetails)
        if form.is_valid() and form1.is_valid():
            user=form.save()
            user.save()
            profile=form1.save(commit=False)
            profile.user=user
            profile.save()
            return redirect('profile')
    else:
        form = userUpdateForm(instance=request.user)
        form1=userProfileUpdate(instance=request.user.userdetails)

    context={
        'form':form,
        'form1':form1,
    }
    return render(request,'update.html',context)

@login_required(login_url='login')
def allfood(request):
    allfood=FoodItems.objects.all()
    return render(request,'allfood.html',{'allfood':allfood})

def addnewfood(request):
    form=AddFoodForm()
    return render(request,"foods/addnewfood.html",{'form':form})


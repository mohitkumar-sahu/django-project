from django.urls import path
from learnapp import views


urlpatterns = [
    path('',views.registration,name='register'),
    path('login',views.user_login,name='login'),
    path('home',views.home,name='home'),
    path('logout',views.user_logout,name='logout'),
    path('profile',views.profile,name='profile'),
    path('update',views.userupdate,name='userupdate')
] 
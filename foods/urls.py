from django.urls import path
from foods import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # food list & add
    path('allfood/', views.allfood, name='allfood'),
    path('addnewfood/', views.addnewfood, name='addnewfood'),

    # cart
    path('addtocart/<int:id>/', views.addtocart, name='addtocart'),
    path('cart/', views.cart, name='cart'),
    path('cart/increase/<str:id>/', views.increase_qty, name='increase_qty'),
    path('cart/decrease/<str:id>/', views.decrease_qty, name='decrease_qty'),
    path('cart/remove/<str:id>/', views.remove_item, name='remove_item'),

    # customize
    path('customize/<int:id>/', views.customize, name='customize'),

    # ⚠️ ALWAYS KEEP THIS LAST
    path('<int:id>/', views.Food_details, name='food_details'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


from django.urls import path
from foods import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('allfood/', views.allfood, name='allfood'),
    path('addnewfood/', views.addnewfood, name='addnewfood'),

    path('addtocart/<int:id>/', views.addtocart, name='addtocart'),
    path('cart/', views.cart, name='cart'),
    path('cart/increase/<str:id>/', views.increase_qty, name='increase_qty'),
    path('cart/decrease/<str:id>/', views.decrease_qty, name='decrease_qty'),
    path('cart/remove/<str:id>/', views.remove_item, name='remove_item'),

    path('customize/<int:id>/', views.customize, name='customize'),

    path('make-order/', views.make_order, name='make_order'),
    path('order_success/<int:order_id>/', views.order_success, name='order_success'),

    path('<int:id>/', views.Food_details, name='food_details'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

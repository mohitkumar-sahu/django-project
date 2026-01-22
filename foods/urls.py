from django.urls import path
from foods import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('<int:id>',views.Food_details),
    path('allfood',views.allfood,name='allfood'),
    path('customize',views.customize,name='customize'),
    path('addtocart',views.addtocart,name='addtocart'),
    path('addnewfood',views.addnewfood,name="addnewfood"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
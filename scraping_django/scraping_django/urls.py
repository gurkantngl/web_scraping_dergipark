from django.contrib import admin
from django.urls import path, include
from main_page import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index, name='index'),
    path('search/', include("articles_page.urls")),
    path('list_db/',include("articles_page.urls"))
]

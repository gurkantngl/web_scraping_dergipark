from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.search, name='search'),
    path('filter',views.filter, name='filter'),
    path('sort',views.sort, name='sort')
]
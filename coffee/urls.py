# C:\Users\anpoi\PycharmProjects\Veb_coffee\coffee\urls.py

from django.urls import path
from . import views # Импортируем views из текущей директории приложения

app_name = 'coffee' # Пространство имен для приложения

urlpatterns = [
    path('', views.home_page, name='home'),
    path('catalog/', views.product_catalog, name='catalog'),
    path('search/', views.search_results, name='search_results'),
]
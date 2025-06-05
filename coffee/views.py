from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from django.http import HttpResponse

def home_page(request):
    return HttpResponse("<h1>Добро пожаловать в кофейню!</h1>")

def product_catalog(request):
    return HttpResponse("<h1>Каталог товаров</h1>")

def search_results(request):
    return HttpResponse("<h1>Результаты поиска</h1>")
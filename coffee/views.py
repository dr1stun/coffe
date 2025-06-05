from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from django.http import HttpResponse

from .models import Product, Category

def home_page(request):
    # Здесь пока просто заглушки, но в будущем будем получать реальные данные
    # Например, 3 самых популярных продукта
    # popular_products = Product.objects.all().order_by('-times_ordered')[:3] # если у Product есть поле times_ordered
    # Или более сложно, если вы будете использовать модель Statistic
    popular_products = Product.objects.all()[:3] # Просто 3 любых продукта для теста
    new_products = Product.objects.all().order_by('-id')[:3] # Просто 3 последних добавленных продукта

    context = {
        'page_title': 'Главная страница кофейни',
        'welcome_message': 'Добро пожаловать в Veb Coffee!',
        'popular_products': popular_products,
        'new_products': new_products,
        # В будущем здесь будут данные для виджетов
    }
    return render(request, 'coffee/home_page.html', context)

def product_catalog(request):
    # Здесь будем выводить полный каталог товаров
    products = Product.objects.all() # Получаем все продукты
    context = {
        'page_title': 'Каталог товаров',
        'products': products,
    }
    return render(request, 'coffee/catalog.html', context)

def search_results(request):
    query = request.GET.get('q') # Получаем поисковый запрос из URL
    results = []
    if query:
        # Ищем продукты по названию или описанию (пока просто заглушка)
        results = Product.objects.filter(name__icontains=query) # __icontains для поиска без учета регистра
        # Можно добавить поиск по другим полям, например, по ингредиентам или категории
        # from django.db.models import Q
        # results = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    context = {
        'page_title': f'Результаты поиска для "{query}"',
        'query': query,
        'results': results,
    }
    return render(request, 'coffee/search_results.html', context)

# Функции для детали, добавления, редактирования, удаления - пока пустые заглушки
def product_detail(request, product_id):
    # Здесь будет логика для отображения одного продукта
    from django.shortcuts import get_object_or_404
    product = get_object_or_404(Product, pk=product_id)
    context = {
        'page_title': product.name,
        'product': product,
    }
    return render(request, 'coffee/product_detail.html', context)

def product_add(request):
    return HttpResponse("<h1>Страница добавления продукта</h1>")

def product_edit(request, product_id):
    return HttpResponse(f"<h1>Страница редактирования продукта {product_id}</h1>")

def product_delete(request, product_id):
    return HttpResponse(f"<h1>Страница удаления продукта {product_id}</h1>")
from django.contrib import admin


# Register your models here.
from django.contrib import admin
from .models import User, Product, Category, Ingredient, Order, OrderItem, Review, Statistic, OrderStatusLog, ProductIngredient, UserPreference, SoldOut, StopList

# Базовая регистрация (для начала)
admin.site.register(Category)
admin.site.register(User)
admin.site.register(Product)
admin.site.register(Ingredient)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Statistic)
admin.site.register(OrderStatusLog)
admin.site.register(ProductIngredient)
admin.site.register(UserPreference)
admin.site.register(SoldOut)
admin.site.register(StopList)


from django.db import models

# Create your models here.
# coffee/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser  # Для расширения стандартной модели User


# Расширение стандартной модели User
class User(AbstractUser):
    ROLE_CHOICES = [
        ('гость', 'Гость'),
        ('бариста', 'Бариста'),
        ('администратор', 'Администратор'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='гость',
        verbose_name='Роль'
    )
    order_count = models.IntegerField(default=0, verbose_name='Количество заказов')
    guest_discount = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0,
        verbose_name='Скидка для гостей (%)'
    )
    # Добавляем связанные менеджеры для групп и разрешений
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="coffee_users",
        related_query_name="coffee_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="coffee_users",
        related_query_name="coffee_user",
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username  # Используем username из AbstractUser


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название напитка/еды')
    category = models.CharField(max_length=50, verbose_name='Категория', null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Цена')
    available = models.BooleanField(default=True, verbose_name='Доступен в меню')
    # Новые поля для каталога
    image = models.ImageField(upload_to='products/', verbose_name='Изображение', null=True, blank=True)
    description = models.TextField(verbose_name='Описание', null=True, blank=True)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название ингредиента')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class ProductIngredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Напиток')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент')
    amount = models.CharField(max_length=50, verbose_name='Количество')

    class Meta:
        verbose_name = 'Состав напитка'
        verbose_name_plural = 'Составы напитков'
        unique_together = ('product', 'ingredient')  # Один ингредиент для одного продукта

    def __str__(self):
        return f"{self.product.name} - {self.ingredient.name}"


class StopList(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name='Недоступный ингредиент')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Кто добавил')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Когда добавлен в стоп')

    class Meta:
        verbose_name = 'Стоп-лист'
        verbose_name_plural = 'Стоп-листы'

    def __str__(self):
        return f"{self.ingredient.name} (Стоп-лист)"


class SoldOut(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Недоступный продукт')
    reason = models.TextField(default='Отсутствует ингредиент', verbose_name='Причина')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Когда помечен как раскупленный')

    class Meta:
        verbose_name = 'Раскупленный товар'
        verbose_name_plural = 'Раскупленные товары'

    def __str__(self):
        return f"{self.product.name} (Раскуплен)"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')
    STATUS_CHOICES = [
        ('Новый', 'Новый'),
        ('В работе', 'В работе'),
        ('Готов', 'Готов'),
        ('Выдан', 'Выдан'),  # Добавим статус "Выдан"
        ('Отменен', 'Отменен'),  # Добавим статус "Отменен"
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Новый', verbose_name='Статус заказа')
    discount_applied = models.BooleanField(default=False, verbose_name='Скидка применена')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая стоимость до скидки')
    final_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Итоговая сумма')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время оформления заказа')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']  # Сортировка заказов по дате создания

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username if self.user else 'Гость'}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')
    quantity = models.IntegerField(verbose_name='Количество')
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Цена за штуку')

    # total_price будет вычисляться в представлении или при сохранении
    # Django не поддерживает GENERATED ALWAYS AS (unit_price * quantity) STORED напрямую в моделях
    # Это можно сделать через метод модели или свойство

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f"{self.product.name} x {self.quantity} в заказе #{self.order.id}"

    @property
    def total_price(self):
        return self.quantity * self.unit_price


class ProductDescriptor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')
    descriptor = models.CharField(max_length=50, verbose_name='Дескриптор вкуса')

    class Meta:
        verbose_name = 'Дескриптор продукта'
        verbose_name_plural = 'Дескрипторы продуктов'
        unique_together = ('product', 'descriptor')  # Один дескриптор для одного продукта

    def __str__(self):
        return f"{self.product.name} - {self.descriptor}"


class UserPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    descriptor = models.CharField(max_length=50, verbose_name='Предпочитаемый дескриптор')
    weight = models.IntegerField(default=1, verbose_name='Вес предпочтения')

    class Meta:
        verbose_name = 'Предпочтение пользователя'
        verbose_name_plural = 'Предпочтения пользователей'
        unique_together = ('user', 'descriptor')

    def __str__(self):
        return f"{self.user.username} - {self.descriptor} ({self.weight})"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Автор отзыва')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name='Оценка (1-5)')
    comment = models.TextField(verbose_name='Комментарий', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отзыва')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв на {self.product.name} от {self.user.username if self.user else 'Аноним'} ({self.rating}/5)"


class Statistic(models.Model):  # Изменил название с Statistics на Statistic для соответствия Django conventions
    product = models.OneToOneField(Product, on_delete=models.CASCADE, verbose_name='Продукт', unique=True)
    times_ordered = models.IntegerField(default=0, verbose_name='Сколько раз заказан')

    class Meta:
        verbose_name = 'Статистика продукта'
        verbose_name_plural = 'Статистика продуктов'

    def __str__(self):
        return f"Статистика для {self.product.name}: {self.times_ordered} заказов"


class OrderStatusLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    old_status = models.CharField(max_length=50, verbose_name='Предыдущий статус')
    new_status = models.CharField(max_length=50, verbose_name='Новый статус')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Кто изменил')
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name='Когда изменено')

    class Meta:
        verbose_name = 'Лог статуса заказа'
        verbose_name_plural = 'Логи статусов заказов'
        ordering = ['-changed_at']

    def __str__(self):
        return f"Заказ #{self.order.id}: {self.old_status} -> {self.new_status}"
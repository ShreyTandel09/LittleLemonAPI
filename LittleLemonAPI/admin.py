from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,MenuItem,Category,Cart,Order,OrderItem

admin.site.register(CustomUser, UserAdmin)

@admin.register(MenuItem)
class MenuItem(admin.ModelAdmin):
    list_display = ( 'title','price','featured', 'category')
@admin.register(Category)
class Category(admin.ModelAdmin):
    list_display = ( 'title', 'slug')
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'menuitem', 'quantity')
@admin.register(Order)
class Order(admin.ModelAdmin):
    list_display = ('user', 'delivery_crew', 'status','total','date')

@admin.register(OrderItem)
class OrderItems(admin.ModelAdmin):
    list_display = ('order', 'menuitem', 'quantity')
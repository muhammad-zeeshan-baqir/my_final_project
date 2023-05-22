from django.contrib import admin
from .models import Customer, Product, Orders, Feedback, Category, Brand


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'address', 'mobile']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'price', 'description']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'email', 'address', 'mobile', 'status']


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'feedback', 'date']


class BrandAdmin(admin.ModelAdmin):
    list_display = ['name']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Orders, OrderAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Category, CategoryAdmin)

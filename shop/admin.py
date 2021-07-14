from django.contrib import admin
from .models import (
    Product, OrderItem, Order, Payment, Category, Checkout, Address, RealOrderItem
)


admin.site.register(Category)
admin.site.register(Address)
admin.site.register(Product)
admin.site.register(OrderItem)
admin.site.register(RealOrderItem)
admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(Checkout)

from django import forms

from shop.models import Product, Checkout


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title',
            'category',
            'image',
            'description',
            'price',
            'address',
            'available'
        ]
        exclude = ['owner', ]


class OrderConfirmation(forms.ModelForm):
    class Meta:
        model = Checkout
        fields = [
            'status'
        ]

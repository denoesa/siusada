from django.contrib.auth import get_user_model
from django import forms
from .models import (
    OrderItem, Product, Checkout, Payment, Order
)

User = get_user_model()


class AddToCartForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1)

    class Meta:
        model = OrderItem
        fields = ['quantity', ]

    def __init__(self, *args, **kwargs):
        self.product_id = kwargs.pop('product_id')
        product = Product.objects.get(id=self.product_id)
        super().__init__(*args, **kwargs)

    def clean(self):
        product_id = self.product_id
        product = Product.objects.get(id=self.product_id)
        quantity = self.cleaned_data['quantity']


class AddressForm(forms.ModelForm):
    class Meta:
        model = Checkout
        fields = [
            'address',
            'request',
        ]


class PaymentForm(forms.ModelForm):
    receipt = forms.FileField(label='receipt', required=True)

    class Meta:
        model = Payment
        fields = [
            'receipt'
        ]

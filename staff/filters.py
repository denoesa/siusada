import django_filters as filters
from django.forms.widgets import TextInput, ChoiceWidget
from shop.models import Product, Checkout


class ProductFilter(filters.FilterSet):

    class Meta:
        model = Product
        fields = ['owner', ]


class OrderFilter(filters.FilterSet):

    class Meta:
        model = Checkout
        fields = ['owner', ]


class ConfirmedFilter(filters.FilterSet):

    class Meta:
        model = Checkout
        fields = ['owner', 'status', ]

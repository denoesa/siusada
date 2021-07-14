import django_filters as filters
from django.forms.widgets import TextInput, ChoiceWidget
from .models import Product, Category, Address


class ProductFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains', widget=TextInput(
        attrs={'placeholder': 'Search product ...', 'size': 40, }), label=False)
    category = filters.ModelChoiceFilter(
        queryset=Category.objects.all(), label=False, empty_label='All category')
    address = filters.ModelChoiceFilter(
        queryset=Address.objects.all(), label=False, empty_label='All location')

import django_filters as filters
from shop.models import Checkout


class ProfileFilter(filters.FilterSet):

    class Meta:
        model = Checkout
        fields = ['user', ]

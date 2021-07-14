from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('cart', views.CartView.as_view(), name='summary'),
    path('product/<slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('increase-quantity/<pk>/',
         views.IncreaseQuantityView.as_view(), name='increase-quantity'),
    path('decrease-quantity/<pk>/',
         views.DecreaseQuantityView.as_view(), name='decrease-quantity'),
    path('remove-from-cart/<pk>/',
         views.RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('checkout/seller/<pk>', views.CheckoutView.as_view(), name='checkout'),
    path('payment/checkout/<pk>', views.PaymentView.as_view(), name='payment'),
    path('thanks/payment/<pk>', views.ThankYou.as_view(), name='thanks'),
    path('cart/seller/<pk>', views.CartDetailView.as_view(), name='cart-detail')

]

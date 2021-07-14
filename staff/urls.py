from django.urls import path
from . import views
from userbase.views import ProfileDataView, ProfileUpdateView

app_name = 'staff'

urlpatterns = [
    path('', views.StaffBaseView.as_view(), name='dashboard'),
    path('profile/', ProfileDataView.as_view(), name='profile'),
    path('profile/<pk>/update/', ProfileUpdateView.as_view(), name='profile-update'),
    path('create/', views.ProductCreateView.as_view(), name='product-create'),
    path('products/', views.ProductListView.as_view(), name='products'),
    path('products/<pk>/update/',
         views.ProductUpdateView.as_view(), name='product-update'),
    path('products/<pk>/delete/',
         views.ProductDeleteView.as_view(), name='product-delete'),
    path('order/', views.StaffOrderView.as_view(), name='order'),
    path('order/confirmed', views.ConfirmedOrderView.as_view(),
         name='confirmed-order'),
    path('order/<pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('order/<pk>/confirm-order/',
         views.ConfirmOrderView.as_view(), name='confirm-order'),
]

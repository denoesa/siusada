from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from core import views
from userbase.views import ProfileDataView, ProfileUpdateView, CustomerUpdateView, OrderDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', views.HomeView.as_view(), name='home'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('shop/', include('shop.urls', namespace='shop')),
    path('staff/', include('staff.urls', namespace='staff')),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/<pk>/update/', CustomerUpdateView.as_view(),
         name='customer-profile-update'),
    path('accounts/signup/', include('userbase.urls', namespace='signup')),
    path('order/<pk>/', OrderDetailView.as_view(), name='order-detail'),
]

urlpatterns += static(settings.STATIC_URL,
                      document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)

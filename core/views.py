from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import reverse
from django.views import generic
from shop.models import Order
from .forms import ContactForm
from django.contrib.auth import get_user_model
from shop.models import Product, Category, Checkout
from shop.filters import ProductFilter
from django.http import HttpResponse
from .filters import ProfileFilter


User = get_user_model()


class FilteredProfile(generic.ListView):
    filterset_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filterset_class(
            self.request.GET, queryset=Checkout.objects.filter(
                user=self.request.user, totalpay__gte=0).order_by('-checkout_date'))
        return self.filterset.qs.distinct()


class ProfileView(LoginRequiredMixin, FilteredProfile):
    template_name = 'userprofile.html'
    model = Checkout
    paginate_by = 10
    filterset_class = ProfileFilter


class FilteredListView(generic.ListView):
    filterset_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filterset_class(
            self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context


class HomeView(FilteredListView):
    template_name = 'shop/product_list.html'
    model = Product
    paginate_by = 12
    filterset_class = ProductFilter
    ordering = ['-created']


class ContactView(LoginRequiredMixin, generic.FormView):
    form_class = ContactForm
    template_name = 'contact.html'

    def get_success_url(self):
        return reverse("home")

    def form_valid(self, form):
        messages.info(
            self.request, "Thanks for getting in touch. We have received your message.")
        name = form.cleaned_data.get('name')
        message = form.cleaned_data.get('message')
        user = self.request.user.email

        full_message = f"""
            Received message below from {name} {user}

            {message}

            """
        send_mail(
            subject="Received contact form submission",
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.NOTIFY_EMAIL]
        )
        return super(ContactView, self).form_valid(form)

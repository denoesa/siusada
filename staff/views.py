from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse, get_object_or_404
from django.views import generic
from shop.models import Order, Product, Payment, OrderItem, Checkout, RealOrderItem
from .forms import ProductForm, OrderConfirmation
from .mixins import StaffUserMixin
from django.contrib.auth import get_user_model
from shop.utils import get_or_set_order_session
from django.utils import timezone
from django.db.models import Sum
from django_filters.views import BaseFilterView
from .filters import ProductFilter, OrderFilter, ConfirmedFilter
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()


class OrderFilteredListView(generic.ListView):
    filterset_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filterset_class(
            self.request.GET, queryset=Checkout.objects.filter(owner=self.request.user).order_by('-checkout_date'))
        return self.filterset.qs.distinct()


class StaffOrderView(LoginRequiredMixin, StaffUserMixin, OrderFilteredListView):
    template_name = 'dashboard/order.html'
    model = Checkout
    paginate_by = 10
    filterset_class = OrderFilter


class StaffBaseView(LoginRequiredMixin, StaffUserMixin, generic.ListView):
    template_name = 'dashboard/index.html'
    model = Checkout

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context = {
            'all': self.get_queryset(),
            'order': Checkout.objects.filter(owner=self.request.user, status=True).count(),
            'solds': RealOrderItem.objects.filter(checkout__owner=self.request.user, checkout__status=True).aggregate(total=Sum('quantity')),
            'products': Product.objects.filter(owner=self.request.user.id).count(),
            'earnings': Checkout.objects.filter(owner=self.request.user, status=True).aggregate(earn=Sum('totalpay')),
            'recents': Checkout.objects.filter(owner=self.request.user).order_by('-checkout_date')[:5]
        }
        return context


class ConfirmFilteredListView(generic.ListView):
    filterset_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filterset_class(
            self.request.GET, queryset=Checkout.objects.filter(owner=self.request.user, status=True).order_by('-checkout_date'))
        return self.filterset.qs.distinct()


class ConfirmedOrderView(LoginRequiredMixin, StaffUserMixin, ConfirmFilteredListView):
    template_name = 'dashboard/confirmed-order.html'
    model = Checkout
    paginate_by = 10
    filterset_class = ConfirmedFilter


class ProductFilteredListView(generic.ListView):
    filterset_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filterset_class(
            self.request.GET, queryset=Product.objects.filter(owner=self.request.user).order_by('-created'))
        return self.filterset.qs.distinct()


class ProductListView(LoginRequiredMixin, StaffUserMixin, ProductFilteredListView):
    template_name = 'dashboard/product.html'
    model = Product
    paginate_by = 10
    filterset_class = ProductFilter


class ProductCreateView(LoginRequiredMixin, StaffUserMixin, generic.CreateView):
    template_name = 'dashboard/product-create.html'
    form_class = ProductForm

    def get_success_url(self):
        return reverse("staff:products")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()
        return super(ProductCreateView, self).form_valid(form)


class ProductUpdateView(LoginRequiredMixin, StaffUserMixin, generic.UpdateView):
    template_name = 'dashboard/product-update.html'
    form_class = ProductForm
    queryset = Product.objects.all()

    def get_success_url(self):
        return reverse("staff:products")

    def form_valid(self, form):
        form.save()
        return super(ProductUpdateView, self).form_valid(form)


class ProductDeleteView(LoginRequiredMixin, StaffUserMixin, generic.DeleteView):
    template_name = 'dashboard/product-delete.html'
    queryset = Product.objects.all()

    def get_success_url(self):
        return reverse("staff:products")


class OrderDetailView(LoginRequiredMixin, StaffUserMixin, generic.TemplateView):
    template_name = 'dashboard/order-detail.html'
    queryset = Order.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["checkouts"] = Checkout.objects.filter(
            pk=self.kwargs['pk'], owner=self.request.user.id)
        context["itemcheckout"] = Checkout.objects.filter(
            pk=self.kwargs['pk'])
        context["customers"] = Checkout.objects.filter(
            pk=self.kwargs['pk']).distinct()
        context["payments"] = Payment.objects.filter(
            checkout__pk=self.kwargs['pk'], owner=self.request.user.id)
        return context


class ConfirmOrderView(LoginRequiredMixin, StaffUserMixin, generic.UpdateView):
    template_name = 'dashboard/confirm.html'
    form_class = OrderConfirmation

    def get_object(self, pk=None):
        return get_object_or_404(Checkout, pk=self.kwargs["pk"], owner=self.request.user.id)

    def get_success_url(self, **kwargs):
        return reverse("staff:order")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["checkouts"] = Checkout.objects.filter(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.status = True
        obj.save()

        useremail = User.objects.filter(checkoutuser__pk=self.kwargs['pk'])
        order = Checkout.objects.get(pk=self.kwargs['pk'])
        shopname = self.request.user.name
        shopemail = self.request.user.email

        full_message = f"""
            Hi, your order with code {order} is ready. We will organise them for you, please wait.

            Thanks.

            {shopname} - {shopemail}
            """

        for i in useremail:
            send_mail(
                subject="SIUSADA - Order Confirmation",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[i.email]
            )

        return super(ConfirmOrderView, self).form_valid(form)

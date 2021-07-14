from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, reverse, redirect
from django.views import generic
from .forms import AddToCartForm, AddressForm, PaymentForm
from .models import Product, OrderItem, Payment, Order, Category, Checkout
from .utils import get_or_set_order_session
from .filters import ProductFilter
from django.db.models import Count, Sum
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()


class ProductDetailView(generic.FormView):
    template_name = 'shop/product_detail.html'
    form_class = AddToCartForm

    def get_object(self):
        return get_object_or_404(Product, slug=self.kwargs["slug"])

    def get_success_url(self):
        return reverse("shop:summary")

    def get_form_kwargs(self):
        kwargs = super(ProductDetailView, self).get_form_kwargs()
        kwargs["product_id"] = self.get_object().id
        return kwargs

    def form_valid(self, form):
        order = get_or_set_order_session(self.request)
        product = self.get_object()

        item_filter = order.items.filter(
            product=product
        )

        if item_filter.exists():
            item = item_filter.first()
            item.quantity += int(form.cleaned_data['quantity'])
            item.save()

        else:
            new_item = form.save(commit=False)
            new_item.product = product
            new_item.order = order
            new_item.save()

        return super(ProductDetailView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['product'] = self.get_object()
        return context


class CartView(LoginRequiredMixin, generic.TemplateView):
    template_name = "shop/cart.html"

    def get_queryset(self):
        order = get_or_set_order_session(self.request)
        return order

    def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)
        cart = self.get_queryset()
        context["order"] = cart.items.values(
            'product_owner__name', 'product_owner').annotate(count=Count('product_owner__name'), countpro=Sum('quantity'))
        return context


class CartDetailView(generic.TemplateView):
    template_name = "shop/cart-detail.html"

    def get_queryset(self):
        order = get_or_set_order_session(self.request)
        return order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.get_queryset()

        context["orderitem"] = cart.items.filter(
            product_owner=self.kwargs['pk'])
        context["total"] = cart.items.filter(
            product_owner=self.kwargs['pk']).aggregate(price=Sum('product_total_price'))
        context['kwargs'] = self.kwargs
        return context


class IncreaseQuantityView(generic.View):
    def get(self, request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        order_item.quantity += 1
        order_item.product_total_price += order_item.product.price
        order_item.save()
        return redirect("shop:summary")


class DecreaseQuantityView(generic.View):
    def get(self, request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        if order_item.quantity <= 1:
            order_item.delete()
        else:
            order_item.quantity -= 1
            order_item.product_total_price -= order_item.product.price
            order_item.save()
        return redirect("shop:summary")


class RemoveFromCartView(generic.View):
    def get(self, request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        order_item.delete()
        return redirect("shop:summary")


class CheckoutView(LoginRequiredMixin, generic.FormView):
    template_name = 'shop/checkout.html'
    form_class = AddressForm

    def get_queryset(self):
        order = get_or_set_order_session(self.request)
        return order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.get_queryset()
        context["orderitem"] = cart.items.filter(
            product_owner=self.kwargs['pk'])
        context["total"] = cart.items.filter(
            product_owner=self.kwargs['pk']).aggregate(price=Sum('product_total_price'))
        context['kwargs'] = self.kwargs
        return context

    def form_valid(self, form):
        carts = self.get_queryset()
        total = carts.items.filter(
            product_owner__id=self.kwargs['pk']).aggregate(price=Sum('product_total_price'))
        obj = form.save(commit=False)
        obj.order = get_or_set_order_session(self.request)
        obj.name = self.request.user.name
        obj.phone = self.request.user.phone
        obj.owner = User.objects.get(pk=self.kwargs['pk'])
        obj.totalpay = total['price']
        obj.user = User.objects.get(pk=self.request.user.pk)
        obj.save()

        self.pk = obj.pk

        shopemail = User.objects.filter(checkoutowner__pk=self.pk)
        order = Checkout.objects.get(pk=self.pk)
        username = self.request.user.name
        useremail = self.request.user.email

        full_message = f"""
            Hi, You just have new order from

            user = {username}
            email = {useremail}

            with order code {order}, please check your order.

            Have a great day.

            """

        for i in shopemail:
            send_mail(
                subject="SIUSADA - New Order",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[i.email]
            )

        return super(CheckoutView, self).form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse("shop:payment", kwargs={'pk': self.pk})


class PaymentView(LoginRequiredMixin, generic.FormView):
    template_name = 'shop/payment.html'
    form_class = PaymentForm

    def get_queryset(self):
        order = get_or_set_order_session(self.request)
        return order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.get_queryset()
        context["total"] = Checkout.objects.filter(pk=self.kwargs['pk'])
        context['kwargs'] = self.kwargs
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.order = get_or_set_order_session(self.request)
        obj.owner = User.objects.get(checkoutowner__pk=self.kwargs['pk'])
        obj.checkout = Checkout.objects.get(pk=self.kwargs['pk'])
        obj.save()
        self.pk = obj.pk
        return super(PaymentView, self).form_valid(form)

    def get_success_url(self):
        return reverse("shop:thanks", kwargs={'pk': self.pk})


class ThankYou(generic.TemplateView):
    template_name = 'shop/thanks.html'

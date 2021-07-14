from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
from allauth.account.views import SignupView
from .forms import FormSignupStaff, FormSignupCustomer, ProfileUpdateForm, CustomerUpdateForm
from staff.mixins import StaffUserMixin
from django.shortcuts import reverse
from shop.models import Order, Checkout
from shop.utils import get_or_set_order_session


class StaffSignup(SignupView):
    template_name = 'account/signup-staff.html'
    form_class = FormSignupStaff
    redirect_field_name = 'next'
    view_name = 'staff_sign_up'

    def get_context_data(self, **kwargs):
        ret = super(StaffSignup, self).get_context_data(**kwargs)
        ret.update(self.kwargs)
        return ret


class CustomerSignup(SignupView):
    template_name = 'account/signup-customer.html'
    form_class = FormSignupCustomer
    redirect_field_name = 'next'
    view_name = 'customer_sign_up'

    def get_context_data(self, **kwargs):
        ret = super(CustomerSignup, self).get_context_data(**kwargs)
        ret.update(self.kwargs)
        return ret


class ProfileDataView(LoginRequiredMixin, StaffUserMixin, generic.ListView):
    template_name = 'dashboard/profile.html'
    queryset = User.objects.all()


class ProfileUpdateView(LoginRequiredMixin, StaffUserMixin, generic.UpdateView):
    template_name = 'dashboard/profile-update.html'
    form_class = ProfileUpdateForm
    queryset = User.objects.all()

    def get_success_url(self):
        return reverse("staff:profile")

    def form_valid(self, form):
        form.save()
        return super(ProfileUpdateView, self).form_valid(form)


class CustomerUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'profile-update.html'
    form_class = CustomerUpdateForm
    queryset = User.objects.all()

    def get_success_url(self):
        return reverse("profile")

    def form_valid(self, form):
        form.save()
        return super(CustomerUpdateView, self).form_valid(form)


class OrderDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'order-detail.html'
    queryset = Checkout.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order"] = Checkout.objects.filter(
            user=self.request.user.id, pk=self.kwargs['pk'])
        return context

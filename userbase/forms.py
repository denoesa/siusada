from django import forms
from allauth.account.forms import SignupForm
from django.db import models

from .models import User


class FormSignupStaff(SignupForm):
    email = forms.EmailField(
        max_length=254, label='email')
    name = forms.CharField(max_length=254, label='name')
    avatar = forms.ImageField(label='avatar', required=True)
    phone = forms.IntegerField(label='phone')
    user_address = forms.CharField(
        max_length=256, label='address')
    biography = forms.CharField(max_length=256, label='bio')

    def save(self, request):
        user = super(FormSignupStaff, self).save(request)
        user.email = self.cleaned_data['email']
        user.name = self.cleaned_data['name']
        user.avatar = self.cleaned_data['avatar']
        user.phone = self.cleaned_data['phone']
        user.user_address = self.cleaned_data['user_address']
        user.biography = self.cleaned_data['biography']
        user.is_staff = True
        user.is_superuser = False
        user.save()

        return user


class FormSignupCustomer(SignupForm):
    email = forms.EmailField(
        max_length=254, label='email')
    name = forms.CharField(max_length=254, label='name')
    avatar = forms.ImageField(label='avatar', required=True)
    phone = forms.IntegerField(label='phone')
    user_address = forms.CharField(
        max_length=256, label='address')
    biography = forms.CharField(max_length=256, label='bio')

    def save(self, request):
        user = super(FormSignupCustomer, self).save(request)
        user.email = self.cleaned_data['email']
        user.name = self.cleaned_data['name']
        user.avatar = self.cleaned_data['avatar']
        user.phone = self.cleaned_data['phone']
        user.user_address = self.cleaned_data['user_address']
        user.biography = self.cleaned_data['biography']
        user.is_staff = False
        user.is_superuser = False
        user.save()

        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'name',
            'email',
            'avatar',
            'user_address',
            'phone',
            'biography',
        ]


class CustomerUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'name',
            'email',
            'avatar',
            'user_address',
            'phone',
            'biography',
        ]

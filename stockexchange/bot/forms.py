from django import forms

from .models import User, Portfolio


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'id',
            'firstname',
            'secondname',
            'username'
        )
        widgets = {
            'username': forms.TextInput
        }


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = (
            'user',
            'ticker',
            'name'
        )
        widgets = {
            'name': forms.TextInput,

        }
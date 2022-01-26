from django.contrib import admin
from .models import User, Portfolio
from .forms import UserForm, PortfolioForm


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'firstname', 'secondname', 'username')
    form = UserForm


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'ticker', 'name')
    form = PortfolioForm

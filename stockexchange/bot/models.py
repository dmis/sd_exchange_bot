from django.db import models


class User(models.Model):
    id = models.PositiveIntegerField(
        primary_key=True,
        verbose_name='Telegram user id'
    )

    firstname = models.CharField(
        verbose_name='First name',
        max_length=200
    )

    secondname = models.TextField(
        verbose_name='Second name',
        max_length=200
    )

    username = models.TextField(
        verbose_name='Username',
        max_length=100
    )

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'


class Portfolio(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='User',

    )
    ticker = models.CharField(
        verbose_name='Ticker',
        max_length=5

    )
    name = models.CharField(
        verbose_name='Name of the security',
        max_length=200
    )

    class Meta:
        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolios'

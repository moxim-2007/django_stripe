from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=1000)
    price = models.IntegerField(verbose_name="Price in cents or kopecks")
    currency = models.CharField(max_length=3, choices=(("usd", "usd"), ("rub", "rub")))


class Discount(models.Model):
    percent_off = models.IntegerField(
        choices=[(i, i) for i in range(101)], verbose_name="Percentage discount"
    )


class Tax(models.Model):
    name = models.CharField(max_length=100)
    inclusive = models.BooleanField(verbose_name="Is tax included in the price")
    percentage = models.IntegerField(
        choices=[(i, i) for i in range(101)], verbose_name="Percentage tax"
    )


class Order(models.Model):
    items = models.ManyToManyField(Item)
    discount = models.ManyToManyField(Discount, blank=True)
    tax = models.ManyToManyField(Tax, blank=True)

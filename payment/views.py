import os
from dotenv import load_dotenv

import stripe
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.http import JsonResponse

from .models import Item, Order

load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_SECRET_KEY")


class ItemDetail(DetailView):
    model = Item
    template_name = "payment/item_detail.html"

    def get_object(self, queryset=None):
        return Item.objects.get(id=self.kwargs["id"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["api_key"] = os.getenv("STRIPE_API_PUBLIC_KEY")
        return context


def buy_item(request, **kwargs):
    if request.method == "GET":
        item = Item.objects.get(id=kwargs["id"])
        checkout_session = create_strip_session(
            currency=item.currency,
            name_item=item.name,
            amount=item.price,
            tax=False,
            coupon=False,
        )
        return JsonResponse({"sessionId": checkout_session.id})


def buy_order(request, **kwargs):
    if request.method == "GET":
        order = Order.objects.get(id=kwargs["id"])
        coupon_db = order.discount.first()
        tax_db = order.tax.first()
        if coupon_db:
            coupon = stripe.Coupon.create(
                duration="once", id=coupon_db.id, percent_off=coupon_db.percent_off
            )
        else:
            coupon = False
        if tax_db:
            tax = stripe.TaxRate.create(
                display_name=tax_db.name,
                inclusive=tax_db.inclusive,
                percentage=tax_db.percentage,
            )
        else:
            tax = False
        price_order = 0
        name_order = ""
        currency_order = order.items.first().currency
        for item in order.items.all():
            if item.currency == currency_order:
                name_order += f"{item.name}; "
                price_order += item.price

        checkout_session = create_strip_session(
            currency_order, name_order, price_order, tax, coupon
        )
        if coupon:
            coupon.delete()
        return redirect(checkout_session.url)


def create_strip_session(currency, name_item, amount, tax, coupon):
    params = {
        "line_items": [
            {
                "price_data": {
                    "currency": currency,
                    "product_data": {
                        "name": name_item,
                    },
                    "unit_amount": amount,
                },
                "quantity": 1,
            }
        ],
        "mode": "payment",
        "success_url": "http://localhost:8000/",
        "cancel_url": "http://localhost:8000/",
    }
    if tax:
        params["line_items"][0]["tax_rates"] = [f"{tax.id}"]
    if coupon:
        params["discounts"] = [{"coupon": coupon}]

    checkout_session = stripe.checkout.Session.create(**params)
    return checkout_session

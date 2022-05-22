from django.urls import path

from .views import buy_item, ItemDetail, buy_order

urlpatterns = [
    path("buy/<int:id>/", buy_item),
    path("item/<int:id>/", ItemDetail.as_view()),
    path("buy_order/<int:id>/", buy_order),
]

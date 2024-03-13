from django.urls import path
from . import views



urlpatterns=[
    path('balance/', views.BalanceListView.as_view(), name='api_balance'),
    path('add/', views.CoinbasePaymentView.as_view(), name="coinbase"),
    path('buy/<int:pk>/', views.BuyView.as_view(), name='api_buy'),
    path('receive/', views.CoinbaseWebhookView.as_view(), name='coinbase_webhook'),
    path('create/telegram/', views.TelegramClientCreateView.as_view(), name='telegram_client_create'),
    path('telegram/receive/', views.TelegrambaseWebhookView.as_view(), name='telegram_webhook'),
]
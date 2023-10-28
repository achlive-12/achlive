from django.urls import path,include
from .views import *
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView
urlpatterns = [
    path('history/', DashboardView.as_view(), name="history"),
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('activate/<str:uidb64>/<str:token>/', AccountActivate.as_view(), name='activate'),
    path('', include('dj_rest_auth.urls')),
    path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
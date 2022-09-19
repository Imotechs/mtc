
from django.contrib import admin
from django.urls import path,include
from .views import (
    register,copy_wallet,wallet,WithdrawView, withdraw_success,
)
urlpatterns = [
path('withdraw/945467890/',WithdrawView.as_view(),name = 'withdraw'),
path('withdrawal/success',withdraw_success,name = 'withdraw_success'),
path('me/',wallet, name = 'wallet'),
#deposit
path('deposit/usdt/copy/<int:pk>/',copy_wallet,name='copy_wallet')
]

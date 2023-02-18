
from django.contrib import admin
from django.urls import path,include
from .views import (
    register,copy_wallet,wallet,WithdrawView, withdraw_success,
    advert,make_wallet,check_wallet,refer,
    get_account,my_com,lock_assets,convertMTC,testings
        )
urlpatterns = [
path('withdraw/945467890/',WithdrawView.as_view(),name = 'withdraw'),
path('withdrawal/success',withdraw_success,name = 'withdraw_success'),
path('me/',wallet, name = 'wallet'),
#advert
path('advert/',advert, name = 'advert'),
path('test/',testings),
#deposit
path('deposit/usdt/copy/<int:pk>/',copy_wallet,name='copy_wallet'),
path('link/mtc/wallet/',make_wallet,name = 'get_wallet'),
path('see/my/mtc/wallet/',check_wallet,name = 'check_wallet'),
path('refer/earn/',refer,name = 'refer'),
path('get/account/',get_account, name ='user_account'),
path('my/comm/',my_com, name = 'my_com'),
path('lock/assets/',lock_assets, name = "lock_up"),
path('swap/mtc/',convertMTC, name = 'swap'),
]

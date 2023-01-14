from django.contrib import admin
from .models import (Account,Profile,Mail,Withdraw,
Subscribers,BuyTrade,SellTrade,Bonus,LockedAsset)
# Register your models here.

admin.site.register(Account)
admin.site.register(Profile)
admin.site.register(Mail)
admin.site.register(Withdraw)
admin.site.register(Subscribers)
admin.site.register(BuyTrade)
admin.site.register(SellTrade)
admin.site.register(Bonus)
admin.site.register(LockedAsset)

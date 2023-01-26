from django.contrib import admin
from .models import UserPayEvidence,Deposit,Coin,TradeTime

# Register your models here.

admin.site.register(UserPayEvidence)
admin.site.register(Deposit)
admin.site.register(Coin)
admin.site.register(TradeTime)

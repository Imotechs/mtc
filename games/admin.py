from django.contrib import admin
from .models import Games,AllGames,FreeGames,Lottery,Bid
# Register your models here.

admin.site.register(Games)
admin.site.register(AllGames)
admin.site.register(FreeGames)
admin.site.register(Lottery)
admin.site.register(Bid)
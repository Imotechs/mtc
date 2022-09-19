from django.contrib import admin
from .models import Account,Profile,Mail,Withdraw,Subscribers
# Register your models here.

admin.site.register(Account)
admin.site.register(Profile)
admin.site.register(Mail)
admin.site.register(Withdraw)
admin.site.register(Subscribers)

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete= models.CASCADE)
    uid = models.CharField(max_length=12, default= '',blank = True)
    phone = models.CharField(max_length=30, null=True,default= '',blank = True)
    referrer = models.CharField(max_length=60, null=True, default= '',blank = True)
    referrals = models.ManyToManyField(User,related_name='ref')
    referred = models.BooleanField(default= False)
    profited = models.BooleanField(default= False)
    def __str__(self):
        return f"{self.user}'s profile"


class Account(models.Model):
    user =  models.OneToOneField(User,on_delete= models.CASCADE)
    main = models.FloatField(blank=True, default= 0)
    balance =  models.FloatField(blank=True, default= 0)
    wallet = models.CharField(max_length=35,null=True,blank=True,unique=True)
    def __str__(self):
        return f"{self.user}'s account"
        
class Mail(models.Model):
    name = models.CharField(max_length=30, blank = True)
    email = models.CharField(max_length=30,blank = True)
    phone=models.CharField(max_length=30,blank = True)
    subject = models.TextField(blank = True) 
    message = models.TextField(blank = True) 
    seen = models.BooleanField(default=False)
    date_sent = models.DateTimeField(auto_now=True)




class Withdraw(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    method = models.CharField(max_length=60, blank=True)
    amount = models.FloatField(default=0)
    account_name = models.CharField(max_length=60, blank=True)
    account_number = models.CharField(max_length=60, blank=True)
    bank = models.CharField(max_length=60, blank=True)
    date_placed = models.DateTimeField(auto_now=True)
    date_approved = models.DateTimeField(blank=True, null=True)
    approved = models.BooleanField(default=False)
    cancel = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user}-{self.method}'

class Subscribers(models.Model):
    email = models.EmailField()
    date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.email}'

class BuyTrade(models.Model):
    user = models.ForeignKey(User,on_delete = models.CASCADE)
    usdt = models.FloatField()
    mtc = models.FloatField()
    buy_time = models.DateTimeField(auto_now=True)
    def __str__(self) :
        return self.user.username

class SellTrade(models.Model):
    user = models.ForeignKey(User,on_delete = models.CASCADE)
    usdt = models.FloatField()
    mtc = models.FloatField()
    profit = models.FloatField(null=True,blank=True)
    sell_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.user.username

class Bonus(models.Model):
    user = models.ForeignKey(User,on_delete = models.CASCADE)
    from_user = models.ForeignKey(User,on_delete = models.CASCADE,related_name='from_user')
    amount = models.FloatField()
    level = models.IntegerField()
    action = models.CharField( max_length = 15,null=True,blank = True)
    claimed = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.user.username

class LockedAsset(models.Model):
    user = models.ForeignKey(User,on_delete = models.CASCADE)
    amount = models.FloatField()
    profit = models.FloatField(default=0.0)
    claimed = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)
    date_to = models.DateTimeField()
    def __str__(self):
        return self.user.username
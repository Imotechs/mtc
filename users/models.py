from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete= models.CASCADE)
    uid = models.CharField(max_length=12, default= '',blank = True)
    country = models.CharField(max_length=30,null=True, default= '',blank = True)
    currency = models.CharField(max_length=30, null=True,blank = True)
    #flag = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=30, null=True,default= '',blank = True)
    referrer = models.CharField(max_length=60, null=True, default= '',blank = True)
    referred = models.BooleanField(default= False)
    profited = models.BooleanField(default= False)
    def __str__(self):
        return f"{self.user}'s profile"


class Account(models.Model):
    user =  models.OneToOneField(User,on_delete= models.CASCADE)
    main = models.FloatField(blank=True, default= 0)
    balance =  models.FloatField(blank=True, default= 0)

    def __str__(self):
        return f"{self.user}'s"
        
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
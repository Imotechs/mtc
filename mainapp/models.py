from django.db import models
from django.contrib.auth.models import User
from .paystack import Paystack
from users.models import Account
# Create your models here.

class TradeTime(models.Model):
    name =models.CharField(max_length=15,null=True,blank=True)
    date_to = models.DateTimeField()
    interval  =models.DateTimeField()
    date = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class Coin(models.Model):
    name = models.CharField(max_length=15)
    value = models.FloatField(default=0.0)
    cap_rate = models.FloatField(default = 0.0)
    def __str__(self):
        return self.name

class Deposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    usd = models.FloatField(default=0)
    method = models.CharField(max_length=15, blank=True)
    transaction_id = models.CharField(max_length=20, blank=True)
    date = models.DateTimeField(blank=True, null=True, auto_now=True)
    date_approved = models.DateTimeField(blank=True, null=True)
    placed = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    cancel = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.user}'
    def verify_payment(self):
        paystack = Paystack()
        status, result = paystack.verify_payment(self.transaction_id,self.amount)
        if status:
            if float(result['amount']/100) >= float(self.amount):
                self.approved = True
                self.method = 'Card Payment'
                self.placed = True
            self.save()
        if self.approved:
            return True
        else:
            return False

class UserPayEvidence(models.Model):
    user =models.ForeignKey(User,on_delete=models.CASCADE)
    evidence = models.ImageField(verbose_name = 'A photo of your payment Evidence',upload_to = 'media/payment_Evidence')
    date_upload = models.DateTimeField(auto_now=True)
    def get_total_evidence(self):
        return self.objects.all().count()
  


class Lottery(models.Model):
    name = models.CharField(max_length=30,null = True)
    numbers = models.CharField(max_length=30,null = True)
    due_date = models.DateTimeField()
    date = models.DateTimeField(auto_now=True)
    win = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Bid(models.Model):
    user = models.ForeignKey(User,null=True,on_delete=models.SET_NULL)
    lottery = models.ForeignKey(Lottery,null=True,on_delete=models.SET_NULL)
    number = models.CharField(max_length=30,null = True)
    stake = models.FloatField(default=0)
    profit = models.FloatField(default=0)
    win = models.BooleanField(default=False)
    date = models.DateField(auto_now=True)

    def __str__(self):
        return self.user.username
    def verify_bid(self):
        account,created = Account.objects.get_or_create(user = self.user)
        self.profit = 5*self.stake
        account.balance += 5*self.stake
        self.win = True
        self.save()
        account.save()
        return True
from django.db import models
from django.contrib.auth.models import User
from .paystack import Paystack
from users.models import Account
# Create your models here.


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
  

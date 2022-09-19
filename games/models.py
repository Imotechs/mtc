from django.db import models
from django.contrib.auth.models import User
from users.models import Account
# Create your models here.

class AllGames(models.Model):
    name = models.CharField(max_length=30)
    players = models.ManyToManyField(User)
    def __str__(self):
        return f'{self.name}'
    @property
    def total_play(self):
        return self.players.count()



class Games(models.Model):
    user = models.ForeignKey(User,default = 1,on_delete=models.SET_DEFAULT)
    game = models.ForeignKey(AllGames,null=True,on_delete=models.SET_NULL)
    stake = models.FloatField(default=0)
    profit = models.FloatField(default=0)
    win = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.game}-{self.stake}'
    
    #def winners(self)
class FreeGames(models.Model):
    user = models.ForeignKey(User,default = 1,on_delete=models.SET_DEFAULT)
    game = models.ForeignKey(AllGames,null=True,on_delete=models.SET_NULL)
    date = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.game.name}'

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
        
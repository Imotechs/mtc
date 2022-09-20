from locale import currency
from django.shortcuts import render,redirect
import random
from django.contrib import messages
from users.models import  Mail, Profile
from .models import Deposit
from django.utils import timezone
from users.models import Account,Subscribers
from users import functions
from django.db.models import Sum
from games.models import AllGames, Games
from datetime import datetime,timedelta,date
from . import location,exchange
from games.models import Lottery,Bid
# Create your views here.


def my_custom_error_view(request):
    return render(request,'500.html')

def page_not_found_view(request):
    return render(request,'404.html')
    
def page_restricted_view(request):
    return render(request,'403.html')

    
def home(request):
    top_list = Games.objects.filter(win = True).order_by('-profit').order_by('-date')[:10]
    my_games = None
    jackpot = Lottery.objects.filter(win = True).last()
    home = True
    if request.user.is_authenticated:
        my_games = Games.objects.filter(user = request.user).order_by('-profit').order_by('-date')[:10]
    context = {
        'top_players':top_list,
        'three_players':top_list[:3],
        'my_games':my_games,
        'home':home,
        'jackpot':jackpot,
    }
    return render(request,'mainapp/index.html',context)
def games(request):
    games = AllGames.objects.all()
    three_players = Games.objects.filter(win = True).order_by('-profit').order_by('-date')[:10]
    game = True
    context = {
        'games':games,
        'three_players':three_players[:3],
        'game':game,
        }
    return render(request,'mainapp/games.html',context)

def subscribe(request):
    if request.method =='POST':
        email = request.POST['email']
        if email == '':
            messages.info(request,' must enter an Email')
            return redirect('home')
        try:
            exist = Subscribers.objects.get(email = email)
            messages.info(request, f'{exist} already subscribed')
            return redirect('home')
        except:
            obj = Subscribers.objects.create(email = email)
            obj.save()
            messages.info(request, 'Thank you for subscribing to our weekly Updates')
            return redirect('home')

def about(request):
    return render(request,'mainapp/about.html')

def contact(request):
    if request.method =='POST':
        obj, created = Mail.objects.get_or_create(
            name = request.POST['name'],
            email = request.POST['email'],
            phone = request.POST['phone'],
            subject = request.POST['subject'],
            message = request.POST['message'],   
            )
        obj.save()
        messages.success(request,'Mail Sent!')
        return redirect ('/')
    context = {
            'contact':True,
        }
    return render(request,'mainapp/contact.html',context)

def terms(request):
    return render(request,'mainapp/terms.html')

def testimonial(request):
    return render(request,'mainapp/testimonial.html')

def tournaments(request):

    context = {
        'turn':True,
    }
    return render(request,'mainapp/tournaments.html',context)

def lottery(request):
    current_lot = Lottery.objects.filter(win = False).last()
    last_won_lot = Lottery.objects.filter(win = True).last()
    won_bids = Bid.objects.filter(win = True).order_by('-profit')
    all_lot = Lottery.objects.all()
    last_winners = Bid.objects.filter(win = True,lottery = last_won_lot).order_by('-profit')
    today = timezone.now()
    nums = [ch for ch in range(1,51)]

    if today > current_lot.due_date:
        for bid in current_lot.bid_set.all():
            bid_numbers = [ int(ch) for ch in current_lot.numbers.replace("[","").replace("]","").split(',')]
            print(bid_numbers)
            if int(bid.number) in bid_numbers :
                print(bid.number)
                bid.verify_bid()
                
        now,due = functions.get_date()
        new_lot = Lottery.objects.create(
            name = f'stake lottery{current_lot.id+1}',
            numbers = random.choices(nums,k = 5),
            due_date = due,
                )
        current_lot.win = True
        current_lot.save()
        new_lot.save()
        return redirect('lot')
    if request.method == 'POST':
        if request.user.is_authenticated:
            account,created = Account.objects.get_or_create(user = request.user)
            if account.main >= float(request.POST['amount']):
                user_bid = Bid.objects.create(
                    user = request.user,
                    lottery = Lottery.objects.last(),
                    stake = request.POST['amount'],
                    number = request.POST['number'],
                )
                user_bid.save()
                account.main -= float(request.POST['amount'])
                account.save()
                messages.info(request,'Bid purchased with main wallet')
                return redirect('lot')
            elif account.balance >= float(request.POST['amount']):
                user_bid = Bid.objects.create(
                    user = request.user,
                    lottery = Lottery.objects.last(),
                    stake = request.POST['amount'],
                    number = request.POST['number'],
                )
                user_bid.save()
                account.balance -= float(request.POST['amount'])
                account.save()
                messages.info(request,'Bid purchased from Earning wallet')
                return redirect('lot')
            else:
                messages.info(request,' insufficient balance to bid!')
                return redirect('wallet')
        return redirect('login')
    if request.user.is_authenticated:
        context = {
            'lot':True,
            'all_lot':all_lot,
            'current_lot':current_lot,
            'my_bids_today':Bid.objects.filter(user = request.user,lottery =current_lot),
            'last_won_lot':last_won_lot,
            'last_numbers':[ ch for ch in last_won_lot.numbers.replace("[","").replace("]","").split(',')],
            'won_bids':won_bids,
            'last_winners':last_winners,
            'all_my_bids':Bid.objects.filter(user = request.user).order_by('-date'),
            }
        return render(request,'mainapp/lotterys.html',context)
    else:
        context = {
            'lot':True,
            'all_lot':all_lot,
            'current_lot':current_lot,
            #'my_bids_today':Bid.objects.filter(user = request.user,lottery =current_lot),
            'last_won_lot':last_won_lot,
            'last_numbers':[ ch for ch in last_won_lot.numbers.replace("[","").replace("]","").split(',')],
            'won_bids':won_bids,
            'last_winners':last_winners,
            #'all_my_bids':Bid.objects.filter(user = request.user).order_by('-date'),
            }
        return render(request,'mainapp/lotterys.html',context)


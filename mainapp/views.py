from locale import currency
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
import random
import json
from django.contrib import messages
from users.models import  Mail, Profile,SellTrade,BuyTrade,Bonus
from .models import Deposit,Coin,TradeTime,Lottery,Bid
from django.utils import timezone
from users.models import Account,Subscribers
from users import functions
from django.db.models import Sum
from datetime import datetime,timedelta,date
from . import location,exchange
from django.http import JsonResponse,HttpResponse
# Create your views here.


def my_custom_error_view(request):
    return render(request,'500.html')

def page_not_found_view(request):
    return render(request,'404.html')

def page_restricted_view(request):
    return render(request,'403.html')


def home(request):


    trade = TradeTime.objects.last()
    today = timezone.now()
    if today >= trade.date_to:
        if today>=trade.interval:
            now,then = functions.get_date()
            interval = functions.get_interval()
            obj = {'id':trade.id, 'date_to':then,'interval':interval}
            TradeTime.objects.update(**obj)

            return redirect('home')

    top_biders = Bid.objects.filter(win = True).order_by('-profit').order_by('-date')[:10]
    my_bids = None
    top_bid_winners = Bid.objects.filter(win = True).order_by('-profit').order_by('-date')[:10]

    jackpot = Lottery.objects.filter(win = True).last()
    home = True
    if request.user.is_authenticated:
        my_bids = Bid.objects.filter(user = request.user).order_by('profit').order_by('-date')
    context = {
        'trade_time':trade,
        'top_bid':top_biders[:10],
        'top_three_bids':top_bid_winners[:3],
        'my_bids':my_bids,
        'home':home,
        'jackpot':jackpot,
    }
    return render(request,'mainapp/index.html',context)
def games(request):
    games = AllGames.objects.all()
    three_players = Games.objects.filter(win = True).order_by('profit').order_by('-date')[:10]
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

def trademore(request):
    return render(request,'users/trademore.html')

def policy(request):
    return render(request,'mainapp/policy.html')

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
    now,due = functions.get_date()
    current_lot = Lottery.objects.filter(win = False).last()
    last_won_lot = Lottery.objects.filter(win = True).order_by('id').last()
    won_bids = Bid.objects.filter(win = True).order_by('-date').order_by('-profit')
    all_lot = Lottery.objects.all().order_by('-date')
    last_winners = Bid.objects.filter(win = True,lottery = last_won_lot).order_by('-date').order_by('-profit')
    today = timezone.now()
    nums = [ch for ch in range(1,51)]
    if today > current_lot.due_date:
        for bid in current_lot.bid_set.all():
            bid_numbers = [ int(ch) for ch in current_lot.numbers.replace("[","").replace("]","").split(',')]
            if int(bid.number) in bid_numbers :
                bid.verify_bid()

        new_lot = Lottery.objects.create(
            name = f'MTC lottery {current_lot.id+1}',
            numbers = random.choices(nums,k = 5),
            due_date = due,
                )
        current_lot.win = True
        current_lot.save()
        new_lot.save()
        return redirect('lot')
    if request.method == 'POST':
        if request.user.is_authenticated:
            bid_amount = float(request.POST['amount'])
            account,created = Account.objects.get_or_create(user = request.user)
            if account.balance >= abs(bid_amount):
                user_bid = Bid.objects.create(
                    user = request.user,
                    lottery = Lottery.objects.last(),
                    stake = bid_amount,
                    number = request.POST['number'],
                )
                user_bid.save()
                account.balance -= bid_amount
                account.save()
                messages.info(request,'Bid purchased!')
                return redirect('lot')
            else:
                messages.info(request,' insufficient MTC balance to bid!')
                return redirect('wallet')
        return redirect('login')
    last_won = None
    if last_won_lot:
        last_won = [ ch for ch in last_won_lot.numbers.replace("[","").replace("]","").split(',')]

    if request.user.is_authenticated:
        my_bids = Bid.objects.filter(user=request.user).order_by('-date').order_by('-profit')
        context = {
            'lot':True,
            'all_lot':all_lot,
            'current_lot':current_lot,
            'my_bids_today':Bid.objects.filter(user = request.user,lottery =current_lot),
            'last_won_lot':last_won_lot,
            'last_numbers':last_won,
            'won_bids':won_bids,
            'my_bids':my_bids,
            'last_winners':last_winners,
            'all_my_bids':Bid.objects.filter(user = request.user).order_by('-date'),
            }
        return render(request,'mainapp/lotterys.html',context)
    else:
        context = {
            'lot':True,
            'all_lot':all_lot,
            'current_lot':current_lot,
            'last_won_lot':last_won_lot,
            'last_numbers':last_won,
            'won_bids':won_bids,
            'last_winners':last_winners,
            }
        return render(request,'mainapp/lotterys.html',context)

#met coin
@login_required
def trade_met(request):
    if request.method =="POST":
        account,created = Account.objects.get_or_create(user = request.user)
        data = json.loads(request.body.decode('utf-8'))
        met,created = Coin.objects.get_or_create(name = 'metcoin')
        amount = float(data['amount'])
        if data['status'] =='buy':
            if not account.wallet:
                msg = {'status':'MTC wallet not found for your account'}
                return JsonResponse(msg)
            if account.wallet and account.main >= amount and amount>0:
                met_eq = amount/met.value

                if met_eq>=5:
                    account.main-= amount
                    account.balance+= met_eq
                    account.save()
                    trade = BuyTrade.objects.create(user = request.user,
                    usdt =amount,mtc = met_eq)
                    trade.save()
                    msg = {"status":'Success!'}
                    return JsonResponse(msg)
                msg = {"status":'Can not Trade less than 5 MTC'}
                return JsonResponse(msg)
            if account.wallet and account.main < amount:
                msg = {"status":'Failed!'}
                return JsonResponse(msg)
            msg = {'status':'Error!,Try Agin'}
            return JsonResponse(msg)

        if data['status'] =='sale':
            if not account.wallet:
                msg = {'status':'MTC wallet not found for your account'}
                return JsonResponse(msg)
            if account.wallet and account.balance >= amount and amount>0:
                dollar_eq = amount*met.value
                last_trade = BuyTrade.objects.filter(user=request.user).last()

                profit = dollar_eq-last_trade.usdt
                if not profit > 0:
                    profit = 0.00
                trade = SellTrade.objects.create(user = request.user,
                usdt = dollar_eq,mtc = amount,profit =profit)
                trade.save()
                account.main+= dollar_eq
                account.balance-= amount
                account.save()
                master_ref = None
                if request.user.profile.referrer:
                    ref = Profile.objects.filter(uid = request.user.profile.referrer)
                if ref[0].referrer:
                    master_ref = Profile.objects.filter(uid = ref[0].referrer)
                if not profit <=0:
                    if ref:
                        bonus_1 = functions.get_bonus(1,profit)
                        b_obj = Bonus.objects.create(user = ref[0].user,
                                    level = 1,from_user = request.user,
                                    amount =bonus_1,claimed = False,
                                    action = 'Trading')
                        b_obj.save()
                        if request.user not in ref[0].referrals.all():
                            ref[0].referrals.add(request.user)
                            ref[0].save()
                        if master_ref:
                            bonus_2 = functions.get_bonus(2,profit)
                            b_obj = Bonus.objects.create(user = master_ref[0].user,
                                    level = 2,from_user = request.user,
                                    amount = bonus_2,claimed = False,
                                    action = 'Trading')
                            b_obj.save()
                msg = {"status":'Success!'}
                return JsonResponse(msg)
            if account.wallet and account.balance < amount:
                msg = {"status":'Failed!'}
                return JsonResponse(msg)
            msg = {'status':'Error!,Try Agin'}
            return JsonResponse(msg)
    return render(request,'met.html')

def current_met_value(request):
    if request.method =='GET':
        num = [0.2,0.3,0,0,0,0,0,0,0,0.35,0.4,0.2,0.3,0.45,-0.45,-0.3,]
        met,created = Coin.objects.get_or_create(name = 'metcoin')
        return JsonResponse({'met':met.value+random.choice(num)})



@login_required
def cap_trading(request):
    trade_ = BuyTrade.objects.filter(user = request.user,sell = False)
    if request.method =="POST":
        account,created = Account.objects.get_or_create(user = request.user)
        data = json.loads(request.body.decode('utf-8'))
        met,created = Coin.objects.get_or_create(name = 'metcoin')
        amount = float(data['amount'])
        if data['status'] =='buy':
            if trade_:
                if account.balance >= amount and amount>0:
                    trade[0].mtc+= amount
                    trade[0].save()
                    msg = {"status":'Success!'}
                    return JsonResponse(msg)
                msg = {"status":'Failed!'}
                return JsonResponse(msg)
            if not account.wallet:
                msg = {'status':'MTC wallet not found for your account'}
                return JsonResponse(msg)
            if account.wallet and account.balance >= amount and amount>0:
                if amount>=5:
                    account.balance-= amount
                    account.save()
                    trade = BuyTrade.objects.create(user = request.user,
                    mtc = amount,mtc_val = met.value,sell = False)
                    trade.save()
                    msg = {"status":'Success!'}
                    return JsonResponse(msg)
                msg = {"status":'Can not Trade less than 5 MTC'}
                return JsonResponse(msg)
            if account.wallet and account.main < amount:
                msg = {"status":'Failed!'}
                return JsonResponse(msg)
            msg = {'status':'Error!,Try Agin'}
            return JsonResponse(msg)

        if data['status'] =='sale':
            if not account.wallet:
                msg = {'status':'MTC wallet not found for your account'}
                return JsonResponse(msg)
            
            if account.wallet and amount>0:
                last_trade = BuyTrade.objects.filter(user=request.user,sell = False).last()
                cap = met.cap_rate*met.value
                profit = met.value - last_trade.mtc_val
                rate = profit/cap
                interest = rate*last_trade.mtc
                # if not profit > 0:
                #     profit = 0.00
                trade = SellTrade.objects.create(user = request.user,
                mtc = last_trade.mtc,profit =interest)
                trade.save()
                last_trade.sell = True
                account.balance += interest+last_trade.mtc
                last_trade.save()
                account.save()
                master_ref = None
                if request.user.profile.referrer:
                    ref = Profile.objects.filter(uid = request.user.profile.referrer)
                    if ref[0].referrer:
                        master_ref = Profile.objects.filter(uid = ref[0].referrer)
                    if not profit <=0:
                        if ref:
                            bonus_1 = functions.get_bonus(1,profit)
                            b_obj = Bonus.objects.create(user = ref[0].user,
                                        level = 1,from_user = request.user,
                                        amount =bonus_1,claimed = False,
                                        action = 'Trading')
                            b_obj.save()
                            if request.user not in ref[0].referrals.all():
                                ref[0].referrals.add(request.user)
                                ref[0].save()
                            if master_ref:
                                bonus_2 = functions.get_bonus(2,profit)
                                b_obj = Bonus.objects.create(user = master_ref[0].user,
                                        level = 2,from_user = request.user,
                                        amount = bonus_2,claimed = False,
                                        action = 'Trading')
                                b_obj.save()
                    msg = {"status":'Success!'}
                    return JsonResponse(msg)
                msg = {"status":'Success!'}
                return JsonResponse(msg)
            
            msg = {'status':'Error!,Try Agin'}
            return JsonResponse(msg)

    context = {
        'trade':trade_
    }
    return render(request,'cap_trading.html',context)


def check_trading(request):
    met,created = Coin.objects.get_or_create(name = 'metcoin')
    last_trade = BuyTrade.objects.filter(user=request.user,sell = False).last()
    if not last_trade:
        cap = met.cap_rate*met.value
        msg = {'amount': 'none','cap':met.cap_rate}
        return JsonResponse(msg)
    cap = met.cap_rate*met.value
    profit = met.value - last_trade.mtc_val
    rate = profit/cap
    interest = rate*last_trade.mtc
    amount_total = last_trade.mtc+interest
    nums = [0.001,0.0011,0.0014,0.00152,0.002,0.008]
    msg = {'amount': amount_total+random.choice(nums),'cap':met.cap_rate,
            'trade_amount':last_trade.mtc}
    return JsonResponse(msg)
    
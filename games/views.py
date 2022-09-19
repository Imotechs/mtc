import random 
from django.shortcuts import render,redirect
from users.models import Account
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import json
from django.contrib import messages
from django.http import HttpResponse
from . import functions
from email import message as MSG
import smtplib
import datetime
import os
from django.template.loader import render_to_string  
from django.contrib.sites.shortcuts import get_current_site  
from django.conf import settings
username = settings.EMAIL_HOST_USER
password= settings.EMAIL_HOST_PASSWORD
# Create your views here.
from .models import FreeGames, Games,AllGames

@login_required
def get_account(request):
    if request.method =='POST':
        account,created = Account.objects.get_or_create(user=request.user)
        data ={
            'main':account.main,       
            'balance':account.balance,       
        }
        return HttpResponse(json.dumps(data), content_type='application/json')

def game_update_account(request,data):
    account,created = Account.objects.get_or_create(user =request.user)
    if str(data['status']) == 'failed':
            if int(data['amount']) <=account.main:
                account.main -=  int(data['amount'])
                account.save()
            pass
    elif str(data['status']) == 'success':
        account.balance += functions.get_game_cent(data['points'],float(data['amount']))
        account.save()

    else:
            pass
def get_game_bonus(request):
    account,created = Account.objects.get_or_create(user =request.user)
    luck =random.choice([0,0.01,0.02,0.03,0.04,0.05])
    account.balance +=  luck
    account.save()
    response = [luck,account.balance]
    return response
     
def game_record(request,data, game_name):
    game,created= AllGames.objects.get_or_create(name = game_name)
    game.players.add(request.user)
    game.save()
    try: 
        if str(data['status']) == 'success':
            profit =functions.get_game_cent(data['points'],int(data['amount'])),
        
            obj = Games.objects.create(
                user = request.user,
                game = game,
                stake = data['amount'],
                profit = profit[0],
                win = True,
                )
            obj.save()
            current_site = get_current_site(request)  
            msg = MSG.EmailMessage()
            message = render_to_string('price_mail.html', {  
                'user': obj.user.username,  
                'domain': current_site.domain, 
                'game':obj,     
            })  
            to_email = obj.user.email   
            msg['To'] =  to_email
            msg['subject'] = 'StakeGames Cash Prize!'
            msg['From'] =f'Stake Games<{username}>'
            msg.set_content(message,subtype='html')
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(username, password)
                try:
                    smtp.send_message(msg)
                except Exception as error:
                    print('error :',error) 
            return game
        elif str(data['status']) == 'failed':
            obj = Games.objects.create(
                user = request.user ,
                game = game,
                stake = data['amount'],
                profit = 0,
                win = False,
                )
            return obj.save()
    except:
        obj = FreeGames.objects.create(
            user = request.user,
            game = game,
            )
        obj.save()
        return obj.save()



'''
Staking Games
'''
def pre_tower(request):
    return render(request,'games/pre_tower.html')

@login_required
def tower(request):
    account,created = Account.objects.get_or_create(user =request.user)
    if account.main==0:
        messages.info(request,'Cant play this game, Your Main Wallet is empty!')
        return redirect('games')
    if request.method =='POST':
        data = json.loads(request.body.decode('utf-8'))
        game_update_account(request,data)
        game = game_record(request,data,'Tower Building')
    return render(request,'games/tower.html')

@login_required
def color_run(request):
    account,created = Account.objects.get_or_create(user =request.user)
    if account.main == 0:
        messages.info(request,'Cant play this game, Your Main Wallet is empty!')
        return redirect('games')
    if request.method =='POST':
        data = json.loads(request.body.decode('utf-8'))
        game_update_account(request,data)
        game = game_record(request,data,'Color Runer')

    return render(request,'games/color.html')


@login_required
def temple_runz(request):
    account,created = Account.objects.get_or_create(user =request.user)
    if account.main == 0:
        messages.info(request,'Cant play this game, Your Main Wallet is empty!')
        return redirect('games')
    if request.method =='POST':
        data = json.loads(request.body.decode('utf-8'))
        game_update_account(request,data)
        game = game_record(request,data,'Temple Runz')
    return render(request,'games/temple_runz.html')

@login_required
def slide_building(request):
    account,created = Account.objects.get_or_create(user =request.user)
    if account.main == 0:
        messages.info(request,'Cant play this game, Your Main Wallet is empty!')
        return redirect('games')
    if request.method =='POST':
        data = json.loads(request.body.decode('utf-8'))
        game_update_account(request,data)
        game = game_record(request,data,'Slide Building')
    return render(request,'games/slide.html')

@login_required
def lottery_game(request):
    account,created = Account.objects.get_or_create(user = request.user)
    num = [ ch for ch in range(999,9999)]
    amount = [i for i in range(1,6)]
    c = (2,3,4,5,6)
    numbers = set(random.sample(num, k=random.choice(c)))
    context = {
        'numbers':numbers,
        'amount':random.choice(amount),
        'account':account,
        'sum':len(numbers),
        'chance':100-(1/len(numbers)*100)
            }
    if account.main <=1:
        messages.info(request,'insufficient wallet balance')
        return redirect('wallet')
    if request.method =='POST':
        prev_numbers =  request.POST.get('numbers')
        choices =  prev_numbers.replace("{","")
        choic = choices.replace("}","")
        ok = choic.split(',')
        if int(account.main) >= int(request.POST['amount']):
            var = int(request.POST['choice'])
            gain = float(request.POST['amount'])*2
            choice =  random.choice(ok)
            if int(var) == int(choice):
                msg = f'You Won!,you guess right!!'
                data = {'amount':request.POST['amount'],'status':'success','points':100-(1/len(ok)*100)}
                game_update_account(request,data)
                game = game_record(request,data,'Charades')
                messages.info(request,msg) 
                return render(request,'games/lottery.html',context)
            else:
                msg = f'Sorry You lose!,The Number should have been {choice} but you choose {var}!'
                data = {'amount':request.POST['amount'],'status':'failed','points':100-(1/len(ok)*100)}
                game_update_account(request,data)
                game = game_record(request,data,'Charades')
                messages.info(request,msg)
                return render(request,'games/lottery.html',context)
        else:
            messages.info(request,'Your Balance is too low')
            return redirect('wallet')

    return render(request,'games/lottery.html',context)
'''
    Demeo Games
'''
def cube(request):
    if request.user.is_authenticated:
        bonus = get_game_bonus(request)
        game= game_record(request,'0','Cube Roll')
        if bonus[0] == 0:
            return render(request,'games/cube.html')
        messages.info(request,f'your account is credited with {bonus[0]*100}C')
        return render(request,'games/cube.html')
    else:
        messages.info(request,f'login to recieve Bonus as you play ')
        return render(request,'games/cube.html')

def racerCar(request):
    if request.user.is_authenticated:
        bonus = get_game_bonus(request)
        game= game_record(request,'0','Master Racing')    
        if bonus[0] == 0:
            return render(request,'games/racer.html') 
        messages.info(request,f'your account is credited with {bonus[0]*100}C')
        messages.info(request,'This game is only played on PC')
        return render(request,'games/racer.html')
    else:
        messages.info(request,f'login to recieve Bonus as you play ')
        return render(request,'games/racer.html')

def birds_killing(request):
    if request.user.is_authenticated:
        bonus = get_game_bonus(request)
        game= game_record(request,'0','Hunter') 
        if bonus[0] == 0:
            return render(request,'games/birds.html')  
        messages.info(request,f'your account is credited with {bonus[0]*100}C')
        return render(request,'games/birds.html')
    else:
        messages.info(request,f'login to recieve Bonus as you play ')
        return render(request,'games/birds.html')

def choicebtn(request):
    return render(request,'games/choicebtn.html')

@login_required
def game1(request):
    account,created = Account.objects.get_or_create(user =request.user)
    if request.method =='POST':
        data = json.loads(request.body.decode('utf-8'))
        game_update_account(request,data)
        game = game_record(request,data,'Number guesing')
    if account.main >0:
        return render(request,'users/gues.html')
    messages.info(request,'Your account is too low to play this game')
    return redirect('profile')
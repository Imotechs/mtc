from django.http import HttpResponse,JsonResponse
import json
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views import View
from mainapp.models import Deposit, UserPayEvidence,Coin
from users.forms import UserRegistrationForm
from users.models import Account, Mail, Profile, Withdraw,Bonus,LockedAsset,Message
from . import functions
from django.db.models import Sum
from django.contrib.sites.shortcuts import get_current_site
import qrcode
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .activating import account_activation_token
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from email import message as MSG
import smtplib
import datetime
from  mainapp import exchange
from django.conf import settings
username = settings.EMAIL_HOST_USER
password= settings.EMAIL_HOST_PASSWORD
# Create your views here.

def register(request,*args,**kwargs):
    if request.method =="POST":

        if User.objects.filter(email = request.POST['email']):
            context = {
                'msg':{"Email":" Email already registered!"},
                'ref':kwargs.get('ref')
            }
            return render(request,'signup.html',context)
        else:
            form = UserRegistrationForm(request.POST)

            if form.is_valid():
                referrer = request.POST.get('ref'),
                if referrer[0] != '':
                    try:
                        ref_user = Profile.objects.get(uid = referrer[0])
                        user_obj = form.save(commit=False)
                        user_obj.is_active = False
                        user_obj.save()
                        obj = Profile(
                        user = User.objects.get(id = user_obj.id),
                        uid = functions.get_user_id(),
                        referrer = ref_user.uid,
                        referred = True,
                        )
                        obj.save()

                        current_site = get_current_site(request)
                        msg = MSG.EmailMessage()
                        mail_subject = 'Verification Stage'
                        message = render_to_string('acc_active_email.html', {
                            'user': user_obj,
                            'domain': current_site.domain,
                            'uid':urlsafe_base64_encode(force_bytes(user_obj.pk)),
                            'token':account_activation_token.make_token(user_obj),
                        })
                        to_email = form.cleaned_data.get('email')
                        email = EmailMessage(
                                    mail_subject, message, to=[to_email]
                        )
                        msg['To'] =  to_email
                        msg['subject'] = 'Verify Your Account'
                        msg['From'] =f'MET Network<{username}>'
                        msg.set_content(message,subtype='html')
                        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                            smtp.login(username, password)
                            try:
                                smtp.send_message(msg)
                            except Exception as error:
                                pass
                            return render(request,'email_sent.html')
                    except Exception as err:
                        context = {
                            'msg':{'Referral':'Invalid Referral Code!'},
                            'ref':kwargs.get('ref')
                                }
                        return render(request,'signup.html',context)
                else:
                    user_obj = form.save(commit=False)
                    user_obj.is_active = False
                    user_obj.save()
                    obj = Profile(
                    user = User.objects.get(id = user_obj.id),
                    uid = functions.get_user_id(),
                    )
                    obj.save()

                    current_site = get_current_site(request)
                    msg = MSG.EmailMessage()
                    mail_subject = 'Activation link has been sent to your email id'
                    message = render_to_string('acc_active_email.html', {
                        'user': user_obj,
                        'domain': current_site.domain,
                        'uid':urlsafe_base64_encode(force_bytes(user_obj.pk)),
                        'token':account_activation_token.make_token(user_obj),
                    })
                    to_email = form.cleaned_data.get('email')
                    msg['To'] =  to_email
                    msg['subject'] = 'Verify Your Account'
                    msg['From'] =f'MET Network<{username}>'
                    msg.set_content(message,subtype='html')
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        smtp.login(username, password)
                        try:
                            smtp.send_message(msg)
                        except Exception as error:
                            pass
                        return render(request,'email_sent.html')

            context = {
                'msg':form.errors,
                'ref':kwargs.get('ref')
                    }
            return render(request,'signup.html',context)
    try:
        context = {
            'ref':kwargs.get('ref')
        }
        return render(request,'signup.html',context)
    except:
         return render(request,'signup.html')


def activate(request, uidb64, token):
    age = [ch for ch in range(14,71)]
    context = {'age':age}
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        refer = Profile.objects.filter(user = user,referred = True,profited = False)
        if refer:
            referrer = Profile.objects.filter(uid = refer[0].referrer)
            refer[0].profited = True
            refer[0].save()
            current_site = get_current_site(request)
            msg = MSG.EmailMessage()
            message = render_to_string('ref_joined.html', {
                'user': referrer[0].user,
                'domain': current_site.domain,
                'ref':user,

            })
            to_email = referrer[0].user.email
            msg['To'] =  to_email
            msg['subject'] = 'User Joined'
            msg['From'] =f'MET Network<{username}>'
            msg.set_content(message,subtype='html')
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(username, password)
                try:
                    smtp.send_message(msg)
                except Exception as error:
                    pass
                return render(request,'re_activate.html',context)
        return render(request,'re_activate.html',context)

    else:
        return HttpResponse ('<h1 style = "color:red;">Activation link Already used or is invalid!</h1>', content_type="text/html")

def login(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request,user)
                messages.info(request,'Great to have you back!')
                return redirect('home')
            else:
                msg = {'msg':'This Account is inactive!'}
                return render(request,'logins.html', {'msg':msg})
        elif user is None:
            context = {'msg':{'Notice':'No account with matching Credentials!'}}

            return render(request,'logins.html', context)

    return render(request,'logins.html')

@login_required
def wallet(request):
    account,created = Account.objects.get_or_create(user = request.user)
    deposit = Deposit.objects.filter(user = request.user,placed = True).order_by('-date')
    withdraws = Withdraw.objects.filter(user = request.user).order_by('-date_placed')
    lock = LockedAsset.objects.filter(user = request.user,claimed = False)
    msg = Message.objects.filter(read = False).order_by('-date')
    locked = None
    if lock:
        locked = lock[0]
    context = {
        'deposit':deposit,
        'withdraws':withdraws,
        'locked':locked,
        'wallet':True,
        'msg':msg,
    }
    return render(request,'mainapp/wallet.html',context)

def met_info(request):
    context ={
        'messagez':Message.objects.filter(read = False).order_by('-date')
    }
    return render(request,'users/met_info.html',context)
def copy_wallet(request,pk):
    wallet = 'TYP5YamBudLsyJ9Q764rU4dCyJAVhPpE2P'
    deposit = Deposit.objects.get(id = pk)
    img = qrcode.make(wallet)
    img.save('media/wallet.png')
    current_site = get_current_site(request)
    context = {
        'wallet_img':'http://'+ current_site.domain + '/media/wallet.png',
        'wallet_str':wallet,
        'deposit':deposit,
    }
    return render(request,'wallet.html',context)




def contact(request):
    if request.method =='POST':
        obj = Mail(
            name = request.POST['name'],
            email = request.POST['email'],
            phone = request.POST['phone'],
            subject = request.POST['subject'],
            message = request.POST['message'],
            )
        obj.save()
        messages.success(request,'Mail Sent!')
        return redirect ('profile')

    return render(request,'mainapp/contact.html')

class WithdrawView(View):
    template_name = 'users/withdraw.html'

    def post(self,*args,**kwargs):
        request = self.request
        account,created= Account.objects.get_or_create(user = request.user)
        if float(request.POST['amount']) <= account.balance:
            if float(request.POST['amount']) >= 15:
                if request.POST['method'] == 'wallet':
                    obj = Withdraw.objects.create(
                        amount = request.POST['amount'],
                        user = request.user,
                        account_number = request.POST['wallet'],
                        account_name = 'TRC20',
                        method = 'Wallet',
                    )
                    obj.save()
                    account.balance -= float(request.POST['amount'])
                    account.save()
                    return redirect('withdraw_success')
                if request.POST['method'] == 'transfer':
                    obj = Withdraw.objects.create(
                        amount = request.POST['amount'],
                        user = request.user,
                        account_number = request.POST['account_number'],
                        account_name = request.POST['account_name'],
                        bank = request.POST['bank'],
                        method = 'Transfer',
                    )
                    obj.save()
                    account.balance -= float(request.POST['amount'])
                    account.save()
                    return redirect('withdraw_success')
            messages.info(request,'Our minimun withdrawal is 15 USD')
            return redirect('wallet')
        messages.info(request,'Your balance is insufficient ')
        return redirect('wallet')

def withdraw_success(request):
    return render(request,'users/withdrawal_success.html')

def uploadEvidence(request):
    if request.method =='POST':
        obj = UserPayEvidence.objects.create(
            evidence = request.FILES['file'],
            user = request.user,
        )
        obj.save()
        messages.success(request,'Uploaded!')
        return redirect('profile')
    return render(request,'users/upload.html')


def setting(request):
    if request.method =='POST':
        try:
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            phone = request.POST['phone']
            country = request.POST['country']
            user = User.objects.get(id = request.user.id)
            user.first_name = first_name
            user.last_name = last_name
            profile = Profile.objects.get(user = request.user)
            profile.phone = phone
            profile.country =country

            user.save()
            profile.save()
            messages.success(request,'Your profile was updated succesfully!')
            return redirect('my_profile')
        except Exception as err:
            return redirect('my_profile')



def testings(request):
    age = [ch for ch in range(14,71)]
    context = {'age':age}
    return render(request,'re_activate.html',context)

@login_required
def game1(request):
    account,created = Account.objects.get_or_create(user =request.user)

    if request.method =='POST':
        data = json.loads(request.body.decode('utf-8'))
        #data = json.loads(data_b)
        print(data)
        if data['status'] == 'failed':
            if int(data['amount']) <=account.main:
                account.main -=  int(data['amount'])
                account.save()
            pass
            #return redirect('game1')
        if data['status'] == 'success':
            account.main += int(data['amount'])*2
            account.save()

    if account.main >0:
        return render(request,'users/game.html')
    messages.info(request,'Your account is too low to play games')
    return redirect('profile')

def advert(request):
    with open(r'C:\Users\ImoTechs\Desktop\StakeGames\mails.txt','r+') as f:
        f.write('adzembehj@gmail.com')
        mails = f.read()
        print(mails)
        mail_list = list(mails)
        to_email = mail_list[0]
        current_site = get_current_site(request)
        msg = MSG.EmailMessage()
        mail_subject = 'Come To StakeGamez'
        message = render_to_string('email_advert.html', {
            'domain': current_site.domain,
        })

        msg['To'] =  to_email
        msg['subject'] = 'Come To StakeGamez'
        msg['From'] = f'Stake Games<{username}>'
        msg.set_content(message,subtype='html')
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(username, password)
            try:
                smtp.send_message(msg)
            except Exception as error:
                pass
    return HttpResponse({'msg':'mail sent'})

@login_required
def make_wallet(request):
    if request.method =='POST':
        account,created = Account.objects.get_or_create(user = request.user)
        wallet = functions.get_wallet()
        if not account.wallet:
            try:
                existing = Account.objects.get(wallet = wallet)
                msg = 'Try again something went wrong!'
                messages.info(request,msg)
                return redirect('trade_met')
            except Exception:
                if account.main >=2:
                    account.wallet = wallet
                    account.main-=2
                    account.save()
                    msg = 'Your Wallet is Created, you can trade now!'
                    messages.info(request,msg)
                    return JsonResponse({'wallet':wallet})
                msg = 'Insuficient USDT Balance!'
                messages.info(request,msg)
                return JsonResponse({'msg':msg})
        msg = 'There is MTC Wallet Attached to your account aready!'
        messages.info(request,msg)
        return JsonResponse({'msg':msg,'wallet':account.wallet})
    return render(request,'users/make_wallet.html')

def check_wallet(request):
    if request.user.account.wallet:
        return HttpResponse(request.user.account.wallet)
    return HttpResponse('No MTC wallet detected!')

def refer(request):
    return render(request,'users/refer.html')

@login_required
def get_account(request):
    if request.method =='POST':
        account,created = Account.objects.get_or_create(user=request.user)
        data ={
            'usdt':round(float(account.main),8),
            'mtc':round(float(account.balance),8),
        }
        return HttpResponse(json.dumps(data), content_type='application/json')

def my_com(request):
    if request.method =='POST':
        id = request.POST['bonus_id']
        bonus = Bonus.objects.get(id = id)
        account,created = Account.objects.get_or_create(user = request.user)
        account.main+= bonus.amount
        account.save()
        bonus.claimed = True
        bonus.save()
        messages.info(request,'Reward Claimed!')
        return redirect('my_com')
    bonus = Bonus.objects.filter(user = request.user).order_by('-date')
    context = {'bonuses':bonus,'com':True}
    return render(request,'users/bonus.html',context)

def lock_assets(request):
    account,created = Account.objects.get_or_create(user = request.user)
    now,then = functions.get_date()
    amount = float(request.POST['amount'])
    if amount < 5:
        messages.info(request,'Amount less than minimum of 5 MTC')
        return redirect('wallet')
    if not account.wallet:
        return redirect('get_wallet')
    if request.method =='POST':
        action = request.POST['action']
        my_lock = LockedAsset.objects.filter(user = request.user,claimed = False)

        if action == 'claim':
            if my_lock:
                master_ref = None
                if request.user.profile.referrer:
                    ref = Profile.objects.filter(uid = request.user.profile.referrer)
                    if ref[0].referrer:
                        master_ref = Profile.objects.filter(uid = ref[0].referrer)
                    profit = functions.locked_bonus(my_lock[0].amount)
                    account.balance+=profit
                    account.save()
                    my_lock[0].profit = profit
                    my_lock[0].claimed = True
                    new_lock = LockedAsset.objects.create(
                    user = request.user,
                    amount = my_lock[0].amount,
                    claimed = False,
                    date = now,
                    date_to = then,
                        )
                    my_lock[0].save()
                    new_lock.save()
                    if not profit <=0:
                        if ref:
                            bonus_1 = functions.get_bonus(1,profit)
                            b_obj = Bonus.objects.create(user = ref[0].user,
                                        level = 1,from_user = request.user,
                                        amount =bonus_1,claimed = False,
                                        action = 'lockUp')
                            b_obj.save()
                            if request.user not in ref[0].referrals.all():
                                ref[0].referrals.add(request.user)
                                ref[0].save()
                            if master_ref:
                                bonus_2 = functions.get_bonus(2,profit)
                                b_obj = Bonus.objects.create(user = master_ref[0].user,
                                        level = 2,from_user = request.user,
                                        amount = bonus_2,claimed = False,action = 'lockUp')
                                b_obj.save()
                    messages.info(request,f'{round(profit,3)}MTC Claimed! ')
                    return redirect('wallet')
                profit = functions.locked_bonus(my_lock[0].amount)
                account.balance+=profit
                account.save()
                my_lock[0].profit = profit
                my_lock[0].claimed = True
                new_lock = LockedAsset.objects.create(
                    user = request.user,
                    amount = my_lock[0].amount,
                    claimed = False,
                    date = now,
                    date_to = then,
                        )
                my_lock[0].save()
                new_lock.save()               
                messages.info(request,f'{round(profit,3)}MTC Claimed! ')
                return redirect('wallet')

        elif action =='lock':
            if my_lock:
                my_lock[0].amount+= amount
                my_lock[0].date_to = then
                my_lock[0].save()
                messages.info(request,'Your assets has been added')
                return redirect('wallet')
            if not account.balance <= amount:
                account.balance-=amount
                new_lock = LockedAsset.objects.create(
                    user = request.user,
                    amount = amount,
                    claimed = False,
                    date = now,
                    date_to = then,
                )
                account.save()
                new_lock.save()
                messages.info(request,'Locked!')
                return redirect('wallet')

            messages.info(request,'Failed!')
            return redirect('wallet')

    return 1
    
@login_required
def convertMTC(request):
    if request.method =='GET':
        return HttpResponse('Method not Allowed')
    account,created = Account.objects.get_or_create(user = request.user)
    mtc,created = Coin.objects.get_or_create(name = 'metcoin')
    if not account.wallet:
        return redirect('get_wallet')
    amount = float(request.POST['amount'])
    action = request.POST['action']
    if action == 'mtc':
        if amount<= account.balance:
            dollar_eq =amount*mtc.value
            account.main+= dollar_eq
            account.balance-= amount
            account.save()
            messages.info(request,'Success')
            return redirect('wallet')
        else:
            messages.info(request,'Total balance Exceeded')
            return redirect('wallet')
    if action == 'usdt':
        if amount <= account.main:
            mtc_eq =amount/mtc.value
            account.main-= amount
            account.balance+= mtc_eq
            account.save()
            messages.info(request,'Success')
            return redirect('wallet')
        else:
            messages.info(request,'Total balance Exceeded')
            return redirect('wallet')
    else:
        return HttpResponse('Method not Allowed')

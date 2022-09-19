from django.http import HttpResponse

import json
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views import View
import mainapp
from mainapp.models import Deposit, UserPayEvidence
from users.forms import UserRegistrationForm
from users.models import Account, Mail, Profile, Withdraw
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
            return render(request,'mainapp/signup.html',context)
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
                        country = request.POST.get('currency'),
                        currency = request.POST.get('currency'),
                        referrer = ref_user.uid,
                        referred = True,
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
                        email = EmailMessage(  
                                    mail_subject, message, to=[to_email]  
                        )  
                        msg['To'] =  to_email
                        msg['subject'] = 'StakeGames Email Verification'
                        msg['From'] =f'Stake Games<{username}>'
                        msg.set_content(message,subtype='html')
                        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                            smtp.login(username, password)
                            try:
                                smtp.send_message(msg)
                            except Exception as error:
                                print('error :',error)                  
                            return render(request,'email_sent.html') 
                    except Exception as err:
                        print('error:',err)
                        context = {
                            'msg':{'Referral':'Invalid Referral Code!'},
                            'ref':kwargs.get('ref')
                                }
                        return render(request,'signup.html',context)
                else:
                    user_obj = form.save()
                    user_obj = form.save(commit=False)
                    user_obj.is_active = False
                    user_obj.save()
                    obj = Profile(
                    user = User.objects.get(id = user_obj.id), 
                    uid = functions.get_user_id(),
                    currency = request.POST.get('currency'),
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
                    msg['subject'] = 'StakeGames Email Verification'
                    msg['From'] =f'Stake Games<{username}>'
                    msg.set_content(message,subtype='html')
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        smtp.login(username, password)
                        try:
                            smtp.send_message(msg)
                        except Exception as error:
                            print('error :',error)                  
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
            referrer_account,created = Account.objects.get_or_create(user = referrer[0].user)
            referrer_account.balance += 1
            referrer_account.save() 
            refer[0].profited = True
            refer[0].save()
            current_site = get_current_site(request)  
            msg = MSG.EmailMessage()
            mail_subject = 'Activation link has been sent to your email id'  
            message = render_to_string('bonus.html', {  
                'user': referrer[0].user,  
                'domain': current_site.domain, 
                'ref':user,
               
            })  
            to_email = referrer[0].user.email   
            msg['To'] =  to_email
            msg['subject'] = 'StakeGames Referral Bonus'
            msg['From'] =f'StakeGames<{username}>'
            msg.set_content(message,subtype='html')
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(username, password)
                try:
                    smtp.send_message(msg)
                except Exception as error:
                    pass
                return redirect('login') 
        return redirect('login') 

    else:  
        return HttpResponse ('Activation link is invalid!', content_type="text/plain")  

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
                msg = {'msg':'Your Account is not activated!'}
                return render(request,'login.html', {'msg':msg})
        elif user is None:
            context = {'msg':{'Notice':'Error in Login Credentials!'}}
                
            return render(request,'login.html', context)
        
    return render(request,'login.html')

@login_required
def wallet(request):
    account,created = Account.objects.get_or_create(user = request.user)
    deposit = Deposit.objects.filter(user = request.user,placed = True).order_by('-date')  
    withdraws = Withdraw.objects.filter(user = request.user).order_by('-date_placed')  
    context = {
        'deposit':deposit,
        'withdraws':withdraws,
    }
    return render(request,'mainapp/wallet.html',context)
       

def copy_wallet(request,pk):
    wallet = 'ertaswdertgcvewsawq123rtgvbt5453ed'
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



def my_profile(request):

    return render(request,'users/profile.html')

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

from django.shortcuts import render,redirect
from django.views.generic import TemplateView,ListView,CreateView,DetailView,DeleteView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.contrib.auth.models import User
from mainapp.models import  UserPayEvidence,Deposit,Coin
from users.models import Profile,Withdraw,Mail,Account
from django.db.models import Sum
from django.contrib import messages
from users import functions
from django.utils import timezone
from email.message import EmailMessage
import smtplib
import json
from django.conf import settings
from users.models import Account,Message
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from mainapp.models import Lottery,Bid
from django.conf import settings
username = settings.EMAIL_HOST_USER
password = settings.EMAIL_HOST_PASSWORD
# Create your views here.

class Dashboard(LoginRequiredMixin,UserPassesTestMixin,TemplateView):
  model = User
  template_name = 'dashboard/index.html'

  def get_context_data(self, *args, **kwargs):
    context =super(Dashboard,self).get_context_data( *args, **kwargs)
    met,created = Coin.objects.get_or_create(name = 'metcoin')
    users =  User.objects.all().order_by('-date_joined')
    Tdeposits = Deposit.objects.filter(approved =True).aggregate(sum = Sum('amount'))
    deposits = Deposit.objects.filter(approved =True).order_by('-date_approved')
    withdraws = Withdraw.objects.filter(approved =True).aggregate(sum = Sum('amount'))
    admins =  User.objects.filter(is_superuser = True).order_by('-date_joined')
    staffs =  User.objects.filter(is_staff = True).order_by('-date_joined')
    mails = Mail.objects.filter(seen= False)
    account_main = Account.objects.all().aggregate(sum = Sum('main'))
    account_balance = Account.objects.all().aggregate(sum = Sum('balance'))
    context.update({'Tdeposits':Tdeposits,'users':users,
    'withdraws':withdraws,'deposits':deposits, 'mails':mails,
    'staffs':staffs, 'admins':admins,
    'account_main':account_main,'account_balance':account_balance,
    'met':met})
    return context
  def test_func(self):
    if self.request.user.is_superuser or self.request.user.is_staff:
      return True
    return False

class deposit(TemplateView):
    deposits =  Deposit.objects.filter(approved=True,cancel=False).order_by('-date_approved')
    withdraws =  Withdraw.objects.filter(approved=True,cancel=False).order_by('-date_approved')



class AllUsers(UserPassesTestMixin,ListView ):
    model = User
    template_name = 'dashboard/reg-users.html'
    paginate_by = 5
    context_object_name = 'users'
    ordering = ['-date_joined']
    def get_context_data(self, *args,**kwargs: any):
        context = super(AllUsers,self).get_context_data(*args,**kwargs)
        mails = Mail.objects.filter(seen= False)
        context.update({ 'mails':mails})
        return context
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


class AllDeposit(UserPassesTestMixin,ListView ):
    model = Deposit
    template_name = 'dashboard/deposits.html'
    paginate_by = 10
    def get_context_data(self, *args,**kwargs: any):
        context = super(AllDeposit,self).get_context_data(*args,**kwargs)
        deposits = Deposit.objects.filter(approved= False, cancel = False,placed = False).order_by('-date')
        pdeposits = Deposit.objects.filter(approved= False, cancel = False,placed = True).order_by('-date')
        context.update({ 'deposits':deposits,'pdeposits':pdeposits})
        return context
    def post(self,request,*args, **kwargs):
        if request.method =='POST':

            try:
                id = request.POST['approve']
                deposit = Deposit.objects.get(id = int(id))
                obj,created = Account.objects.get_or_create(user = deposit.user)
                obj.main +=  deposit.amount
                obj.save()
                deposit.approved = True
                deposit.date_approved = timezone.now()
                deposit.save()
                current_site = get_current_site(request)
                msg = EmailMessage()
                message = render_to_string('deposit_mail.html', {
                    'user': deposit.user,
                    'domain': current_site.domain,
                    'deposit':deposit,

                })
                to_email = deposit.user.email
                msg['To'] =  to_email
                msg['subject'] = 'Deposit Approved'
                msg['From'] =f'MET<{username}>'
                msg.set_content(message,subtype='html')
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(username, password)
                    try:
                        smtp.send_message(msg)
                    except Exception as error:
                        pass
                    messages.info(request,'Approved!')
                    return redirect('deposits')

            except Exception as err:
                id = request.POST['cancel']
                deposit = Deposit.objects.get(id = int(id))
                deposit.cancel = True
                deposit.date_approved = timezone.now()
                deposit.save()
                messages.info(request,'Canceled!')
                return redirect('deposits')

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False
    
class MessageView(UserPassesTestMixin,ListView):
    model = Message
    template_name = 'dashboard/messagez.html'
    paginate_by = 10
    def get_context_data(self, *args,**kwargs: any):
        context = super(MessageView,self).get_context_data(*args,**kwargs)
        messages = Message.objects.filter(read= False).order_by('-date')
        context.update({ 'messages':messages,})
        return context
    def post(self,request,*args, **kwargs):
        if request.method =='POST':
            id = request.POST['approve']
            msg = Message.objects.get(id = int(id))
            msg.read = True
            msg.save()
            return redirect('message')
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False
    
class MessageCompose(UserPassesTestMixin,ListView):
    model = Message
    template_name = 'dashboard/message_compose.html'
    def post(self,request,*args, **kwargs):
        if request.method =='POST':
            subject = request.POST['subject']
            url = request.POST['url']
            body = request.POST['body']
            msg = Message.objects.create(subject = subject,body = body, url = url)
            msg.save()
            return redirect('message')
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False

class AllWithdraws(UserPassesTestMixin,ListView ):
    model = Deposit
    template_name = 'dashboard/withdrawals.html'
    paginate_by = 10
    def get_context_data(self, *args,**kwargs: any):
        context = super(AllWithdraws,self).get_context_data(*args,**kwargs)
        withdraws = Withdraw.objects.filter(approved= False, cancel = False)
        context.update({ 'withdraws':withdraws})
        return context
    def post(self,request,*args, **kwargs):
        if request.method =='POST':
            try:
                id = request.POST['approve']
                withdraw = Withdraw.objects.get(id = int(id))
                obj,created = Account.objects.get_or_create(user = withdraw.user)
                obj.balance -= withdraw.amount
                obj.save()
                withdraw.approved = True
                withdraw.date_approved = timezone.now()
                withdraw.save()
                current_site = get_current_site(request)
                msg = EmailMessage()
                message = render_to_string('withdraw_mail.html', {
                    'user': withdraw.user,
                    'domain': current_site.domain,
                    'withdraw':withdraw,

                })
                to_email = withdraw.user.email
                msg['To'] =  to_email
                msg['subject'] = 'Withdrawal Approved'
                msg['From'] =f'MET<{username}>'
                msg.set_content(message,subtype='html')
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(username, password)
                    try:
                        smtp.send_message(msg)
                    except Exception as error:
                        pass
                    messages.info(request,'Approved!')
                    return redirect('withdraws')

            except Exception:
                id = request.POST['cancel']
                withdraw = Withdraw.objects.get(id = int(id))
                withdraw.cancel = True
                withdraw.date_approved = timezone.now()
                withdraw.save()
                obj,created = Account.objects.get_or_create(user = withdraw.user)
                obj.balance += withdraw.amount
                obj.save()
                messages.info(request,'Canceled!')
                return redirect('withdraws')

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False

class Emails(UserPassesTestMixin,ListView ):
    model = Mail
    template_name = 'dashboard/email-inbox.html'
    def get_context_data(self, *args,**kwargs: any):
        context = super(Emails,self).get_context_data(*args,**kwargs)
        mails = Mail.objects.filter(seen = False).order_by('-id')
        context.update({'mails':mails})
        return context
    def post(self,request,*args, **kwargs):
        if request.method =='POST':
            try:
                id = request.POST['mail']
                mail = Mail.objects.get(id = int(id))
                mail.seen = True
                mail.save()
                return redirect('mails')
            except Exception:
                return redirect('mails')
    def test_func(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return True
        return False

class ViewEmails(UserPassesTestMixin,DetailView):
    model = Mail
    template_name = 'dashboard/email-read.html'


    def test_func(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return True
        return False



class MakeMail(UserPassesTestMixin,TemplateView ):
    model = Mail
    template_name = 'dashboard/email-compose.html'
    def post(self,request,*args, **kwargs):
        if request.method =='POST':
            try:
                email = request.POST['email']
                subject =request.POST['subject']
                body =request.POST['message']
                msg = EmailMessage()
                msg['To'] = email
                msg['subject'] = subject
                msg['From'] =f'no-reply<{username}>'
                msg.set_content(body)
                try:
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        smtp.login(username, password)
                        smtp.send_message(msg)
                        messages.success(request,'Mail Sent Succesfully!')
                        return redirect('sendmails')
                except Exception as error:
                    messages.info(request, f'Error : {error}')
                    return redirect('sendmails')

            except Exception as err:
                print('there is errrrro: ',err)
                return redirect('mails')
    def test_func(self):
        if self.request.user.is_superuser  or self.request.user.is_staff:
            return True
        return False


class AdminUploadView(UserPassesTestMixin,ListView):
    model = UserPayEvidence
    template_name = 'dashboard/evidence.html'
    context_object_name = 'uploads'
    paginate_by = 2
    ordering = ['-date_upload']

    def test_func(self):
        if self.request.user.is_superuser  or self.request.user.is_staff:
            return True
        return False

class WinGames(UserPassesTestMixin,ListView):
    context_object_name = 'win_games'
    ordering = ['-date']
    paginate_by = 5
    template_name = 'dashboard/win.html'
    def test_func(self):
        if self.request.user.is_superuser  or self.request.user.is_staff:
            return True
        return False




#lottery system
class LotteryView(LoginRequiredMixin,UserPassesTestMixin,ListView):
    template_name = 'dashboard/lottery.html'
    model = Lottery
    def get_context_data(self,*args, **kwargs):
        context = super(LotteryView,self).get_context_data(*args,**kwargs)
        lottery = Lottery.objects.filter(win = False).last()
        context.update({'bids':lottery.bid_set.all()})
        return context
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False



def change_met(request):
    if request.user.is_authenticated and request.user.is_superuser:
        met,created = Coin.objects.get_or_create(name = 'metcoin')
        if request.method=='POST':
            data = json.loads(request.body.decode('utf-8'))
            if data['status'] =='cap':
                met.cap_rate = float(data['cap'])
                met.save()
                return JsonResponse({'met':round(met.value,3)})

            amount = float(data['amount'])
            met.value+= amount
            met.save()
            return JsonResponse({'met':round(met.value,3)})

        inc_ = [0.10,0.20,0.30,0.40,0.50,0.60,0.70,0.80,0.90,1.00]
        dec_ = [-0.1,-0.2,-0.3,-0.4,-0.5,-0.6,-0.7,-0.8,-0.9,-1.0]
        cap = [5,6,7,8,9,10]
        context = {
            'current':met.value,
            'ups':inc_,
            'downs':dec_,
            'cap':cap,
        }
        return render(request,'signal.html',context)
    return redirect('home')




from django.conf import settings
from mainapp.models import Deposit
from users.models import Account
from django.views.generic import TemplateView,View
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.contrib import messages
from users import functions
from users.models import Account
from mainapp import exchange
from django.contrib.sites.shortcuts import get_current_site 
import qrcode
def completed(request,*args,**kwargs):
  pk =kwargs.get('pk')
  method = kwargs.get('ref')
  obj = Deposit.objects.filter(id = pk,approved = False,cancel = False)
  if obj:
    obj[0].method = method
    obj[0].placed = True
    obj[0].save()
    messages.info(request,'Your account will be credited once your payment is confirmed')
    return redirect('wallet')
  else:
    return redirect('wallet')
@login_required
def payment_checkout(request):
    txn_id = functions.get_payment_id(f'{request.user.username[:3]}')
    if request.method =='POST':
        currency = request.user.profile.currency
        if currency is not None and currency != 'USD':
            usd = exchange.convert_currency(currency,request.POST['amount'])
            if usd is not None:
                obj = Deposit(user = request.user,
                        transaction_id = txn_id,
                        approved = False, 
                        amount = request.POST['amount'],
                        usd = usd,
                        )
                obj.save()
                return redirect('payment',int(obj.id))
            messages.info(request,'Failed to convert local currency')
            return redirect('wallet')
          
        elif currency == 'USD':
            obj = Deposit(user = request.user,
                        transaction_id = txn_id,
                        approved = False, 
                        amount = request.POST['amount'],
                        usd = request.POST['amount'],
                        )
            obj.save()
            return redirect('payment',int(obj.id))
        messages.info(request,"Failed to identify User's local currency")
        return redirect('wallet')

class PaymentView(TemplateView):
    template_name = 'mainapp/payment.html'

    def get_context_data(self, **kwargs: any):
      payment_id =self.kwargs['pk']
      user = self.request.user
      wallet = 'ertaswdertgcvewsawq123rtgvbt5453ed'
      img = qrcode.make(wallet)
      img.save('media/wallet.png')
      current_site = get_current_site(self.request)  
      payment = Deposit.objects.filter(id = payment_id)
      context = super(PaymentView,self).get_context_data(**kwargs)
      context.update({
            'wallet_qr':'http://'+ current_site.domain + '/media/wallet.png',
            'wallet_str':wallet,
            'user':user,
            'payment':payment[0],
            'PAYSTACK_PUBLICK_KEYS':settings.PAYSTACK_PUBLICK_KEYS,
        })
      return context


class PaymentSuccess(View):       
  def get(self,request,*args, **kwargs):
    if request.method == 'GET':
      ref = kwargs['ref']
      obj = Deposit.objects.get(user =request.user,
                                  transaction_id = ref,
              approved = False,cancel = False,)
      verified = obj.verify_payment()
      if verified:
        user = request.user
        account,created = Account.objects.get_or_create(user = user)
        account.main += obj.usd
        account.save()
        messages.success(request,'Varification succesfull')
        return render(request,'mainapp/payment_success.html')
      else:
          messages.success(request,'Varification failed!!!')
          return redirect('wallet')



 
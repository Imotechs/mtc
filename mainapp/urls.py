
from django.urls import path,include,reverse_lazy
from .views import (home,testimonial,terms,about,
                    subscribe,games,contact,
                    lottery,tournaments,
                    current_met_value,trade_met,policy,
                    trademore,cap_trading,check_trading
)
import users.views as user_views
from django.contrib.auth import views as auth_views
from .payment import PaymentSuccess,payment_checkout,PaymentView,completed
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', home, name = 'home'),
    path('subscrbe/our/mails/',subscribe,name = 'sub'),
    path('our/privacy/policies/', terms, name = 'terms'),
    path('about/us/',about, name = 'about'),
    path('privacy/policy/',policy, name = 'policy'),
    path('contact/us/',contact, name = 'contact'),
    path('testimonials/',testimonial, name = 'testimonials'),
    path('met/info/',user_views.met_info,name = 'met_info'),
    path('lottery/',lottery,name = 'lot'),
    path('tournaments/',tournaments,name = 'turn'),
    path('trade/inst/',trademore,name='trademore'),
    #met coin
    path('access/met/value/',current_met_value,name = 'get_met_value'),
    path('trading/met/',trade_met,name = 'cap_trade'),
    path('trading/mtc/', cap_trading,name = 'trade_met'),
    path('checking/', check_trading),
    #accounts
    path('accounts/sign_up/', user_views.register,name ='register'),
    path('accounts/sign_up/<str:ref>/', user_views.register),
    path('accounts/login/', user_views.login,name ='login'),
    path('account/activate/<uidb64>/<token>/',user_views.activate, name = 'activate'),

    #payments
    path('checkout/',payment_checkout, name = 'checkout'),
    path('make/payment/<int:pk>/',PaymentView.as_view(), name = 'payment'),
    path('payment/success/<str:ref>/',PaymentSuccess.as_view(), name = 'paymentsuccess'),
    path('completed/<str:ref>/<int:pk>/',completed, name = 'completed')
]
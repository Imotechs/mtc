from django.urls import path
from django.views import View
from .views import (Dashboard,AllUsers,AllDeposit,AllWithdraws,
MakeMail,Emails,change_met,AdminUploadView,ViewEmails,WinGames,
LotteryView,MessageView,MessageCompose

)
urlpatterns = [
    path('main/', Dashboard.as_view(), name='dashboard'),
    # path('staffs/', Staffs.as_view(), name = 'staffs'),   
    path('all/users/', AllUsers.as_view(), name = 'allusers'),
    path('current/deposits/', AllDeposit.as_view(), name = 'deposits'),
    path('current/withdrawals/', AllWithdraws.as_view(), name = 'withdraws'),
    path('all/mails/', Emails.as_view(), name = 'mails'),
    path('send/mails/', MakeMail.as_view(), name = 'sendmails'),
    path('view/<int:pk>/mails/', ViewEmails.as_view(), name = 'readmail'),
    path('uploads/views/', AdminUploadView.as_view(), name = 'evidenceview'),
    path('win/games/',WinGames.as_view(),name = 'win_games'),
    path('lost/games/',WinGames.as_view(template_name = 'dashboard/lost.html'),name = 'lost_games'),
    
    path('lottery/bids/',LotteryView.as_view(),name = 'bids'),
    path('met/ch/val/', change_met,name = 'change_met'),
    path('see/msg/',MessageView.as_view(), name = 'message'),
    path('compose/msg/',MessageCompose.as_view(), name = 'make_message'),

]

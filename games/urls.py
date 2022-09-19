
from django.urls import path
from .views import (tower,racerCar,
choicebtn,color_run,
get_account,temple_runz,slide_building,cube,pre_tower,
birds_killing,lottery_game
)

urlpatterns = [
path('tower/',pre_tower,name = 'pre_tower'),
path('tower/building/',tower, name = 'tower'),
path('color/run/',color_run,name = 'color_run'),
path('temple/runz/',temple_runz, name = 'temple_runz'),
path('slide/building/',slide_building, name = 'slider'),
path('lottery/game/',lottery_game, name = 'charades'),
# User account
path('user/account/',get_account, name ='user_account'),
#Demo Games
path('racer/car/',racerCar, name = 'racer'),
path('rand/num/choices/',choicebtn,name = 'choicebtn'),
path('cube/master/',cube,name = 'cube'),
path('birds/killing/',birds_killing, name = 'bird_killer'),

]

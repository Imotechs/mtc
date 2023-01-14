import datetime
import random
import json
def get_date():
    now = datetime.datetime.now()
    nday = datetime.timedelta(days = 1)
    due_time = now + nday
    return now, due_time


def get_percentage(amount,percent):
    percentage = percent/100
    try:
        interest = int(amount)*percentage
        return interest
    except Exception as er:
        return None


def make_new_deposit():
    now = datetime.datetime.now()
    time_str = ''.join(ch for ch in str(now) if ch.isalnum())
    num1 = time_str[3:8]
    num2 = time_str[8:17]
    return f'{num2}{num1}GT'


def get_game_time():
    now = datetime.datetime.now()
    nday = datetime.timedelta(minutes= 1)
    due_time = now + nday

    return due_time
    
def get_user_id():
    now = datetime.datetime.now()
    time_str = ''.join(ch for ch in str(now) if ch.isalnum())
    num1 = time_str[5:8]
    num2 = time_str[8:15]
    return f'{num2}{num1}'

def get_rand_user():
    num = [250,600,700,200,320,300,710,201,312,]
    return random.choice(num)

def get_referrer_percentage(amount):
    percentage = 0.005
    try:
        interest = int(amount)*percentage
        return interest
    except Exception as er:
        return er


def  get_payment_id(item):

    ctime = datetime.datetime.now()
    mtime = str(ctime.today())
    newtime = ''.join(ch for ch in mtime if ch.isalnum())
    year = newtime[0:4]
    month_day = newtime[5:14]
   
    my_id = f'{item}-{year}-{str(month_day)}'
  
    return my_id

   
def get_wallet():
    wallet =''
    alpha = ['T','X','y','B','c','b','k','L','P','z','F','f','h','H','O','o','N','R','s','V','0','1','2','3','4','5','6','7','8','9']
    while len(wallet)<27:
         wallet+= random.choice(alpha)
    wallet = 'MTC'+wallet
    return wallet

def get_bonus(type,profit):
    if type ==1:
        return 0.035*profit
    elif type ==2:
        return 0.017*profit

def locked_bonus(amount):
    bonus = [0.05,0.06,0.07,0.08,0.09,0.10]
    return amount*random.choice(bonus)
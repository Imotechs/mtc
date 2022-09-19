import datetime
import random

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
    print(due_time)

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
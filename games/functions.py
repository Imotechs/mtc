def get_game_cent(points,amount):
    try:
        percent = points/100
        money = abs(amount*percent)
    except:
        money = amount
    return money
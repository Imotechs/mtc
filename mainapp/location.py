import requests
access_key = 'f89a0a3f2b760d78adbeb8b13277a906'
bas_url = 'http://api.ipstack.com/'

# {
#   "success": false,
#   "error": {
#     "code": 104,
#     "type": "monthly_limit_reached",
#     "info": "Your monthly API request volume has been reached. Please upgrade your plan."
#   }
# }

def get_client_location(ip):
    url = f'http://api.ipstack.com/{ip}?access_key={access_key}'
    response = requests.get(url)
    result = response.json()

    return result

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



def get_client_locations(ip):
    YOUR_ACCESS_KEY = ''
    url = f'https://api.ipapi.com/api/{ip}?access_key={YOUR_ACCESS_KEY}'
    response = requests.get(url)
    result = response.json()

    return result

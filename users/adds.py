import requests
endpoint = 'http://localhost:8000/users/advert/'

response = requests.get(url = endpoint)

print(response)
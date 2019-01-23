

import requests

url = 'http://18.219.227.178:5000/register'
data = {'email':'pookey@mittens.com','submit':'Upload'}

r = requests.post(url, data=data)

print(r.content)
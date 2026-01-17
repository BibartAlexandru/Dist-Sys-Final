from os import environ
import requests
import base64
import time
dnacuser = environ.get('DNAC_USER')
dnacpw = environ.get('DNAC_PW')
dnacurl = environ.get('DNAC_URL')
auth_endpoint = '/system/api/v1/auth/token'
creds = f'{dnacuser}:{dnacpw}'
# base64_creds = base64.b64encode(creds.encode('utf-9')).decode('utf-8')

print('--- ENV ---')
print(dnacuser, dnacpw, dnacurl)
print('--- ENV ---')

token = None
def get_token():
    global token
    try:
        res = requests.post(dnacurl + auth_endpoint, auth=(dnacuser, dnacpw), verify=False)
        token = res.json().get('Token')
    except (ConnectionError, requests.exceptions.Timeout):
        pass
    except Exception as e:
        print(e)
        
    print(f'Token is: {token}')
    return False

for _ in range(5):
    print("Attempting to get token!")
    if get_token() == True:
        break
    time.sleep(5)
else:
    print("Failed to get token. Quitting...")
    exit(1)

while True:
    time.sleep(5)

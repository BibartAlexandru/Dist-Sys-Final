from os import environ
import requests
import time
dnacuser = environ.get('DNAC_USER')
dnacpw = environ.get('DNAC_PW')
dnacurl = environ.get('DNAC_URL')
auth_endpoint = '/system/api/v1/auth/token'
REQ_TIMEOUT = 10 # seconds

print('--- ENV ---')
print(dnacuser, dnacpw, dnacurl)
print('---+++++---')

token = None
def get_token():
    global token
    try:
        res = requests.post(dnacurl + auth_endpoint, auth=(dnacuser, dnacpw), verify=False, timeout=REQ_TIMEOUT)
        token = res.json().get('Token')
        print(f'Token is: {token}')
        return True
    except (ConnectionError, requests.exceptions.Timeout):
        print('some err')
        return False
    except Exception as e:
        print(e)
        return False

def try_get_token():
    for _ in range(5):
        print("Attempting to get token!")
        if get_token() == True:
            break
        print("Failed to get token. Retrying...")
        time.sleep(5)
    else:
        print("Failed to get token. Quitting...")
        exit(1)

def get_configs():
    pass

def save_configs():
    pass

def diff_configs():
    pass

def commit_if_diffs_exist():
    pass

def main():
    try_get_token()
    get_configs()
    save_configs()
    diff_configs()
    commit_if_diffs_exist()

main()
while True:
    time.sleep(5)

from os import environ
import requests
import time
from pydantic import BaseModel
from devtools import pprint
import subprocess
from datetime import datetime

DNACUSER = environ.get('DNAC_USER')
DNACPW = environ.get('DNAC_PW')
DNACURL = environ.get('DNAC_URL')
AUTH_ENDPOINT = '/system/api/v1/auth/token'
NETW_DEV_CONFS_ENDPOINT = '/intent/api/v1/networkDeviceConfigFiles'
NETW_DEV_ENDPOINT = '/intent/api/v1/network-device'
REQ_TIMEOUT = 10 # seconds
CONFIGS_DIR = '/configs_dir'

class NetworkDeviceConfigData(BaseModel):
    netw_dev_id: str
    hostname: str
    config: str

# ------- GLOBAL VARS ----------
confs_data: list[NetworkDeviceConfigData] = []
token = None
# ------- GLOBAL VARS ----------

print('--- ENV ---')
print(DNACUSER, DNACPW, DNACURL)
print('---+++++---')

def get_token():
    global token
    try:
        res = requests.post(DNACURL + AUTH_ENDPOINT, auth=(DNACUSER, DNACPW), verify=False, timeout=REQ_TIMEOUT)
        token = res.json().get('Token')
        print('------------------')
        print(f'Token is: {token}')
        print('------------------')
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

def get_download_dev_conf_endpoint(conf_id: str) -> str:
    global DNACURL
    global NETW_DEV_CONFS_ENDPOINT
    return f'{DNACURL}{NETW_DEV_CONFS_ENDPOINT}/{conf_id}/downloadMasked'

def get_configs():
    global confs_data
    confs_data = []

    headers = {
        "X-Auth-Token": token, 
        "Content-Type": 'application/json'
    }
    try:
        res = requests.get(DNACURL + NETW_DEV_CONFS_ENDPOINT, verify=False, timeout=REQ_TIMEOUT, headers=headers)
        configs_metadata = res.json().get('response')
        if configs_metadata is None:
            print("No configs! Aborting...")
            exit(1)
        # For some reason, some devices retrieve the startup and running config, but I couldn't find an API endpoint that retrieves the startup configs
        configs_metadata = list(filter(lambda conf: conf['fileType'] == 'RUNNINGCONFIG', configs_metadata))
        if len(configs_metadata) == 0:
            print("No running configs! Have a good day!")
            return
        for config_metadata in configs_metadata:
            netw_dev_id = config_metadata.get('networkDeviceId')
            #print(f'ID: {netw_dev_id}')
            res = requests.get(f'{DNACURL}{NETW_DEV_ENDPOINT}/{netw_dev_id}', headers=headers, verify=False)
            netw_dev_info = res.json().get('response')

            endpoint = get_download_dev_conf_endpoint(config_metadata['id'])
            #print(f"Querying: {endpoint}!")
            res = requests.post(endpoint, headers=headers, verify=False)
            config = res.text
            confs_data.append(
            NetworkDeviceConfigData(
                netw_dev_id=netw_dev_id,
                hostname=netw_dev_info.get('hostname'),
                config=config
            ))

    except (ConnectionError, requests.exceptions.Timeout):
        print('some err')
        exit(1)
    except Exception as e:
        print(e)
        exit(1)

def save_configs():
    for confd in confs_data:
        # pprint(confd)
        with open(f'{CONFIGS_DIR}/{confd.hostname}_{confd.netw_dev_id}_running.conf', 'w') as fout:
            fout.writelines(confd.config)

def is_different_from_last_commit() -> bool:
    new_files = False
    diffs_exist = False
    cmd = '''
    . /app/.env && \
    cd /app/${GITHUB_REPO} && \
    git pull && \
    cp /configs_dir/* ./
    '''
    r = subprocess.run(
            cmd,
            capture_output=True,
            text=True, 
            shell=True,
            executable="/bin/bash"
            )
    if r.returncode != 0:
        print(f'{cmd} returned: {r.returncode}. STDERR: {r.stderr}')
        exit(1)
    # Untracked files => new configs
    cmd = '''
    . /app/.env && \
    cd /app/${GITHUB_REPO} && \
    git ls-files --others --exclude-standard | wc -l
    '''
    r = subprocess.run(
            cmd,
            capture_output=True,
            text=True, 
            shell=True,
            executable="/bin/bash"
            )
    if r.returncode != 0:
        print(f'{cmd} returned: {r.returncode}. STDERR: {r.stderr}')
        exit(1)

    nr_files = int(r.stdout.strip())
    if nr_files > 0:
        new_files = True
        print(r.stdout.strip())

    cmd = '''
    . /app/.env && \
    cd /app/${GITHUB_REPO} && \
    git add .
    '''
    r = subprocess.run(
            cmd,
            capture_output=True,
            text=True, 
            shell=True,
            executable="/bin/bash"
            )
    if r.returncode != 0:
        print(f'{cmd} returned: {r.returncode}. STDERR: {r.stderr}')
        exit(1)

    cmd = '''
    . /app/.env && \
    cd /app/${GITHUB_REPO} && \
    git diff --staged
    '''
    r = subprocess.run(
            cmd,
            capture_output=True,
            text=True, 
            shell=True,
            executable="/bin/bash"
            )
    if len(r.stdout.strip()) > 0:
        diffs_exist = True
        print(r.stdout.strip())
    print(f'New Files: {new_files}\nDiffs Exist: {diffs_exist}')
    return new_files or diffs_exist

def commit_diff():
    print(f'[{datetime.now()}] Config change detected. Committing !!!')
    cmd = '''
    . /app/.env && \
    cd /app/${GITHUB_REPO} && \
    git commit -m "Config Change on: ''' + str(datetime.now()) + '''"
    git push origin main
    '''
    r = subprocess.run(
            cmd,
            capture_output=True,
            text=True, 
            shell=True,
            executable="/bin/bash"
            )
    if r.returncode != 0:
        print(f'{cmd} returned: {r.returncode}. STDERR: {r.stderr}')
        exit(1)

def main():
    try_get_token()
    get_configs()
    save_configs()
    if is_different_from_last_commit():
        commit_diff()

main()
while True:
    # Basically once a day. Cron would be better than this loop, but it is what it is...
    time.sleep(60 * 60 * 24)

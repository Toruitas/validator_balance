import os
import requests
import time
import math

SECONDS_PER_SLOT = 12
SLOTS_PER_EPOCH = 32
GWEI_PER_ETH = 1000000000
ETH1_NETWORK = "goerli"
ETH2_NETWORK = "medalla"
INFURA_PROJECT_ID = os.environ.get('INFURA_PROJECT_ID')
INFURA_ETH1_BASE_URL = f"https://{ETH1_NETWORK}.infura.io/v3/{INFURA_PROJECT_ID}"
INFURA_ETH2_BASE_URL = f"https://{ETH2_NETWORK}.infura.io/v1"
INFURA_SECRET = os.environ.get('INFURA_SECRET')

# JSON RPC used for ETH1
JSON_RPC = {
    'jsonrpc':'2.0',
    'method':'',  # change later
    'params':[],  # must give, even if blank
    'id':INFURA_PROJECT_ID,
    }

# response = requests.post(INFURA_BASE_URL, auth=("", INFURA_SECRET))

# while True:
# JSON_RPC['method'] = 'eth_blockNumber'
# check_epoch = requests.post(INFURA_ETH1_BASE_URL, json=JSON_RPC, auth=("", INFURA_SECRET))
# genesis_time = check_epoch.json()


beacon = requests.get(INFURA_ETH2_BASE_URL+'/eth/v1/beacon/genesis', auth=(INFURA_PROJECT_ID, INFURA_SECRET))
print(beacon.text)

# right_now = time.time()
# current_epoch = math.floor((now - ))
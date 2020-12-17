import os
import requests
import time
import math
from datetime import datetime, date
from signal import signal, SIGINT
from sys import exit

import pandas as pd
from coinbase.wallet.client import Client

def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    exit(0)


if __name__ == '__main__':
    signal(SIGINT, handler)
    print('Running. Press CTRL-C to exit.')

    coinbase_client = Client(os.environ.get("COINBASE_API_KEY"), os.environ.get("COINBASE_SECRET"))

    SECONDS_PER_SLOT = 12
    SLOTS_PER_EPOCH = 32
    GWEI_PER_ETH = 1000000000
    BEACONCHAIN_BASE_URL = "https://beaconcha.in/api/v1"

    beaconchain_timeout = 15
    beaconchain_timed_out = False
    coinbase_timeout = 15

    # Max 10
    validators = [
        '0xa68266429de6906469b825fbe01d70b5d155963dd0d0cd640b907f1da136de843638c0fb8ec6ba62660308ae2ecbf782',
        '0x9891e4522462230f6cdce5fc78dba78a99d6e82cc476feda0f91b6e8bd88f430038f086f90b2bea2f2fd9a2fa940897c'
        ]

    # Initialize csv files w/ correct headers
    for v in validators:
        try:
            df = pd.read_csv(f'csvs/lifetime/{v}.csv', index_col=0)
        except FileNotFoundError as e:
            df = pd.DataFrame(columns = ["timestamp", "datetime_utc","epoch","effective_balance_eth","balance_eth","delta_eth","balance_usd","delta_usd"])
            df.to_csv(f'csvs/lifetime/{v}.csv')

    # Loop through validators, check for most recent epochs.
    while True:
            # open or create today's csv
        today = date.today()
        try:
            df_today = pd.read_csv(f'csvs/daily/{today}.csv', index_col=0)
        except FileNotFoundError as e:
            df_today = pd.DataFrame(columns = ["timestamp", "datetime_utc","validator","epoch","effective_balance_eth","balance_eth","delta_eth","balance_usd","delta_usd"])
            df_today.to_csv(f'csvs/daily/{today}.csv')

        try:
            # get ETH_USD
            eth_usd_price = float(coinbase_client.get_spot_price(currency_pair = 'ETH-USD').amount) # only check this once for the whole loop through validators
            coinbase_timeout = 15
        except requests.ConnectionError as e:
            print(f"Unable to connect to Coinbase API, retrying in for {coinbase_timeout} seconds.")
            time.sleep(coinbase_timeout)
            coinbase_timeout += 15
            continue
        
        for v in validators:
            print(f"Updating balance sheet for validator: {v}")
            datapoints = [] # list of rows to add to DF.

            df = pd.read_csv(f'csvs/lifetime/{v}.csv', index_col=0)
            if len(df) > 0:
                last_recorded_epoch = df['epoch'].iloc[-1]
            else:
                last_recorded_epoch = 0

            try:
                history = requests.get(f"{BEACONCHAIN_BASE_URL}/validator/{v}/balancehistory")
                beaconchain_timeout = 15
                beaconchain_timed_out = False
            except requests.ConnectionError as e:
                print(f"Unable to connect to Beaconchain API, retrying in {beaconchain_timeout} seconds.")
                time.sleep(beaconchain_timeout)
                beaconchain_timeout += 15
                beaconchain_timed_out = True
                break

            data = history.json()['data']
            
            for epoch in data:
                if epoch['epoch'] > last_recorded_epoch:
                    balance_eth = (epoch["balance"]/GWEI_PER_ETH)
                    balance_usd = balance_eth*eth_usd_price
                    # leave deltas to 0 for now, we'll re-calculate shortly
                    row_to_add = {
                        "timestamp": int(time.time()), 
                        "datetime_utc": str(datetime.utcnow()), 
                        "epoch": epoch["epoch"], 
                        "effective_balance_eth": epoch["effectivebalance"]/GWEI_PER_ETH, 
                        "balance_eth": balance_eth, 
                        "delta_eth": 0, 
                        "balance_usd": balance_usd, 
                        "delta_usd": 0
                    }
                    datapoints.append(row_to_add)
                else:
                    # break and go to next validator
                    break

            # if we have datapoints, we want to reverse the row, so the oldest are first and newest last. The API returns newest first. 
            # The CSV has more recent entries appended to the bottom.
            if len(datapoints) > 0:
                datapoints = datapoints[::-1]
                
                # get the most recently saved balance info

                # calculate deltas
                for idx, dp in enumerate(datapoints):
                    if idx == 0:
                        if len(df) > 0:
                            last_eth_balance = df['balance_eth'].iloc[-1]
                            last_usd_balance = df['balance_usd'].iloc[-1]
                            delta_eth = dp["balance_eth"] - last_eth_balance
                            delta_usd = delta_eth * eth_usd_price  # don't want to do the delta between last usd balance and current, as there may have been price flux. Price flux goes into capital gains/losses
                            dp["delta_eth"] = delta_eth
                            dp["delta_usd"] = delta_usd
                    else:
                        delta_eth = dp["balance_eth"] - datapoints[idx-1]["balance_eth"]
                        delta_usd = delta_eth * eth_usd_price
                        dp["delta_eth"] = delta_eth
                        dp["delta_usd"] = delta_usd
                
                # save to the continuous/lifetime csv
                pd_datapoints = pd.DataFrame(datapoints)
                df = df.append(pd_datapoints, ignore_index=True)
                df.to_csv(f'csvs/lifetime/{v}.csv')

                # save to today's dataframe
                pd_datapoints['validator'] = v
                df_today = df_today.append(pd_datapoints, ignore_index=True)
                df_today.to_csv(f'csvs/daily/{today}.csv')

                print("Validator records updated to epoch: ", df['epoch'].iloc[-1])
            else:
                print("No new values found in epoch ", df['epoch'].iloc[-1])
        if not beaconchain_timed_out:
            time.sleep(SECONDS_PER_SLOT*SLOTS_PER_EPOCH/2)

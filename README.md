# Validator Balance

### Intro

This is a very small Python script which is intended to be run on the same box as a validator, but really can be run on any box with 100% uptime. It tracks a list of up to 10 validators, and saves balance details for every epoch to locally-saved csv files.

It tries to check only once per epoch, or roughly every 6 minutes. Each validator gets its own CSV file, with data for ["timestamp", "datetime_utc","epoch","effective_balance_eth","balance_eth","delta_eth","balance_usd","delta_usd"]. 

On the first run, if you have been running your validators for a while, be aware that the Beaconcha.in API endpoint I'm using seems to only get a maximmum of the 100 most-recent epochs. Additionally, the API doesn't get historical prices as Beaconchain doesn't provide timestamps. 

In a future update, I may at least add historical pricing for those past 100 epochs, by just calculating backwards based on how many seconds are in an epoch. 

I would recommend you find a solution to backup these CSV files regularly, as all this does is create them and append new data to the end.

### Pre-installation:
Register for Coinbase if you haven't and create an API key. One you are logged in, go [here](https://developers.coinbase.com/) and click "MY APPS" in the upper-right corner. Create the app and key. This script doesn't need any permissions, but Coinbase requires you to choose some when creating the key, so just choose whatever permissions you want. 

Then you can install the script.

### Installation
1. `pipenv install`
2. Export environment variables for COINBASE_API_KEY and COINBASE_SECRET
3. `pipenv shell`
4. `python validator_balance.py`

Then the script will start running. If the CSV files don't already exist, first they'll be created with the appropriate headers. If they do exist, on each loop the files will be opened, new data added, and saved.
from pathlib import Path
import os
import sys
import json
import time
import pandas as pd
from  dotenv import load_dotenv
from bridge_monitor import BridgeMonitor
from tabulate import tabulate
load_dotenv()

from web3 import Web3
PROVIDER_URI = "wss://{network}.infura.io/ws/v3/{project_id}".format(
                network='mainnet', project_id=os.getenv("WEB3_INFURA_PROJECT_ID"))
w3 = Web3(Web3.WebsocketProvider(PROVIDER_URI))

# verifying environment set-up
print("env loaded") if type(os.getenv("WEB3_INFURA_PROJECT_ID")) == str else print("env not loaded")
print("w3 connected:",str(w3.isConnected()))

addr_df = pd.read_csv(Path('./Resources/bridge_addrs.csv'))
addr_df['Address'] = addr_df['Address'].apply(w3.toChecksumAddress)

def main():
    print('\nBeginning Monitoring of Below Bridges:')
    print(tabulate(addr_df,headers='keys',tablefmt='psql',showindex='False'),'\n')

    monitor = BridgeMonitor(w3,addr_df)
    monitor.filter_layer2_events(poll_interval = 60)

if __name__ == '__main__':
    main()
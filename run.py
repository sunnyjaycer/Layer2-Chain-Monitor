from pathlib import Path
import os
import sys
import json
import time
import pandas as pd
from  dotenv import load_dotenv
from bridge_monitor import BridgeMonitor
load_dotenv()

from web3 import Web3
PROVIDER_URI = "wss://{network}.infura.io/ws/v3/{project_id}".format(
                network='mainnet', project_id=os.getenv("WEB3_INFURA_PROJECT_ID"))
w3 = Web3(Web3.WebsocketProvider(PROVIDER_URI))

# verifying environment set-up
print("env loaded") if type(os.getenv("WEB3_INFURA_PROJECT_ID")) == str else print("env not loaded")
print("w3 connected:",str(w3.isConnected()))

topics = list( pd.read_csv(Path('./Resources/topics.csv'))['Transfer Event Signature'] )

def main():
    monitor = BridgeMonitor(w3,topics)
    monitor.filter_layer2_events(poll_interval = 5)

if __name__ == '__main__':
    main()
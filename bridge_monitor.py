from web3 import Web3
from pathlib import Path
from hexbytes import HexBytes
import json
import time
import pandas as pd

# loading ERC20 contract
with open(Path("./Resources/ERC20_abi.json")) as json_file:
    erc20_abi = json.load(json_file)

class BridgeMonitor:
    """
    Monitor class contains monitoring functionality the listed information on Layer 2 Chain contract transfer events
    """

    def __init__(self,web3,address_df):
        self.web3 = web3
        self.addresses = list(address_df['Address'])
        self.contract_events_filter = self.web3.eth.filter({
            'address' : self.addresses
        })
        self.transfer_topic = HexBytes('0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef')

    def __log_tx(self,tx_hash,tx_from,tx_to,tx_blkn,token_sym,val):
        print(f'Tx Hash  : {tx_hash.hex()}')
        print(f'From     : {tx_from}')
        print(f'To       : {tx_to}')
        print(f'Token(s) : {token_sym}')
        print(f'Value    : {val}')
        print(f'Block #  : {tx_blkn}')
        print('-'*52)


    def __get_tx_data(self):
        events = self.contract_events_filter.get_new_entries()
        for event in events:
            tx_rcpt = self.web3.eth.getTransactionReceipt(event['transactionHash'])
            transfer_log = [log for log in tx_rcpt['logs'] if self.transfer_topic in log['topics']][0]
            tx_from = '0x' + transfer_log['topics'][1].hex()[-40:]
            tx_to = '0x' + transfer_log['topics'][2].hex()[-40:]
            tx_blkn = tx_rcpt['blockNumber']
            #token_det = self.__get_token_symbols( list( set( [log['address'] for log in tx_rcpt['logs']] ) ) )
            token_symb = self.__get_token_symbols(transfer_log['address'])
            tx_val = int(transfer_log['data'],16)            
            self.__log_tx(event['transactionHash'],tx_from,tx_to,tx_blkn,token_symb,tx_val)
    

    def __get_token_symbols(self,token_addrs):
        token_symbs = ''
        temp_token_contract = self.web3.eth.contract(self.web3.toChecksumAddress(token_addrs),abi = erc20_abi)
        token_symbs = temp_token_contract.functions.symbol().call()
        return token_symbs


    def filter_layer2_events(self,poll_interval = 15):
        while True:
            self.__get_tx_data()
            time.sleep(poll_interval)
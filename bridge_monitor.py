from web3 import Web3
from pathlib import Path
import os
import sys
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

    def __init__(self,web3,topics):
        self.web3 = web3
        self.topics = topics
        self.contract_events_filter = self.web3.eth.filter({
            'topics' : topics
        })


    def __log_tx(self,tx_hash,tx_from,tx_to,tx_blkn,token_addr):
        print(f'Tx Hash  : {tx_hash.hex()}')
        print(f'From     : {tx_from}')
        print(f'To       : {tx_to}')
        print(f'Block #  : {tx_blkn}')
        print(f'Token(s) : {token_addr}')
        print('-'*52)


    def __get_tx_data(self):
        events = self.contract_events_filter.get_new_entries()
        for event in events:
            print('EVENT DETECTED')
            tx_rcpt = self.web3.eth.getTransactionReceipt(event['transactionHash'])
            tx_from = tx_rcpt['from']
            tx_to = tx_rcpt['to']
            tx_blkn = tx_rcpt['blockNumber']
            token_addr = self.__get_token_symbols( list( set( [log['address'] for log in tx_rcpt['logs']] ) ) )
            # if len(token_addr) > 1: print('Program thinks there are multiple tokens!')
            self.__log_tx(event['transactionHash'],tx_from,tx_to,tx_blkn,token_addr)
    

    def __get_token_symbols(self,token_addrs):
        token_symbs = []
        for token_addr in token_addrs:
            try:
                token_symbs.append( self.web3.eth.contract(self.web3.toChecksumAddress(token_addr),abi = erc20_abi).functions.symbol().call() )
            # TODO: make it such that it only excepts for ContractLogicError
            except:
                pass
        return token_symbs


    def filter_layer2_events(self,poll_interval = 15):
        while True:
            self.__get_tx_data()
            print(f"Current Block #{self.web3.eth.get_block('latest')['number']}")
            time.sleep(poll_interval)
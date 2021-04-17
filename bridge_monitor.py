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

    def _log_tx(self,tx_hash,tx_from,tx_to,tx_blkn,token_sym,val):
        print(f'Tx Hash  : {tx_hash.hex()}')
        print(f'From     : {tx_from}')
        print(f'To       : {tx_to}')
        print(f'Token(s) : {token_sym}')
        print(f'Value    : {val}')
        print(f'Block #  : {tx_blkn}')
        print('-'*52)


    def _get_token_symbols(self,token_addrs):
        token_symbs = ''
        temp_token_contract = self.web3.eth.contract(self.web3.toChecksumAddress(token_addrs),abi = erc20_abi)
        token_symbs = temp_token_contract.functions.symbol().call()
        return token_symbs

    
    def to_thirty_two(self,topic):
        thirty_two = '0x' + topic.hex()[-40:]
        return self.web3.toChecksumAddress(thirty_two)


    def _get_tx_data(self):
        events = self.contract_events_filter.get_new_entries()
        for event in events:
            tx_rcpt = self.web3.eth.getTransactionReceipt(event['transactionHash'])
            transfer_log_list = [log for log in tx_rcpt['logs'] if self.transfer_topic in log['topics']]
            
            # TODO: this part of the code needs to be fixed. IndexError is being thrown. Might have to do with not being Checksum
            # If the log contains the address of any bridge contract address, that's the log we want. 
            # Some transactions (like 0x5c32688f5bacfd346a38b196bfc1331cbcb8271f88273b0c1a6f949a84b56396) have multiple transfers
            transfer_log = [log for log in transfer_log_list if any(self.to_thirty_two(topic) in self.addresses for topic in log['topics'])][0]
            
            tx_from = '0x' + transfer_log['topics'][1].hex()[-40:]
            tx_to = '0x' + transfer_log['topics'][2].hex()[-40:]
            tx_blkn = tx_rcpt['blockNumber']
            token_symb = self._get_token_symbols(transfer_log['address'])
            tx_val = int(transfer_log['data'],16)

            self._log_tx(event['transactionHash'],tx_from,tx_to,tx_blkn,token_symb,tx_val)


    def filter_layer2_events(self,poll_interval = 15):
        while True:
            self._get_tx_data()
            time.sleep(poll_interval)
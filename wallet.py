from py_hd_wallet import wallet
import eel
import re
from urllib.request import Request, urlopen
import json
import hashlib

from constants import *
from web3 import Web3
import os 
from dotenv import load_dotenv
from eth_account import Account 
import subprocess
import json
from bit import Key, PrivateKey, PrivateKeyTestnet
from bit.crypto import ECPrivateKey
from bit.curve import Point
from bit.format import (
    bytes_to_wif, public_key_to_address, public_key_to_coords, wif_to_bytes
)
from bit.network import NetworkAPI, get_fee_cached, satoshi_to_currency_cached
from bit.network.meta import Unspent
#from bit.transaction import calc_txid, create_p2pkh_transaction, sanitize_tx_data
from web3.middleware import geth_poa_middleware


eel.init('web')


#Wallet Functions

@eel.expose
def create_seed():
    seed = re.sub("[^\w]", " ",  wallet.generate_mnemonic()).split()
    count = 0
    seed_dict = {}
    for word in seed:
        count += 1
        word_count = "word" + str(count)
        seed_dict.update( {word_count : word} )
    return seed_dict

@eel.expose
def get_wallets(seed):
    coins = ['BTC','BTG','BCH','LTC','DASH','DOGE','XRP','ZCASH','XLM']
    coin_purse = {}
    for coin in coins:
        w = wallet.create_wallet(network=coin, seed=seed, children=1)
        coin_purse.update({
            coin : {"address": w['address'],
                   "privatek": w["xprivate_key"]
                   "publick" : w["xpublic_key"]
                   "children": w["children"]
                   }
        })
    return coin_purse

@eel.expose
def priv_key_to_account(coin, priv_key):
    
    if coin == "eth":        return Account.privateKeyToAccount(priv_key)       
    elif coin == "btc-test": return PrivateKeyTestnet(priv_key)  
    elif coin == "btc":      return PrivateKey(priv_key) 
    else:                    return "Not a supported coin"

    
def create_tx(coin, account, to, amount):
"""
coin options: eth, btc-test.
account: account containing all the info like private and public 
key as well as address of a certain account. This must be obtained
trough the method priv_key_to_account().
to: address to transfer funds.
amount: amount of the currency. Take into account that Ether must 
be expressed in weis.
"""
    if coin == "eth":
        gas_estimate = w3.eth.estimateGas(
            {
                "from": account.address,
                "to": to,
                "value": amount
            }
        )

        return {
            "from": account.address,
            "to": to,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gas_estimate,
            "nonce":w3.eth.getTransactionCount(account.address)
        }

    elif coin == "btc-test":
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])
    
    elif coin == "btc":
        return PrivateKey.prepare_transaction(account.address, [(to, amount, BTC)])
    
    else:
        return "Not a supported coin"

@eel.expose
def send_tx(coin, account, to, amount):
"""
coin options: eth, btc-test.
account: account containing all the info like private and public 
key as well as address of a certain account. This must be obtained
trough the method priv_key_to_account().
to: address to transfer funds.
amount: amount of the currency. Take into account that Ether must 
be expressed in weis.
"""  
    tx = create_tx(coin, account.address, to, amount)
    signed_tx = account.sign_transaction(tx) #how to do this tho
    
    if coin == "eth": 
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return result.hex()
    
    elif coin == "btc-test":
        result = NetworkAPI.broadcast_tx_testnet(signed_tx)
        return result
    
    elif coin == "btc":
        result = NetworkAPI.broadcast_tx(signed_tx)
        return result
    
    else:
        return "Not a supported coin"
    

@eel.expose
def get_balance(coin, account):
    
    if coin == "eth": 
        return w3.eth.getBalance(account.address)
         
    
    elif coin == "btc-test" or coin == "btc":
        return account.get_balance("btc")
    
    else:
        return "Not a supported coin"

    
    
    
#Dashboard Functions

def read_json(url):
    request = Request(url)
    response = urlopen(request)
    data = response.read()
    url2 = json.loads(data)
    return url2

@eel.expose
def get_prices(ticker_list = ['BTC','BTG','BCH','LTC','DASH','DOGE','XRP','ZEC','XLM']): 
    # Leaving this an argument instead of fixed string for flexibility, can be simpler/faster with fixed url input
    ticker_string=""
    for ticker in ticker_list:
        ticker_string += ticker+","
    url = f"https://min-api.cryptocompare.com/data/pricemulti?fsyms={ticker_string}&tsyms=USD"
    price_data = read_json(url)
    return price_data


# Password Functions

def hash_pass(pass_w):
    return hashlib.sha256(bytes(pass_w, 'utf-8')).hexdigest()

@eel.expose
def set_password(pass_w):
    file = open(".pwd", "w")
    file.write(hash_pass(pass_w))
    file.close()
    return True

@eel.expose
def check_password(pass_w):
    file = open(".pwd", "r")
    if file.read() == hash_pass(pass_w):
        return 'True'
    else:
        return 'False' 


eel.start('loginWindow.html', size=(1350, 750))
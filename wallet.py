from py_hd_wallet import wallet
import eel
import re
from urllib.request import Request, urlopen
import json
import hashlib
import os

import scrypt
import qrcode

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
from path import Path
import pandas as pd
from ML.ml_functions import get_arima_forecast_plot, get_rf_ensemble_plot

import pprint as pp
import requests
import hmac

get_rf_ensemble_plot()
get_arima_forecast_plot()
eel.init('web')

load_dotenv()
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
        os.environ[word_count] = word
    return seed_dict

@eel.expose
def derive_wallets(mnemonic, coin, nkeys):

    command = f'php ./hd-wallet-derive/hd-wallet-derive.php --mnemonic="{mnemonic}" --coin={coin} --numderive={nkeys}  --format=json -g'
    available_coins = "./hd-wallet-derive.php --help-coins" # --> currently not in use
    new_process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

    (output, err) = new_process.communicate()

    p_status = new_process.wait()

    if err:
        print("\nError:###\n\n")
        return err
    return json.loads(output)

coin_purse = {}


@eel.expose
def get_wallets(seed):
    #print(f"get_wallet. seed: \n{seed}")
    """
    coins = ['BTC','BTG','BCH','LTC','DASH','DOGE','XRP','ZCASH','XLM']
    global coin_purse 
    for coin in coins:
        w = wallet.create_wallet(network=coin, seed=seed, children=1)
        coin_purse.update({
            coin : {"address": w['address'],
                   "privatek": w["xprivate_key"],
                   "publick" : w["xpublic_key"],
                   "children": w["children"]
                   }
                   # a disadvantage of hd_derive_wallet is that it doesn't generate 
                   # a specific child. For instance, like the child with index 19384.
                   # So you are forced to create the whole chain of child addresses
                   # from 0 to 19384.
        })"""
    coin_purse = {  #We'll have to add more coins, specially ERC20 tokens
    "ETH"     : derive_wallets(seed, "ETH", 2), 
    "BTC-test": derive_wallets(seed, "BTC-test", 2),
    "BTC"     : derive_wallets(seed, "BTC", 2),
    "BTG"     : derive_wallets(seed, "BTG", 2),
    "BCH"     : derive_wallets(seed, "BCH", 2),
    "LTC"     : derive_wallets(seed, "LTC", 2),
    "DASH"    : derive_wallets(seed, "DASH", 2),
    "DOGE"   : derive_wallets(seed, "DOGE", 2),
    #"XRP"     : derive_wallets(seed, "XRP", 10), #https://bitcoin.stackexchange.com/questions/75385/does-ripple-has-support-for-hd-wallets
    "ZCASH"   : derive_wallets(seed, "ZEC", 2),
    #"XML"     : derive_wallets(seed, "XML", 10),
}
    return coin_purse

@eel.expose
def priv_key_to_account(coin, priv_key):
    #print(f"coin: {coin} type: {type(coin)}\nprivate key: {priv_key} type: {type(priv_key)}")
    
    """Use it like this: my_btctest_account = priv_key_to_account("btc-test",coin_purse["btc-test"][0]["privkey"])"""
    if coin == "ETH":        
        return Account.privateKeyToAccount(priv_key)       
    elif coin == "BTC-test": 
        return PrivateKeyTestnet(priv_key)  
    elif coin == "BTC":
        print("a btc account is being created")
        acc = PrivateKey(priv_key) 
        #print(acc)
        return acc 
    else:                    return "Not a supported coin"

    
def create_tx(coin, account, to, amount):
    """
    coin options: eth, btc-test, btc.
    account: account containing all the info like private and public 
    key as well as address of a certain account. This must be obtained
    trough the method priv_key_to_account().
    to: address to transfer funds.
    amount: amount of the currency. Take into account that Ether must 
    be expressed in weis.
    """
    if coin == "ETH":
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
    
    elif coin == "BTC":
        return PrivateKey.prepare_transaction(account.address, [(to, amount, BTC)])
    
    else:
        return "Not a supported coin"

@eel.expose
def send_tx(coin, privkey, to, amount):
    """
    coin options: eth, btc-test.
    privkey: ignore this (have to fix it): account containing all the info like private and public 
    key as well as address of a certain account. This must be obtained
    trough the method priv_key_to_account().
    to: address to transfer funds.
    amount: amount of the currency. Take into account that Ether must 
    be expressed in weis.
    Example: send_tx(coin = "btc-test",account = my_btctest_account, to = coin_purse["btc-test"][1]["address"],amount= 0.01)
    """  
    #print(f"{coin}, {privkey}, {to}, {amount}")
    tx = create_tx(coin, priv_key_to_account(coin, privkey), to, amount)
    print(tx)
    signed_tx = priv_key_to_account(coin, privkey).sign_transaction(tx) #how to do this tho
    
    if coin == "ETH": 
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return result.hex()
    
    elif coin == "btc-test":
        result = NetworkAPI.broadcast_tx_testnet(signed_tx)
        return result
    
    elif coin == "BTC":
        result = NetworkAPI.broadcast_tx(signed_tx)
        print(result)
        return result
    
    else:
        return "Not a supported coin"
    

@eel.expose
def get_balance(coin, privkey):
    
    balance = -1
    
    if coin == "ETH": 
        return w3.eth.getBalance(priv_key_to_account(coin, privkey).address)
            
    elif coin == "BTC-test" or coin == "BTC":        
        balance = priv_key_to_account(coin, privkey).get_balance("btc")
        return balance
    
    else:
        return "Not a supported coin"
    
@eel.expose
def make_qr(address):
    """
    address: string format of address
    """
    qrcode.make(address).save("web/images/QR.png")
    return True



@eel.expose
def get_seed():
    seed_phrase = ""
    for i in range(12):
        word = "word" + str(i + 1)
        seed_phrase += os.environ[word] + " "
    return seed_phrase
    

@eel.expose
def decrypt_seed(seed_index):
    print(f"seed index: {seed_index}")
    password = "Wallet #1 in 2020" # For right now, the password doesn't count.
    seed_path = Path(f".pwd.csv")
    seed_df = pd.read_csv(seed_path)
    ecnrypted_seed =bytes.fromhex(seed_df["seed"].iloc[int(seed_index)])   
    decrypted = scrypt.decrypt(ecnrypted_seed, password, maxtime=0.4)
    #print(f"decrypted seed: \n{decrypted}")
    return decrypted
  

    
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

def hash_pass(pass_w, salt):
    return scrypt.encrypt(pass_w , salt, maxtime=0.2)

@eel.expose
def set_password(pass_w, seed):
    
    password = {"seed": [hash_pass(seed ,"Wallet #1 in 2020").hex()], #we encrypt the mnemonic seed with the password
               "password": [hash_pass(pass_w,"super wallet").hex()]} #ecnryption of the password with a salt
    
    psw_df = pd.DataFrame(password)    
    pass_path = Path(f".pwd.csv")
    
    try:
        current_df = pd.read_csv(pass_path)
        print("found file")
        current_df.drop(columns=["Unnamed: 0"], inplace = True)        
        updated_df = pd.concat([current_df, psw_df], axis = 0, ignore_index=True, sort=True)
        print("concatenated succesfully")
        print(updated_df)
        updated_df.to_csv(pass_path)
        
    except:
        print("no password db found")
        psw_df.to_csv(pass_path)

    return True

@eel.expose
def check_password(pass_w):
   
    pass_path = Path(f".pwd.csv")
    password = pd.read_csv(pass_path)
    for row in range(password.shape[0]):
        ecnrypted_pass =bytes.fromhex(password["password"].iloc[row])   
        decrypted = scrypt.decrypt(ecnrypted_pass,'super wallet',maxtime=0.4)
        if decrypted == pass_w: 
            return row
    print("no password found")
    return -1

def getCurrencies():
    '''
    Should be called when the user goes to the exchange screen. No Parameters.
    
    Should return a list of possible swaps.
    
    120 X 119 pairs, at 14280 possibiliy pairs
    '''
    #API CALL
    message = {
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'getCurrencies', #getCurrenciesFull will return all available and their state
    'params': []
    }

    serialized_data = json.dumps(message)

    sign = hmac.new(API_SECRET.encode('utf-8'), serialized_data.encode('utf-8'), hashlib.sha512).hexdigest()

    headers = {'api-key': API_KEY, 'sign': sign, 'Content-type': 'application/json'}
    
    response_getcurrencies = requests.post(API_URL, headers=headers, data=serialized_data)
    
    #Error handling if serve is down or crashes
    if '<Response [200]>' == str(response_getcurrencies) :
        pass
    else:
        raise ValueError("Serve may have crashed or is down for repairs. Please try again later.")
    
    #List of possible currencies
    list_of_currencies = response_getcurrencies.json()['result']
    
    return list_of_currencies

def getNetwork(coin):
    network=None

    if coin == "BTG": 
        from clove.network import Bitcoin_gold
        network = Bitcoin_gold()
    elif coin == "LTC": 
        from clove.network import Litecoin
        network = Litecoin()
    elif coin == "BTC": 
        from clove.network import Bitcoin
        network = Bitcoin()
    elif coin == "DASH": 
        from clove.network import Dash
        network = Dash()
    else: return "Coin not supported"

    return network


@eel.expose
def start_atom_swap(coin, privkey, to, amount):

    network = getNetwork(coin)
    
    print(network)
    sendWallet = network.get_wallet(private_key=privkey)
    print(f"balance of sendWallet: {network.get_balance(sendWallet.address)}")
    initial_transaction = network.atomic_swap(
        sender_address=sendWallet.address,
        recipient_address=to,
        value=float(amount) 
        )
    initial_transaction.add_fee_and_sign(sendWallet)
    tx_details = initial_transaction.show_details()
    initial_transaction.publish()
    with open("startedSwap.json", "w") as write_file:
        json.dump(tx_details, fp=write_file, indent=4, sort_keys=True, default=str)
    #json_tx = json.dumps(tx_details, indent=4, sort_keys=True, default=str)
    #print(json_tx)
    return tx_details


@eel.expose
def audit_tx(coin, _contract, _transaction_address, local=True):

    network = getNetwork(coin)

    audited_contract = network.audit_contract(contract=_contract,transaction_address= _transaction_address)
    tx = audited_contract.show_details()
    if local: return audited_contract
    else: return tx

@eel.expose
def participateSwap(sendingCur, receivingCur, privkey, to, amount, _contract, _transaction_address):

    #contractNetwork = getNetwork(receivingCur)
    partNetwork = getNetwork(sendingCur)

    contract = audit_tx(receivingCur, _contract, _transaction_address)

    wallet = partNetwork.get_wallet(private_key=privkey)
    print(f"balance of sendWallet: {partNetwork.get_balance(wallet.address)}")
    participate_transaction = contract.participate(
        symbol=sendingCur,
        sender_address=wallet.address,
        recipient_address=to,
        value=float(amount),)
    participate_transaction.add_fee_and_sign(wallet)
    tx_details = participate_transaction.show_details()
    
    with open("participatedSwap.json", "w") as write_file:
        json.dump(tx_details, fp=write_file, indent=4, sort_keys=True, default=str)
    json_tx = json.dumps(tx_details, indent=4, sort_keys=True, default=str)
    print(json_tx)

    participate_transaction.publish()

    return tx_details

@eel.expose
def redeem_tx(coin, privkey, _contract, _transaction_address):

    network = getNetwork(coin)
    
    print(network)
    wallet = network.get_wallet(private_key=privkey)
    print(f"balance of sendWallet: {network.get_balance(wallet.address)}")
    contract = audit_tx(coin, _contract, _transaction_address)

    with open('startedSwap.json') as f:
        data = json.load(f)

    redemption = contract.redeem(secret=data["secret"], wallet=wallet)

    redemption.add_fee_and_sign()
    redemption.publish()
    tx_details = redemption.show_details()
    with open("redeemedSwap.json", "w") as write_file:
        json.dump(tx_details, fp=write_file, indent=4, sort_keys=True, default=str)
    #json_tx = json.dumps(tx_details, indent=4, sort_keys=True, default=str)
    #print(json_tx)
    return tx_details

@eel.expose
def finish_swap(coin, privkey, _contract, _transaction_address):
    """
    coin: is the currency that the initial transaction sent.
    privkey: the private key of the local account in the receiving currency 
    _contract: of the started transaction
    _transaction_address: transaction
    """

    network = getNetwork(coin)

    wallet = network.get_wallet(private_key=privkey)

    with open('participatedSwap.json') as f:
        data = json.load(f)
    
    contract = audit_tx(coin, _contract, _transaction_address)
    
    secret = network.extract_secret_from_redeem_transaction(data["contract_address"])
    closing_tx = contract.redeem(secret=secret, wallet=wallet)
    closing_tx.add_fee_and_sign()
    closing_tx.publish()
    tx_details = closing_tx.show_details()

    return tx_details


eel.start('loginWindow.html', size=(1350, 750))

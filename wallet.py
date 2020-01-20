from py_hd_wallet import wallet
import eel
import re
from urllib.request import Request, urlopen
import json
import hashlib
import os
import platform
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
from ML.ml_functions import get_arima_forecast_plot

get_arima_forecast_plot()
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
        os.environ[word_count] = word
    return seed_dict

@eel.expose
def derive_wallets(mnemonic, coin, nkeys):
    os = platform.system()
    if os == 'Windows':
        prefix = 'php'
        command = f'{prefix} ./hd-wallet-derive/hd-wallet-derive.php --mnemonic="{mnemonic}" --coin={coin} --numderive={nkeys}  --format=json -g'
    elif os == 'Darwin':
        command = f'./hd-wallet-derive/hd-wallet-derive.php --mnemonic="{mnemonic}" --coin={coin} --numderive={nkeys}  --format=json -g'
    else:
        return err
    
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
    "ETH"     : derive_wallets(seed, "ETH", 10), 
    "BTC-test": derive_wallets(seed, "BTC-test", 10),
    "BTC"     : derive_wallets(seed, "BTC", 10),
    "BTG"     : derive_wallets(seed, "BTG", 10),
    "BCH"     : derive_wallets(seed, "BCH", 10),
    "LTC"     : derive_wallets(seed, "LTC", 10),
    "DASH"    : derive_wallets(seed, "DASH", 10),
    "DOGE"   : derive_wallets(seed, "DOGE", 10),
    #"XRP"     : derive_wallets(seed, "XRP", 10), #https://bitcoin.stackexchange.com/questions/75385/does-ripple-has-support-for-hd-wallets
    "ZCASH"   : derive_wallets(seed, "ZEC", 10),
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
    print(f"{coin}, {privkey}, {to}, {amount}")
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
    

#Production Version (Encrypted)

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
'''  

@eel.expose
def decrypt_seed(seed_index):
    
    #FOR DEVELOPMENT ONLY - NOT SECURE
    
    print(f"seed index: {seed_index}")
    password = "Wallet #1 in 2020" # For right now, the password doesn't count.
    seed_path = Path(f".pwd.csv")
    seed_df = pd.read_csv(seed_path)
    decrypted =seed_df["seed"].iloc[int(seed_index)]  
    #print(f"decrypted seed: \n{decrypted}")
    return decrypted
'''   
    
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

# Production Version (Encrypted)

def hash_pass(pass_w, salt):
    #return hashlib.sha256(bytes(pass_w, 'utf-8')).hexdigest() #Original
    return scrypt.encrypt(pass_w , salt, maxtime=0.2)


@eel.expose
def set_password(pass_w, seed):
    print(f"pass: {pass_w}\nseed: {seed}")
    
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
'''

@eel.expose
def set_password(pass_w, seed):

    # FOR DEVELOPMENT ONLY - NOT SECURE

    print(f"pass: {pass_w}\nseed: {seed}")
    
    password = {"seed": [seed], #we encrypt the mnemonic seed with the password
               "password": [pass_w]} #ecnryption of the password with a salt
    
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
'''

# Production Version (Encrypted)

@eel.expose
def check_password(pass_w):
   
    pass_path = Path(f".pwd.csv")
    password = pd.read_csv(pass_path)
    for row in range(password.shape[0]):
        #print(row)
        ecnrypted_pass =bytes.fromhex(password["password"].iloc[row])   
        decrypted = scrypt.decrypt(ecnrypted_pass,'super wallet',maxtime=0.4)
        #print(decrypted)
        if decrypted == pass_w: 
            return row
    print("no password found")
    return -1
'''

@eel.expose
def check_password(pass_w):

    # FOR DEVELOPMENT ONLY - NOT SECURE

    pass_path = Path(f".pwd.csv")
    password = pd.read_csv(pass_path)
    for row in range(password.shape[0]):
        print(row)
        decrypted =password["password"].iloc[row]  
        print(decrypted)
        if decrypted == pass_w: 
            return row
    print("no password found")
    return -1
'''
eel.start('loginWindow.html', size=(1350, 750))

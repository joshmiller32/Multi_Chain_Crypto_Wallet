from py_hd_wallet import wallet
import eel
import re
from urllib.request import Request, urlopen
import json
import hashlib


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
            coin : w['address']
        })
    return coin_purse


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
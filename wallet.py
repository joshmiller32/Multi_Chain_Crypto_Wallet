from py_hd_wallet import wallet
import eel
import re

eel.init('web')

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

eel.start('loginWindow.html', size=(1000, 600))
from py_hd_wallet import wallet

def new_user():
    seed = wallet.generate_mnemonic()
    return seed

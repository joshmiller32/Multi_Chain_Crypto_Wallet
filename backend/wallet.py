from py_hd_wallet import wallet
import sys
'''
def new_user():
    seed = wallet.generate_mnemonic()
    return seed
    
converting from function because electron can only read from system outputs
'''
seed = wallet.generate_mnemonic()
print(seed)
sys.stdout.flush()

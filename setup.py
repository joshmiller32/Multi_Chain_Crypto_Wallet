import subprocess
import sys

def install(package):
    print(f"Installing {package} ...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
packages = ["py_hd_wallet", "eel", "qrcode", "clove", "web3", "python-dotenv", "bit", "plotly", "scikit-garden", "scrypt"]

for package in packages:
    try: 
        install(package)
    except:
        pass

print(f"Finished Installing {len(packages)} Packages")

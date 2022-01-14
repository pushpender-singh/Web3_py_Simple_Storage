import json
from solcx import compile_standard, install_solc
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

# Reading the smart contract

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

install_solc("0.8.0")


compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evmbytecode.sourceMap"]}
            }
        },
    },
    solc_version="0.8.0",
)

# Dumping the compiled code with abi and bytecode in another .json file

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Bytecode extraction

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["simpleStorage"]["evm"][
    "bytecode"
]["object"]

# ABI extraction

abi = compiled_sol["contracts"]["SimpleStorage.sol"]["simpleStorage"]["abi"]

# For connecting to ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
chain_id = 1337
my_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
private_key = os.getenv("PRIVATE_KEY")

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.getTransactionCount(my_address)

# Creating a transaction

transaction = SimpleStorage.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)

# Signing a transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

print("Deploying Contract!")
# Sending a transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

# Wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
tx_reciept = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Done! Contract deployed ")

simple_storage = w3.eth.contract(address=tx_reciept.contractAddress, abi=abi)
# Call from contract

print(f"Initial Stored Value {simple_storage.functions.retrieve().call()}")
# Working with deployed smart contract
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)

# Signing
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)

# Sending
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
print("Updating stored Value...")
tx_reciept = w3.eth.wait_for_transaction_receipt(send_store_tx)
print(simple_storage.functions.retrieve().call())

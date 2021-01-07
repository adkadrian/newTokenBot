import requests
import os
from web3.auto.infura import infura


def sendMessage(_message):
    bot = os.getenv('TELEGRAM_BOT')
    botKey = os.getenv('TELEGRAM_BOT_KEY')
    receiver = 1078114516
    baseUrl = 'https://api.telegram.org/bot{}:{}/sendMessage?' \
              'chat_id={}&text="{}"'.format(bot, botKey, receiver, _message)
    requests.get(baseUrl)


def p(argument):
    print(argument)


def getTransactionReceiver(_transaction):
    return _transaction['to']


def getTransactionReceipt(_transactionHash):
    # return infura.eth.getTransactionReceipt(_transactionHash)
    return infura.eth.waitForTransactionReceipt(_transactionHash)


def getBlockNumber(_block):
    return _block['number']


def getBlockTransactions(_block):
    return _block['transactions']


def getBlock(_blockNumber='latest'):
    return infura.eth.getBlock(_blockNumber, True)


recentBlockNumber = None

while True:
    block = getBlock()
    blockNumber = getBlockNumber(block)
    p(str(recentBlockNumber) + ' ' + str(blockNumber))
    if blockNumber != recentBlockNumber:
        p('checking block: ' + str(blockNumber))
        transactions = getBlockTransactions(block)
        for transaction in transactions:
            if transaction['to'] is None:
                p('new contract found')
                if transaction['to'] is None or transaction['to'] == 0x0:
                    p('block number: ' + str(blockNumber))

                    ABI = [{"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}],
                            "payable": False, "stateMutability": "view", "type": "function"}, {"constant": False,
                                                                                               "inputs": [
                                                                                                   {"name": "_spender",
                                                                                                    "type": "address"},
                                                                                                   {"name": "_value",
                                                                                                    "type": "uint256"}],
                                                                                               "name": "approve",
                                                                                               "outputs": [{"name": "",
                                                                                                            "type": "bool"}],
                                                                                               "payable": False,
                                                                                               "stateMutability": "nonpayable",
                                                                                               "type": "function"},
                           {"constant": True, "inputs": [], "name": "totalSupply",
                            "outputs": [{"name": "", "type": "uint256"}], "payable": False, "stateMutability": "view",
                            "type": "function"}, {"constant": False, "inputs": [{"name": "_from", "type": "address"},
                                                                                {"name": "_to", "type": "address"},
                                                                                {"name": "_value", "type": "uint256"}],
                                                  "name": "transferFrom", "outputs": [{"name": "", "type": "bool"}],
                                                  "payable": False, "stateMutability": "nonpayable",
                                                  "type": "function"},
                           {"constant": True, "inputs": [], "name": "decimals",
                            "outputs": [{"name": "", "type": "uint8"}],
                            "payable": False, "stateMutability": "view", "type": "function"},
                           {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf",
                            "outputs": [{"name": "balance", "type": "uint256"}], "payable": False,
                            "stateMutability": "view", "type": "function"},
                           {"constant": True, "inputs": [], "name": "symbol",
                            "outputs": [{"name": "", "type": "string"}],
                            "payable": False, "stateMutability": "view", "type": "function"}, {"constant": False,
                                                                                               "inputs": [
                                                                                                   {"name": "_to",
                                                                                                    "type": "address"},
                                                                                                   {"name": "_value",
                                                                                                    "type": "uint256"}],
                                                                                               "name": "transfer",
                                                                                               "outputs": [{"name": "",
                                                                                                            "type": "bool"}],
                                                                                               "payable": False,
                                                                                               "stateMutability": "nonpayable",
                                                                                               "type": "function"},
                           {"constant": True,
                            "inputs": [{"name": "_owner", "type": "address"}, {"name": "_spender", "type": "address"}],
                            "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "payable": False,
                            "stateMutability": "view", "type": "function"},
                           {"payable": True, "stateMutability": "payable", "type": "fallback"}, {"anonymous": False,
                                                                                                 "inputs": [
                                                                                                     {"indexed": True,
                                                                                                      "name": "owner",
                                                                                                      "type": "address"},
                                                                                                     {"indexed": True,
                                                                                                      "name": "spender",
                                                                                                      "type": "address"},
                                                                                                     {"indexed": False,
                                                                                                      "name": "value",
                                                                                                      "type": "uint256"}],
                                                                                                 "name": "Approval",
                                                                                                 "type": "event"},
                           {"anonymous": False, "inputs": [{"indexed": True, "name": "from", "type": "address"},
                                                           {"indexed": True, "name": "to", "type": "address"},
                                                           {"indexed": False, "name": "value", "type": "uint256"}],
                            "name": "Transfer", "type": "event"}]
                    contract = infura.eth.contract(
                        address=getTransactionReceipt(transaction['hash'])['contractAddress'],
                        abi=ABI
                    )
                    try:
                        address = getTransactionReceipt(transaction['hash'])['contractAddress']
                        totalSupply = contract.functions.totalSupply().call()
                        name = contract.functions.name().call()
                        symbol = contract.functions.symbol().call()
                        message = 'New token found: \n' \
                                  'Name: {}\n' \
                                  'Symbol: {}\n' \
                                  'Total Supply: {}\n' \
                                  'Address: {}'.format(name, symbol, str(totalSupply), str(address))
                        p(message)
                        sendMessage(message)

                    except:
                        p('It wasn\'t  a Token')
    recentBlockNumber = blockNumber


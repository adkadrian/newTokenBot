import requests
import os
from web3.auto.infura import infura


# function to sending messages by telegram bot
# bot id and key should be defined as environment variable
def sendMessage(_message):
    bot = os.getenv('TELEGRAM_BOT')
    botKey = os.getenv('TELEGRAM_BOT_KEY')
    receiver = os.getenv('RECEIVER')
    baseUrl = 'https://api.telegram.org/bot{}:{}/sendMessage?' \
              'chat_id={}&text="{}"'.format(bot, botKey, receiver, _message)
    requests.get(baseUrl)


# returns receiver of given transaction
def getTransactionReceiver(_transaction):
    return _transaction['to']


# returns transaction receipt for provided transaction hash
def getTransactionReceipt(_transactionHash):
    return infura.eth.waitForTransactionReceipt(_transactionHash)


# returns block number for given block
def getBlockNumber(_block):
    return _block['number']


# returns all block transactions
def getBlockTransactions(_block):
    return _block['transactions']


# returns block data, if number will be not provided returns data for latest block
def getBlock(_blockNumber='latest'):
    return infura.eth.getBlock(_blockNumber, True)


# store number of last checked block
recentBlockNumber = None

# program loop
while True:
    # get data for latest block
    block = getBlock()

    # get block number
    blockNumber = getBlockNumber(block)
    print(str(recentBlockNumber) + ' ' + str(blockNumber))

    # check if new block is available
    if blockNumber != recentBlockNumber:
        print('checking block: ' + str(blockNumber))

        # get all transactions of block
        transactions = getBlockTransactions(block)

        # fetch transactions
        for transaction in transactions:

            # check receiver of transaction,
            # if to is None new contract is created
            if transaction['to'] is None:
                print('new contract found')
                print('block number: ' + str(blockNumber))

                # get newly created contract address
                contractAddress = getTransactionReceipt(transaction['hash'])['contractAddress']

                # ABI of ERC20 contracts
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

                # get contract
                contract = infura.eth.contract(address=contractAddress, abi=ABI)

                # check if newly created contract has ERC20 functions
                # like totalSupply(), name() and symbol()
                try:
                    # get contract address
                    address = getTransactionReceipt(transaction['hash'])['contractAddress']

                    # try call totalSupply() function, if returns value it's mean that is new token
                    totalSupply = contract.functions.totalSupply().call()

                    # get token name
                    name = contract.functions.name().call()

                    # get token symbol
                    symbol = contract.functions.symbol().call()

                    # create message to send if new token is created
                    message = 'New token found: \n' \
                              'Name: {}\n' \
                              'Symbol: {}\n' \
                              'Total Supply: {}\n' \
                              'Address: {}'.format(name, symbol, str(totalSupply), str(address))

                    # print and send message
                    print(message)
                    sendMessage(message)
                except:
                    # if token functions raise exception it's mean it wasn't token
                    print('It wasn\'t  a Token')

    # set recentBlockNumber after checking all transactions in block
    # to not check the same block once again
    recentBlockNumber = blockNumber

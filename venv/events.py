import requests
import os

from hexbytes import HexBytes
from web3.auto.infura import infura


# sends message by telegram bot
# id and key of the bot should be provided
# as a local variables
def sendMessage(_message):
    bot = os.getenv('TELEGRAM_BOT')
    botKey = os.getenv('TELEGRAM_BOT_KEY')
    receiver = os.getenv('RECEIVER')
    baseUrl = 'https://api.telegram.org/bot{}:{}/sendMessage?' \
              'chat_id={}&text="{}"'.format(bot, botKey, receiver, _message)
    requests.get(baseUrl)


# returns address of receiver from provided transaction
def getTransactionReceiver(_transaction):
    return _transaction['to']


# returns receipt of provided transactions
def getTransactionReceipt(_transactionHash):
    return infura.eth.waitForTransactionReceipt(_transactionHash)


# returns block number from provided block data
def getBlockNumber(_block):
    return _block['number']


# returns all transactions from provided block data
def getBlockTransactions(_block):
    return _block['transactions']


# returns data for provided block number
# if number is not provided returns data for latest block
def getBlock(_blockNumber='latest'):
    return infura.eth.getBlock(_blockNumber, True)


# converts hexadecimal to checksum address
# which accepts as parameter web3.contract function
def toChecksumAddress(_address):
    return infura.toChecksumAddress(_address)


# address of UNISWAP contract which all creation of the new pair of tokens interact with
uniswapAddress = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'

# store last checked block number
recentBlockNumber = None

# Hex Bytes representations of function which creates new pair
eventPairCreatedHash = HexBytes(infura.keccak(text='PairCreated(address,address,address,uint256)').hex())

# Hex Bytes representations of function which transfer tokens
eventTokenTransfer = HexBytes(infura.keccak(text='Transfer(address,address,uint256)').hex())

# program loop
while True:
    # get latest block data
    block = getBlock()

    # get block number
    blockNumber = getBlockNumber(block)
    print(str(recentBlockNumber) + ' ' + str(blockNumber))

    # check if block wasn't checked
    if blockNumber != recentBlockNumber:
        print('checking block: ' + str(blockNumber))

        # get all block transactions
        transactions = getBlockTransactions(block)

        # fetch all transactions
        for transaction in transactions:
            # check if receiver of the transaction is UNISWAP
            if transaction['to'] == uniswapAddress:
                # get receipt of currently checking transaction
                # which interact with UNISWAP
                receipt = getTransactionReceipt(transaction['hash'])

                # define event
                event = None

                # try to get logs and topics from receipt, some transactions don't contain logs
                # transactions which create new pair have log of the calling function CreatedPair
                try:
                    # if log is present set data as event to check
                    event = receipt['logs'][0]['topics'][0]
                except:
                    # if transaction doesn't have logs leave event variable as None
                    event = None

                # check if transactions event is creation of new pair
                if event == eventPairCreatedHash:
                    print('new pair')

                    # get transaction hash
                    transactionHash = transaction['hash'].hex()

                    # get tokens addresses
                    token0 = toChecksumAddress(receipt['logs'][0]['topics'][1][12:].hex())
                    token1 = toChecksumAddress(receipt['logs'][0]['topics'][2][12:].hex())

                    # ABI of ERC20 contracts
                    ABI = [{"constant": True, "inputs": [], "name": "name",
                            "outputs": [{"name": "", "type": "string"}],
                            "payable": False, "stateMutability": "view", "type": "function"}, {"constant": False,
                                                                                               "inputs": [
                                                                                                   {
                                                                                                       "name": "_spender",
                                                                                                       "type": "address"},
                                                                                                   {
                                                                                                       "name": "_value",
                                                                                                       "type": "uint256"}],
                                                                                               "name": "approve",
                                                                                               "outputs": [
                                                                                                   {"name": "",
                                                                                                    "type": "bool"}],
                                                                                               "payable": False,
                                                                                               "stateMutability": "nonpayable",
                                                                                               "type": "function"},
                           {"constant": True, "inputs": [], "name": "totalSupply",
                            "outputs": [{"name": "", "type": "uint256"}], "payable": False,
                            "stateMutability": "view",
                            "type": "function"},
                           {"constant": False, "inputs": [{"name": "_from", "type": "address"},
                                                          {"name": "_to", "type": "address"},
                                                          {"name": "_value", "type": "uint256"}],
                            "name": "transferFrom", "outputs": [{"name": "", "type": "bool"}],
                            "payable": False, "stateMutability": "nonpayable",
                            "type": "function"},
                           {"constant": True, "inputs": [], "name": "decimals",
                            "outputs": [{"name": "", "type": "uint8"}],
                            "payable": False, "stateMutability": "view", "type": "function"},
                           {"constant": True, "inputs": [{"name": "_owner", "type": "address"}],
                            "name": "balanceOf",
                            "outputs": [{"name": "balance", "type": "uint256"}], "payable": False,
                            "stateMutability": "view", "type": "function"},
                           {"constant": True, "inputs": [], "name": "symbol",
                            "outputs": [{"name": "", "type": "string"}],
                            "payable": False, "stateMutability": "view", "type": "function"}, {"constant": False,
                                                                                               "inputs": [
                                                                                                   {"name": "_to",
                                                                                                    "type": "address"},
                                                                                                   {
                                                                                                       "name": "_value",
                                                                                                       "type": "uint256"}],
                                                                                               "name": "transfer",
                                                                                               "outputs": [
                                                                                                   {"name": "",
                                                                                                    "type": "bool"}],
                                                                                               "payable": False,
                                                                                               "stateMutability": "nonpayable",
                                                                                               "type": "function"},
                           {"constant": True,
                            "inputs": [{"name": "_owner", "type": "address"},
                                       {"name": "_spender", "type": "address"}],
                            "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "payable": False,
                            "stateMutability": "view", "type": "function"},
                           {"payable": True, "stateMutability": "payable", "type": "fallback"}, {"anonymous": False,
                                                                                                 "inputs": [
                                                                                                     {
                                                                                                         "indexed": True,
                                                                                                         "name": "owner",
                                                                                                         "type": "address"},
                                                                                                     {
                                                                                                         "indexed": True,
                                                                                                         "name": "spender",
                                                                                                         "type": "address"},
                                                                                                     {
                                                                                                         "indexed": False,
                                                                                                         "name": "value",
                                                                                                         "type": "uint256"}],
                                                                                                 "name": "Approval",
                                                                                                 "type": "event"},
                           {"anonymous": False, "inputs": [{"indexed": True, "name": "from", "type": "address"},
                                                           {"indexed": True, "name": "to", "type": "address"},
                                                           {"indexed": False, "name": "value", "type": "uint256"}],
                            "name": "Transfer", "type": "event"}]

                    # get contracts of the tokens
                    contract0 = infura.eth.contract(address=token0, abi=ABI)
                    contract1 = infura.eth.contract(address=token1, abi=ABI)

                    # get names of the tokens
                    token0name = contract0.functions.name().call()
                    token1name = contract1.functions.name().call()

                    # prepare message to send
                    message = 'NEW PAIR\n' \
                              '{}-{}\n' \
                              '{}'.format(token0name, token1name, transactionHash)
                    print(message)

                    # send message
                    sendMessage(message)

                # check if transaction event is Transfer
                elif event == eventTokenTransfer:
                    print('token transfer')
                else:
                    print('different event')

    # store number of the checked block to not check it again
    recentBlockNumber = blockNumber

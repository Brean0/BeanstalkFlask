# import web3 libraries:
from web3 import Web3
from flask import jsonify
import json
import os

def getWeb3Data():
    BEANSTALK_CONTRACT = '0xC1E088fC1323b20BCBee9bd1B9fC9546db5624C5'
    BEANSTALK_PRICE = '0xb01CE0008CaD90104651d6A84b6B11e182a9B62A'
    BEAN_CONTRACT = '0xBEA0000029AD1c77D3d5D23Ba2D8893dB9d1Efab'
    MULTICALL_CONTRACT = '0xcA11bde05977b3631167028862bE2a173976CA11'

    web3 = Web3(Web3.HTTPProvider(os.environ.get('RPC_URL')))
    BEANSTALK_ABI = json.load(open('beanstalk.json'))
    BEANSTALK_PRICE_ABI = json.load(open('beanstalkPrice.json'))
    BEAN = json.load(open('bean.json'))
    MULTICALL_ABI = json.load(open('multicall.json'))

    beanstalk = web3.eth.contract(BEANSTALK_CONTRACT, abi=BEANSTALK_ABI)
    beanstalkPrice = web3.eth.contract(BEANSTALK_PRICE, abi=BEANSTALK_PRICE_ABI)
    bean = web3.eth.contract(BEAN_CONTRACT, abi=BEAN)
    multiCall = web3.eth.contract(MULTICALL_CONTRACT, abi=MULTICALL_ABI)
    
    calldata = [
        (BEAN_CONTRACT,bean.functions.totalSupply().selector), ## bean supply
        (BEANSTALK_CONTRACT, beanstalk.functions.season().selector), # season
        (BEANSTALK_CONTRACT, beanstalk.functions.totalUnharvestable().selector), # podLine
        (BEANSTALK_PRICE, beanstalkPrice.functions.price().selector) # beanstalk price
        ]
    multiData = multiCall.functions.blockAndAggregate(calldata).call()[2]
    supply = web3.to_int(multiData[0][1]) / 1e6
    season = web3.to_int(multiData[1][1])
    podLine = web3.to_int(multiData[2][1])
    price = web3.to_int(multiData[3][1][32:64]) / 1e6
    liquidity = web3.to_int(multiData[3][1][64:96]) / 1e6
    deltaB = web3.to_int(multiData[3][1][96:128])
    deltaB = (deltaB - 2 ** 256) / 1e6 if deltaB > 2 ** 255 else deltaB / 1e6
    podRate = podLine * 100/(supply * 1e6)
    return (
        "Season: " + str(season),
        "Price: " + str(price), 
        "Supply: " + '{0:,.0f}'.format(supply),
        "Liquidity: " + '{0:,.0f}'.format(liquidity),
        "DeltaB: " + '{0:,.0f}'.format(deltaB), 
        "PodRate: " + '{0:,.0f}%'.format(podRate),
        "L2SR: " + '{0:,.2f}%'.format(liquidity * 50 / supply)
    )
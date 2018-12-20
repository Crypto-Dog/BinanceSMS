# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 08:44:59 2018

@author: Crypto-Dog
"""
##############################Imports##########################################
import smtplib
import math
import config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib.request, json
##############################Functions########################################
"""
Purpose: Get total amount of base volume from a list of orders
Parameters:
    orders = order list from Binance
    total = variable to store the total in, initial value should be 0
Return: the total base volume from all orders given
"""
def getTotalBTC(orders, total):
    #Loop through orders
    for x in orders:
        #Add the trading pair volume * trading pair base to the total
        total += float(x[0]) * float(x[1])
    return total
"""
Purpose: Get total amount of trading pair volume from a list of orders
Parameters:
    orders = order list from Binance
    total = variable to store the total in, initial value should be 0
Return: the total volume from all orders given
"""
def getTotalLINK(orders, total):
    #Loop through orders
    for x in orders:
        #Add the trading pair volume to the total
        total += float(x[1])
    return total
"""
Purpose: Get the highest trading pair volume sell from sell side
Parameter:
    orders: sell order list from Binance
Return: A tuple with the price and quantity of the top sell from the sell side
"""
def getTopSell(orders):
    #Define variables to hold top sell and top price and set initailly to 0
    topSell = 0
    topPrice = 0.0
    #Loop through orders
    for x in orders:
        if(float(x[1]) > topSell):
            topSell = float(x[1])
            topPrice = float(x[0])
    return(topPrice, topSell)
"""
Purpose: Get the top trading pair volume candle from a set of klines
Parameter:
    kline = kline from Binance
Return: A tuple with the top trading pair volume from a single candle and the 
time it happened at
"""
def getTopVolume(kline):
    #Define variables to hold top volume and time and set initially to 0
    topVolume = 0
    time_ = 0
    #Loop through klines
    for x in kline:
        if(float(x[5]) > topVolume):
            topVolume = float(x[5])
            time_ = float(x[0])
    return (topVolume, time_)
"""
Purpose: Get the top trading pair buy/sell from a set of klines
Parameter:
    kline = kline from Binance
Return: A tuple with the top market order, the time it happened, if it is a buy
or sell, the high for that candle, the low for that candle
"""
def getTopMarketBuy(kline):
    #Define variables to hold top buy, time, order type, the high, & the low
    topBuy = 0
    time_ = 0
    orderType = 0
    high = 0.0
    low = 0.0
    #Loop through klines
    for x in kline:
        if(float(x[9]) > topBuy or float(x[5]) - float(x[9]) > topBuy):
            topBuy = float(x[9])
            time_ = float(x[0])
            if(float(x[1]) <= float(x[4])): #if open is <= the close
                orderType = 1 #Buy, Green Candle
                high = float(x[2])
            else:
                topBuy = float(x[5]) - float(x[9])
                orderType = 0 #Sell, Red Candle
                low = float(x[3])
    return (topBuy, time_, orderType, high, low)
"""
Purpose: Check a set of klines to see if the trading base volume has doubled
Parameter:
    kline = kline from Binance
Return: A tuple with whether the volume doubled or not, the current volume,
and the previous volume
"""
def checkIfVolumeDoubled(kline):
    #Define variables needed to store data for the function
    doubled = 0
    volume = 0.0
    prevVolume = 0.0
    #Loop through klines
    for x in kline:
        if(volume != 0.0 and float(x[7]) >= 2*prevVolume):
            print("Volume has doubled in the past hour!")
            doubled = 1
        elif(volume != 0.0 and float(x[7]) < 2*prevVolume):
            print("Volume has not doubled in the past hour.")
        else:
            prevVolume = float(x[7])
        volume = float(x[7])
    return (doubled, volume, prevVolume)
"""
Purpose: Check a set of klines to see if the trading base volume has halved
Parameter:
    kline = kline from Binance
Return: A tuple with whether the volume halved or not, the current volume,
and the previous volume
"""
def checkIfVolumeHalved(kline):
    #Define variables needed to store data for the function
    halved = 0
    volume = 0.0
    prevVolume = 0.0
    #Loop through klines
    for x in kline:
        if(volume != 0.0 and float(x[7]) <= prevVolume/2):
            print("Volume has halved in the past hour!")
            halved = 1
        elif(volume != 0.0 and float(x[7]) > prevVolume/2):
            print("Volume has not halved in the past hour.")
        else:
            prevVolume = round(float(x[7]), 8)
        volume = round(float(x[7]), 8)
    return (halved, volume, prevVolume)
"""
Purpose: Check if a price has been hit in a set of klines
Parameters:
    kline = kline from Binance
    price = Price to check
Return: whether or not the price was hit or not
"""
def checkIfPriceHit(kline, price):
    priceHit = 0
    for x in kline:
        #check if price is <= the high and >= the low
        if(price <= float(x[2]) and price >= float(x[3])): 
            priceHit = 1
    return priceHit
"""
Purpose: To send an email
Parameters:
    subject = The subject of the email
    text = The body of the email
    html = HTML code of the text
No Return
"""
def sendEmail(subject, text, html):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = config.EMAIL_ADDRESS
        msg['To'] = config.RECEIVER
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(config.EMAIL_ADDRESS, config.PASSWORD)
        server.sendmail(config.EMAIL_ADDRESS, config.RECEIVER, msg.as_string())
        server.quit()
        print("Success: Email sent!")
    except:
        print("Email failed to send.")
"""
Purpose: Get orderbook data from Binance
Parameters:
    symbol = Orderbook ticker
    limit = max 1000, # of orders to fetch
Return: The JSON response from Binance with all the orderbook data
"""
def getOrderBookData(symbol, limit):
    #Create url to get json from
    url = "https://api.binance.com/api/v1/depth?symbol="
    url += config.SYMBOL
    url += "&limit="
    url += config.LIMIT
    try:
        with urllib.request.urlopen(url) as url:
            data = json.loads(url.read().decode())
        return data
    except:
        print("Failed to fetch LINK order book")
"""
Purpose: Print order book data to terminal
Parameter:
    data = orderbook data from Binance
Return: A tuple with the text and HTML variables needed to send this data as an
email
"""
def printData(data):
    asks_list = data['asks']
    bids_list = data['bids']
    
    asks_length = len(asks_list) - 1

    totalForSaleBTC = 0.0
    totalWantedBTC = 0.0
    totalForSaleLINK = 0
    totalWantedLINK = 0
    topSell = (0.0, 0)
    topSell = getTopSell(asks_list)

    totalForSaleBTC = round(getTotalBTC(asks_list, totalForSaleBTC), 8)
    totalWantedBTC = round(getTotalBTC(bids_list, totalWantedBTC), 8)
    totalWantedLINK = getTotalLINK(bids_list, totalWantedLINK)
    totalForSaleLINK = getTotalLINK(asks_list, totalForSaleLINK)

    text = "Total " + str(config.COIN) + " up for sale = " + "{:,}".format(math.floor(totalForSaleLINK)) + "\n"
    text += "Total " + str(config.TRADING_BASE) + " to buy LINK up for sale = " + str(totalForSaleBTC) + "\n"
    text += "Top sell price available on order book: " + str(asks_list[asks_length][0]) + "\n"
    text += "Top Order: SELL " + "{:,}".format(math.floor(topSell[1])) + " " + str(config.COIN) + " @" + str(topSell[0]) + " " + str(config.TRADING_BASE) + " for a total of " + str(topSell[0]*topSell[1]) + " " + str(config.TRADING_BASE) + "" + "\n"
    text += "Total " + str(config.COIN) + " wanted = " + "{:,}".format(math.floor(totalWantedLINK)) + "\n"
    text += "Total " + str(config.TRADING_BASE) + " to buy wanted " + str(config.COIN) + " = " + str(totalWantedBTC)
    html = """\
    <html>
        <head></head>
        <body>
            <p>Total """ + str(config.COIN) + """\
             up for sale = """ + "{:,}".format(math.floor(totalForSaleLINK)) + """\
                <br>Total """ + str(config.TRADING_BASE) + """\
                 to buy """ + str(config.COIN) + """\
                  up for sale = """ + str(totalForSaleBTC) + """\
                <br>Top sell price available on order book: """ + str(asks_list[asks_length][0]) + """\
                <br>Top Order: SELL """ + "{:,}".format(math.floor(topSell[1])) + """ """ + str(config.COIN) + """ @""" + str(topSell[0]) + """ """ + str(config.TRADING_BASE) + """ for a total of """ + str(topSell[0]*topSell[1]) + """ """ + str(config.TRADING_BASE) + """BTC
                <br>Total """ + str(config.COIN) + """\
                 wanted = """ + "{:,}".format(math.floor(totalWantedLINK)) + """\
                <br>Total """ + str(config.TRADING_BASE) + """\
                to buy wanted """ + str(config.COIN) + """ = """ + str(totalWantedBTC) + """\
            </p>
        </body>
    <html>
    """
    subject = "Binance ["
    subject += str(config.SYMBOL)
    subject += "]: Orderbook Data"
    print(text)
    return (subject, text, html)
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 18:18:24 2018

@author: Crypto-Dog
"""
##############################Imports##########################################
import time
import math
import datetime
import binanceBot
import config
from binance.client import Client
import requests.exceptions
#############################Start Script######################################
#Establish if Binance is up and running
while True:
    try:
        client = Client(config.API_KEY, config.API_SECRET)
        status = client.get_system_status()
    except (requests.ConnectTimeout, requests.ConnectionError, requests.ReadTimeout, requests.HTTPError, requests.Timeout):
        continue
    break
status = status['msg'] #store status message from Binance
if status != 'normal':
    quit() #Only run code if Binance is up and running
else:
    print("All systems go.\n")
#Global Variables
counter = 0
priceHit = 0
singularityBTC = 0
singularityETH = 0
buyBack = 0
buy = 0
sellId = 12345678
buyId = 87654321
singularityIdBTC = 18273645
singularityIdETH = 81726354
#Start infinite loop
while counter != -1:
    #Get orderbook data and print it out
    data = binanceBot.getOrderBookData(config.SYMBOL, config.LIMIT)
    email = binanceBot.printData(data)

    #Get 1m klines from last 5 minutes
    while True:
        try:
            link = client.get_historical_klines(symbol=config.SYMBOL, interval='1m', start_str="5 minute ago UTC")
        except (requests.ConnectTimeout, requests.ConnectionError, requests.ReadTimeout, requests.HTTPError, requests.Timeout):
            continue
        break

    #Only run this code if the SELL_TRIGGER has not been hit yet
    if(priceHit != 2):
        #Check if SELL_TRIGGER price has been hit, 1 = yet, 0 = no
        priceHit = binanceBot.checkIfPriceHit(link, float(config.SELL_TRIGGER))
        #Price was hit...
        if(priceHit == 1):
            print(float(config.SELL_TRIGGER), "was hit!")
            #Setup email
            text = "Sell trigger price hit " + str(config.SELL_TRIGGER) + " " + str(config.TRADING_BASE)
            text += ". Your order to sell " + str(config.TRADING_ALLOWANCE) + " " + str(config.COIN) + "@" + str(config.TARGET_PRICE) + " BTC"
            text += " has been placed!"
            html = """\
            <html>
                <head></head>
                <body>
                    <p>Sell trigger price hit """ + str(config.SELL_TRIGGER) + """\
                    BTC. Your order to sell """ + str(config.TRADING_ALLOWANCE) + """\
                     """ + str(config.COIN) + """\
                     @""" + str(config.TARGET_PRICE) + """\
                     """ + str(config.TRADING_BASE) + """\
                     has been placed!</p>
                </body>
            </html>
            """
            subject = "Binance ["
            subject += str(config.SYMBOL)
            subject += "]: Sell Triggered!"
            #Place sell order and store orderId
            while True:
                try:
                    order = client.order_limit_sell(
                            symbol=config.SYMBOL,
                            quantity=math.floor(float(config.TRADING_ALLOWANCE)),
                            price=config.TARGET_PRICE)
                except (requests.ConnectTimeout, requests.ConnectionError, requests.ReadTimeout, requests.HTTPError, requests.Timeout):
                    continue
                break
            sellId = order['orderId']
            #Flip priceHit switch
            priceHit = 2
            #Flip buyBack switch on
            buyBack = 1
            print("Sell order placed!")
            #Send email
            binanceBot.sendEmail(subject, text, html)
        else:
            print(config.SELL_TRIGGER, str(config.TRADING_BASE) + " was not hit")
    #Sell was triggered...
    if(buyBack == 1):
        #Get the status of the sell order
        while True:
            try:
                status = client.get_order(
                        symbol=config.SYMBOL,
                        orderId=sellId)
            except (requests.ConnectTimeout, requests.ConnectionError, requests.ReadTimeout, requests.HTTPError, requests.Timeout):
                continue
            break
        #Check if the sell order has been filled
        if(status['status'] == 'FILLED'):
            print("Sell order was filled!")
            #Calculate free balance of trading base (coin gained from the trade) and set buyback order and store orderId
            while True:
                try:
                    balance = client.get_asset_balance(asset=config.TRADING_BASE)
                except (requests.ConnectTimeout, requests.ConnectionError, requests.ReadTimeout, requests.HTTPError, requests.Timeout):
                    continue
                break
            free = float(balance['free'])
            buy = math.floor(free/float(config.BUYBACK_PRICE))
            while True:
                try:
                    order = client.order_limit_buy(
                            symbol=config.SYMBOL,
                            quantity=buy,
                            price=config.BUYBACK_PRICE)
                except (requests.ConnectTimeout, requests.ConnectionError, requests.ReadTimeout, requests.HTTPError, requests.Timeout):
                    continue
                break
            buyId = order['orderId']
            #Setup email
            text = "Sell order at " + str(config.TARGET_PRICE) + " " + str(config.TRADING_BASE) + " for " + str(config.TRADING_ALLOWANCE) + " " + str(config.COIN) + " has been filled!\n"
            text += "Buy order for " + str(buy) + " " + str(config.COIN) + " @" + str(config.BUYBACK_PRICE) + " " + str(config.TRADING_BASE) + " has been placed!"
            html = """\
            <html>
                <head></head>
                <body>
                    <p>Sell order at """ + str(config.TARGET_PRICE) + """\
                      """ + str(config.TRADING_BASE) + """\
                     for """ + str(config.TRADING_ALLOWANCE) + """\
                      """ + str(config.COIN) + """\
                     has been filled!<br>Buy order for """ + str(buy) + """\
                      """ + str(config.COIN) + """\
                      @ """ + str(config.BUYBACK_PRICE) + """\
                      """ + str(config.TRADING_BASE) + """\
                     has been placed!</p>
                </body>
            </html>
            """
            subject = "Binance ["
            subject += str(config.SYMBOL)
            subject += "]: Sell Order Filled! Buyback Order Placed!"
            binanceBot.sendEmail(subject, text, html)
            #Flip buyBack switch
            buyBack = 2
            print("Buy order placed!")
        print("Sell was triggered. Waiting for sell to fill...")
    #Sell was filled, buy order placed...
    if(buyBack == 2):
        #Get status of buyback order
        while True:
            try:
                status = client.get_order(
                        symbol=config.SYMBOL,
                        orderId=buyId)
            except (requests.ConnectTimeout, requests.ConnectionError, requests.ReadTimeout, requests.HTTPError, requests.Timeout):
                continue
            break
        #Check if buyback order has been filled
        if(status['status'] == 'FILLED'):
            print("Buy order filled!")
            #Calculate total gained LINK
            total = buy - int(config.TRADING_ALLOWANCE)
            #Setup email and send it
            text = "Your order to buy back " + str(buy) + " " + str(config.COIN) + " @" + str(config.BUYBACK_PRICE) + " " + str(config.TRADING_BASE) + " has been filled!\n"
            text += "You gained " + str(total) + " " + str(config.COIN) + "!"
            html = """\
            <html>
                <head></head>
                <body>
                    <p>Your order to buy back  """ + str(buy) + """\
                       """ + str(config.COIN) + """\
                      @ """ + str(config.BUYBACK_PRICE) + """\
                       """ + str(config.TRADING_BASE) + """\
                      has been filled!<br>You gained """ + str(total) + """\
                       """ + str(config.COIN) + """\
                      !</p>
                </body>
            </html>
            """
            subject = "Binance ["
            subject += str(config.SYMBOL)
            subject += "]: Buy Order Filled!"
            binanceBot.sendEmail(subject, text, html)
            #Flip buyBack switch
            buyBack = 3
        print("Sell was filled. Awaiting buyback order to fill...")
    ###################CHECK IF SINGULARITY PRICE HAS BEEN HIT#################
    if(singularityBTC != 2):
        #Check to see if the price singularity has been hit, 1 = yes, 0 = no
        singularityBTC = binanceBot.checkIfPriceHit(link, float(config.SINGULARITY_BTC))
        if(singularityBTC == 1):
            print(float(config.SINGULARITY_BTC), str(config.TRADING_BASE) + " was hit!")
            #Setup email
            text = "The " + str(config.COIN) + " Price Singulariy has occured! An order to sell " + str(config.SINGULARITY_TRADING_ALLOWANCE) + " " + str(config.COIN) + ""
            text += " @" + str(config.SINGULARITY_BTC) + " " + str(config.TRADING_BASE) + " has been placed!"
            html = """\
            <html>
                <head></head>
                <body>
                    <p>The """ + str(config.COIN) + """\
                     Price Singulariy has occured! An order to sell """ + str(config.SINGULARITY_TRADING_ALLOWANCE) + """\
                    """ +str(config.COIN) + """\
                    @ """ + str(config.SINGULARITY_BTC) + """\
                    """ + str(config.TRADING_BASE) + """\
                     has been placed!</p>
                </body>
            </html>
            """
            subject = "Binance ["
            subject += str(config.SYMBOL)
            subject += "]: THE PRICE SINGULARITY HAS HIT!"
            #Place order to sell LINK @ price singularity, don't place it before singularity is reached so order book remains thin -__-
            while True:
                try:
                    order = client.order_limit_sell(
                            symbol=config.SYMBOL,
                            quantity=math.floor(float(config.SINGULARITY_TRADING_ALLOWANCE)),
                            price=config.SINGULARITY_BTC)
                except (requests.ConnectTimeout, requests.ConnectionError, requests.ReadTimeout, requests.HTTPError, requests.Timeout):
                    continue
                break
            singularityIdBTC = order['orderId']
            binanceBot.sendEmail(subject, text, html)
            singularityBTC = 2
        else:
            print(config.SINGULARITY_BTC, str(config.TRADING_BASE) + " was not hit")
    if(singularityBTC == 2):
        #Get status of buyback order
        while True:
            try:
                status = client.get_order(
                        symbol=config.SYMBOL,
                        orderId=singularityIdBTC)
            except (requests.ConnectTimeout, requests.ConnectionError, requests.ReadTimeout, requests.HTTPError, requests.Timeout):
                continue
            break
        #Check if singularity order has been filled
        if(status['status'] == 'FILLED'):
            print("YOU'RE RICH! SINGULARITY ORDER FILLED!")
            #Setup email and send it
            text = "Your order to sell " + str(config.SINGULARITY_TRADING_ALLOWANCE) + " " + str(config.COIN) + ""
            text += " @" + str(config.SINGULARITY_BTC) + " " + str(config.TRADING_BASE) + " has been filled!"
            html = """\
            <html>
                <head></head>
                <body>
                    <p>Your order to sell """ + str(config.SINGULARITY_TRADING_ALLOWANCE) + """\
                    """ + str(config.COIN) + """\
                     @ """ + str(config.SINGULARITY_BTC) + """\
                    """ + str(config.TRADING_BASE) + """\
                     has been filled!</p>
                </body>
            </html>
            """
            subject = "Binance ["
            subject += str(config.SYMBOL)
            subject += "]: YOU'RE RICH!"
            binanceBot.sendEmail(subject, text, html)
            singularityBTC = 3
    #Only run this code if the price singualarity hasn't been hit
    if(singularityETH != 2):
        #Check to see if the price singularity has been hit, 1 = yes, 0 = no
        singularityETH = binanceBot.checkIfPriceHit(link, float(config.SINGULARITY_ETH))
        if(singularityETH == 1):
            print(float(config.SINGULARITY_ETH), str(config.TRADING_BASE_) + " was hit!")
            #Setup email
            text = "The " + str(config.COIN) + " Price Singulariy has occured! An order to sell " + str(config.SINGULARITY_TRADING_ALLOWANCE) + " " + str(config.COIN) + ""
            text += " @" + str(config.SINGULARITY_ETH) + " " + str(config.TRADING_BASE) + " has been placed!"
            html = """\
            <html>
                <head></head>
                <body>
                    <p>The """ + str(config.COIN) + """\
                     Price Singulariy has occured! An order to sell """ + str(config.SINGULARITY_TRADING_ALLOWANCE) + """\
                    """ +str(config.COIN) + """\
                    @ """ + str(config.SINGULARITY_ETH) + """\
                    """ + str(config.TRADING_BASE) + """\
                     has been placed!</p>
                </body>
            </html>
            """
            subject = "Binance ["
            subject += str(config.SYMBOL)
            subject += "]: THE" + str(config.TRADING_BASE_) + " PRICE SINGULARITY HAS HIT!"
            #Place order to sell LINK @ price singularity, don't place it before singularity is reached so order book remains thin -__-
            while True:
                try:
                    order = client.order_limit_sell(
                            symbol=config.SYMBOL_,
                            quantity=math.floor(float(config.SINGULARITY_TRADING_ALLOWANCE)),
                            price=config.SINGULARITY_ETH)
                except (requests.ConnectTimeout, requests.ConnectionError, requests.ReadTimeout, requests.HTTPError, requests.Timeout):
                    continue
                break
            singularityIdETH = order['orderId']
            binanceBot.sendEmail(subject, text, html)
            singularityBTC = 2
        else:
            print(config.SINGULARITY_ETH, str(config.TRADING_BASE_) + " was not hit")
    if(singularityETH == 2):
        #Get status of buyback order
        while True:
            try:
                status = client.get_order(
                        symbol=config.SYMBOL,
                        orderId=singularityIdETH)
            except (requests.ConnectTimeout, requests.ConnectionError, requests.ReadTimeout, requests.HTTPError, requests.Timeout):
                continue
            break
        #Check if singularity order has been filled
        if(status['status'] == 'FILLED'):
            print("YOU'RE RICH! SINGULARITY ORDER FILLED!")
            #Setup email and send it
            text = "Your order to sell " + str(config.SINGULARITY_TRADING_ALLOWANCE) + " " + str(config.COIN) + ""
            text += " @" + str(config.SINGULARITY_ETH) + " " + str(config.TRADING_BASE_) + " has been filled!"
            html = """\
            <html>
                <head></head>
                <body>
                    <p>Your order to sell """ + str(config.SINGULARITY_TRADING_ALLOWANCE) + """\
                    """ + str(config.COIN) + """\
                     @ """ + str(config.SINGULARITY_ETH) + """\
                    """ + str(config.TRADING_BASE_) + """\
                     has been filled!</p>
                </body>
            </html>
            """
            subject = "Binance ["
            subject += str(config.SYMBOL)
            subject += "]: YOU'RE RICH!"
            binanceBot.sendEmail(subject, text, html)
            singularityETH = 3
    #Get current time for volume check
    currentTime = datetime.datetime.now()
    ###################CHECK FOR LARGE MARKET BUYS/SELLS#######################
    if(currentTime.minute == 0 or currentTime.minute == 5 or currentTime.minute == 10 or currentTime.minute == 15 or currentTime.minute == 20 or currentTime.minute == 25 or currentTime.minute == 30 or currentTime.minute == 35 or currentTime.minute == 40 or currentTime.minute == 45 or currentTime.minute == 50 or currentTime.minute == 55):
        #Get the top volume candle and top market buy/sell
        topVolume = binanceBot.getTopVolume(link)
        topMarketBuy = binanceBot.getTopMarketBuy(link)
        print("Top volume 1m candle:", topVolume[0])
        #1 = Green candle
        if(topMarketBuy[2] == 1):
            print("Someone market bought", "{:,}".format(math.floor(topMarketBuy[0])), str(config.COIN))
        else:
            print("Someone market sold", "{:,}".format(math.floor(topMarketBuy[0])), str(config.COIN))
        #Check if top market buy in the past 5 minutes is >= to MARKET_TRACKER, green candle
        if(topMarketBuy[0] >= float(config.MARKET_TRACKER) and topMarketBuy[2] == 1):
            print("BIG MOVEMENT!")
            #Setup and send email
            text = "Someone market bought " + "{:,}".format(math.floor(topMarketBuy[0])) + " " + str(config.COIN) + ""
            text += " and sent the price to " + str(topMarketBuy[3]) + " " + str(config.TRADING_BASE)
            html = """\
            <html>
            <head></head>
            <body>
                <p>Someone market bought """ + "{:,}".format(math.floor(topMarketBuy[0])) + """\
                 """ + str(config.COIN) + """\
                  and sent the price to """ + str(topMarketBuy[3]) +"""\
                 """ + str(config.TRADING_BASE) + """\
                 </p>
            </body>
            </html>
            """
            subject = "Binance ["
            subject += str(config.SYMBOL)
            subject += "]: Big Market Buy!"
            binanceBot.sendEmail(subject, text, html)
        #Check if top market buy in the past 5 minutes is >= to MARKET_TRACKER, red candle
        elif(topMarketBuy[0] >= float(config.MARKET_TRACKER) and topMarketBuy[2] == 0):
            print("BIG MOVEMENT")
            #Setup and send email
            text = "Someone market sold " + "{:,}".format(math.floor(topMarketBuy[0])) + " " + str(config.COIN) + ""
            text += " and sent the price to " + str(topMarketBuy[4]) + " " + str(config.TRADING_BASE)
            html = """\
            <html>
            <head></head>
            <body>
                <p>Someone market sold """ + "{:,}".format(math.floor(topMarketBuy[0])) + """\
                 """ + str(config.COIN) + """\
                  and sent the price to """ + str(topMarketBuy[4]) +"""\
                 """ + str(config.TRADING_BASE) + """\
                 </p>
            </body>
            </html>
            """
            subject = "Binance ["
            subject += str(config.SYMBOL)
            subject += "]: Big Market Sell!"
            binanceBot.sendEmail(subject, text, html)
        else:
            print("No big movement.")
    ###########################CHECK HOURLY VOLUME#############################
    if(currentTime.minute == 59):
        #Get volume from past 2 hours
        while True:
            try:
                volume = client.get_historical_klines(symbol=config.SYMBOL, interval='1h', start_str="2 hours ago UTC")
            except (requests.ConnectTimeout, requests.ConnectionError, requests.ReadTimeout, requests.HTTPError, requests.Timeout):
                continue
            break
        volumeDoubled = binanceBot.checkIfVolumeDoubled(volume)
        #Check if volume doubled...
        if(volumeDoubled[0] == 1):
            #Setup and send email
            text = str(config.COIN) + " volume has doubled in the past hour!"
            text += " Current hourly volume is: "
            text += str(volumeDoubled[1])
            text += " " + str(config.TRADING_BASE) + ". Previous volume was: "
            text += str(volumeDoubled[2]) + " " + str(config.TRADING_BASE) + "."
            html = """\
            <html>
            <head></head>
            <body>
                <p>""" + str(config.COIN) + """\
                 volume has doubled in the past hour! Current hourly volume is """ + str(volumeDoubled[1]) + """\
                 """ + str(config.TRADING_BASE) + """\
                 . Previous volume was """ + str(volumeDoubled[2]) + """\
                 """ + str(config.TRADING_BASE) + """\
                 .</p>
            </body>
            <html>
            """
            subject = "Binance ["
            subject += str(config.SYMBOL)
            subject += "]: Hourly Volume Doubled!"
            binanceBot.sendEmail(subject, text, html)
        volumeHalved = binanceBot.checkIfVolumeHalved(volume)
        #Check if volume halved...
        if(volumeHalved[0] == 1):
            #Setup and send email
            text = str(config.COIN) + " volume has halved in the past hour!"
            text += " Current hourly volume is: "
            text += str(volumeHalved[1])
            text += " " + str(config.TRADING_BASE) + ". Previous volume was: "
            text += str(volumeDoubled[2]) + " " + str(config.TRADING_BASE) + "."
            html = """\
            <html>
            <head></head>
            <body>
                <p>""" + str(config.COIN) + """\
                volume has halved in the past hour! Current hourly volume is """ + str(volumeHalved[1]) + """\
                """ + str(config.TRADING_BASE) + """\
                . Previous volume was """ + str(volumeHalved[2]) + """\
                 """ + str(config.TRADING_BASE) + """\
                 .</p>
            </body>
            <html>
            """
            subject = "Binance ["
            subject += str(config.SYMBOL)
            subject += "]: Hourly Volume Halved!"
            binanceBot.sendEmail(subject, text, html)
    ###########################CHECK DAILY VOLUME##############################
    if(currentTime.hour == 23 and currentTime.minute == 59):
        print("Checking if daily volume has doubled/halved...")
         #Get volume from past 2 days
        while True:
            try:
                volume = client.get_historical_klines(symbol=config.SYMBOL, interval='1d', start_str="2 days ago UTC")
            except (requests.ConnectTimeout, requests.ConnectionError, requests.ReadTimeout, requests.HTTPError, requests.Timeout):
                continue
            break
        volumeDoubled = binanceBot.checkIfVolumeDoubled(volume)
        #Check if volume doubled...
        if(volumeDoubled[0] == 1):
            #Setup and send email
            text = str(config.COIN) + " volume has doubled in the past day!"
            text += " Current dailyly volume is: "
            text += str(volumeDoubled[1])
            text += " " + str(config.TRADING_BASE) + ". Previous volume was: "
            text += str(volumeDoubled[2]) + " " + str(config.TRADING_BASE) + "."
            html = """\
            <html>
            <head></head>
            <body>
                <p>""" + str(config.COIN) + """\
                 volume has doubled in the past day! Current daily volume is """ + str(volumeDoubled[1]) + """\
                 """ + str(config.TRADING_BASE) + """\
                 . Previous volume was """ + str(volumeDoubled[2]) + """\
                 """ + str(config.TRADING_BASE) + """\
                 .</p>
            </body>
            <html>
            """
            subject = "Binance ["
            subject += str(config.SYMBOL)
            subject += "]: Daily Volume Doubled!"
            binanceBot.sendEmail(subject, text, html)
        volumeHalved = binanceBot.checkIfVolumeHalved(volume)
        #Check if volume halved...
        if(volumeHalved[0] == 1):
            #Setup and send email
            text = str(config.COIN) + " volume has halved in the past day!"
            text += " Current daily volume is: "
            text += str(volumeHalved[1])
            text += " " + str(config.TRADING_BASE) + ". Previous volume was: "
            text += str(volumeDoubled[2]) + " " + str(config.TRADING_BASE) + "."
            html = """\
            <html>
            <head></head>
            <body>
                <p>""" + str(config.COIN) + """\
                volume has halved in the past day! Current volume is """ + str(volumeHalved[1]) + """\
                """ + str(config.TRADING_BASE) + """\
                . Previous volume was """ + str(volumeHalved[2]) + """\
                 """ + str(config.TRADING_BASE) + """\
                 .</p>
            </body>
            <html>
            """
            subject = "Binance ["
            subject += str(config.SYMBOL)
            subject += "]: Daily Volume Halved!"
            binanceBot.sendEmail(subject, text, html)
    ###########################CHECK WEEKLY VOLUME#############################
    #Get day number for when Binance weekly candles start/end
    while True:
        try:
            volumeWeek = client.get_historical_klines(symbol=config.SYMBOL, interval='1w', start_str="2 weeks ago UTC")
        except (requests.ConnectTimeout, requests.ConnectionError, requests.ReadTimeout, requests.HTTPError, requests.Timeout):
            continue
        break
    timestamp = volumeWeek[1][6]
    date = datetime.datetime.fromtimestamp(timestamp / 1e3)
    week = date.day
    if(currentTime.hour == 23 and currentTime.minute == 59 and currentTime.day == week):
        print("Checking if weekly volume has doubled/halved...")
         #Get volume from past 2 days
        while True:
            try:
                volume = client.get_historical_klines(symbol=config.SYMBOL, interval='1w', start_str="2 weeks ago UTC")
            except (requests.ConnectTimeout, requests.ConnectionError, requests.ReadTimeout, requests.HTTPError, requests.Timeout):
                continue
            break
        volumeDoubled = binanceBot.checkIfVolumeDoubled(volume)
        #Check if volume doubled...
        if(volumeDoubled[0] == 1):
            #Setup and send email
            text = str(config.COIN) + " volume has doubled in the past day!"
            text += " Current weekly volume is: "
            text += str(volumeDoubled[1])
            text += " " + str(config.TRADING_BASE) + ". Previous volume was: "
            text += str(volumeDoubled[2]) + " " + str(config.TRADING_BASE) + "."
            html = """\
            <html>
            <head></head>
            <body>
                <p>""" + str(config.COIN) + """\
                 volume has doubled in the past day! Current weekly volume is """ + str(volumeDoubled[1]) + """\
                 """ + str(config.TRADING_BASE) + """\
                 . Previous volume was """ + str(volumeDoubled[2]) + """\
                 """ + str(config.TRADING_BASE) + """\
                 .</p>
            </body>
            <html>
            """
            subject = "Binance ["
            subject += str(config.SYMBOL)
            subject += "]: Weekly Volume Doubled!"
            binanceBot.sendEmail(subject, text, html)
        volumeHalved = binanceBot.checkIfVolumeHalved(volume)
        #Check if volume halved...
        if(volumeHalved[0] == 1):
            #Setup and send email
            text = str(config.COIN) + " volume has halved in the past day!"
            text += " Current weekly volume is: "
            text += str(volumeHalved[1])
            text += " " + str(config.TRADING_BASE) + ". Previous volume was: "
            text += str(volumeDoubled[2]) + " " + str(config.TRADING_BASE) + "."
            html = """\
            <html>
            <head></head>
            <body>
                <p>""" + str(config.COIN) + """\
                volume has halved in the past day! Current volume is """ + str(volumeHalved[1]) + """\
                """ + str(config.TRADING_BASE) + """\
                . Previous volume was """ + str(volumeHalved[2]) + """\
                 """ + str(config.TRADING_BASE) + """\
                 .</p>
            </body>
            <html>
            """
            subject = "Binance ["
            subject += str(config.SYMBOL)
            subject += "]: Weekly Volume Halved!"
            binanceBot.sendEmail(subject, text, html)
    #Print and new line and sleep for desired time
    print()
    time.sleep(int(config.CHECK_EVERY))
    #Bump counter, will be used in the future...
    counter = counter + 1
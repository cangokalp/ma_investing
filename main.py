import pdb
import yfinance as yf
import numpy as np
import pandas as pd
from prettytable import PrettyTable

def calculator(stockName, period='720d'):

    stock = yf.Ticker(stockName)

    hist = stock.history(interval="1d", period=period)

    hist = hist.reset_index()
    hist["MA_50"] = hist['Close'].rolling(window=50).mean()
    hist["MA_200"] = hist['Close'].rolling(window=200).mean()

    hist['Close_vs_MA_50'] = np.where(hist['Close'] > hist['MA_50'], 'Higher', 'Lower')
    hist['Close_vs_MA_200'] = np.where(hist['Close'] > hist['MA_200'], 'Higher', 'Lower')

    hist = hist.dropna()

    # Shift the Close_vs_MA_50 column by one row and compare it with the original column
    hist['Flip'] = np.where((hist['Close_vs_MA_50'] != hist['Close_vs_MA_50'].shift(1)) | (hist['Close_vs_MA_200'] != hist['Close_vs_MA_200'].shift(1)), 'Yes', 'No')
    hist["Flip50"] = np.where(hist['Close_vs_MA_50'] != hist['Close_vs_MA_50'].shift(1), 'Yes', 'No')

    hist = hist.reset_index()
    hist.loc[0, "Flip"] = "No"

    flipDF = hist[hist['Flip'] == 'Yes']

    initialMoney = 1000
    buyPrice = 0
    holdingStock = False
    stockCount = 0
    firstBuyPrice= 0
    lastSellPrice = 0

    for index,row in flipDF.iterrows():
        if(not holdingStock and (row["Close_vs_MA_50"] == 'Higher'  or row["Close_vs_MA_200"] == 'Higher')):

            if row["Flip50"] == "Yes":
               if row['Open'] > row["MA_50"] * 1.15:
                    print("pass gectim beyler" ,  row[['Date', 'Close', 'MA_50']])
                    continue
            else:
                if row['Open'] > row["MA_200"] * 1.15:
                    print("pass gectim beyler" , row[['Date', 'Close', 'MA_200']])
                    continue


            if row["Flip50"] == 'Yes':
                if row['Open'] < row["MA_50"]:
                    # print("buying ", row[['Date', 'Close', 'MA_50']], row["Close"] / row["MA_50"])
                    price = row["MA_50"]

                    stockCount = initialMoney / price
                    firstBuyPrice = price if firstBuyPrice == 0 else firstBuyPrice
                else:
                    stockCount = initialMoney / row['Open']
                    firstBuyPrice = row['Open'] if firstBuyPrice == 0 else firstBuyPrice
            else:
                if row['Open'] < row["MA_200"]:
                    # print("buying " , row[['Date', 'Close', 'MA_200']], row["Close"] / row["MA_200"])
                    price = row["MA_200"]

                    stockCount = initialMoney / price
                    firstBuyPrice = price if firstBuyPrice == 0 else firstBuyPrice
                else:
                    stockCount = initialMoney / row['Open']
                    firstBuyPrice = row['Open'] if firstBuyPrice == 0 else firstBuyPrice


            holdingStock = True
            # print("buying" , row[['Date', 'Open', 'Close', 'MA_50', 'MA_200', "Flip50"]])
        elif(holdingStock and (row["Close_vs_MA_50"] == 'Lower' or row["Close_vs_MA_200"] == 'Lower') ):


            if row["Flip50"]  == 'Yes' :

                if row['Close'] <  row["MA_50"] and row['Open'] >  row["MA_50"]:
                    # print("selling  ", row[['Date', 'Close', 'Open', 'MA_50']], row["MA_50"]/row["Close"])

                    price = row["MA_50"]

                    initialMoney = price * stockCount
                    lastSellPrice = price
                else:
                    initialMoney = row['Open'] * stockCount
                    lastSellPrice =  row['Open']

            else:
                if row['Close'] <  row["MA_200"] and row['Open'] >  row["MA_200"]:
                    # print("selling  ", row[['Date', 'Close', 'MA_200']], row["MA_200"]/row["Close"])

                    price = row["MA_200"]

                    initialMoney = price * stockCount
                    lastSellPrice = price
                else:
                    initialMoney = row['Open'] * stockCount
                    lastSellPrice = row['Open']


            holdingStock = False
            # print("hareket deltasi", initialMoney - currentPrice, initialMoney)
            # print("selling" ,  row[['Date', 'Open','Close', 'MA_50', 'MA_200']])


    # print(firstBuyPrice)
    # print(lastSellPrice)
    t = PrettyTable(['Stock', 'RoboLong', 'Buy&Hold'])
    t.add_row([stockName, "{:.2%}".format((initialMoney - 1000)/ 1000), "{:.2%}".format((lastSellPrice - firstBuyPrice) /  firstBuyPrice)])
    print(t)
    # print(stockName, initialMoney - 1000, initialMoney, (initialMoney - 1000)/ 1000 * 100, (lastSellPrice - firstBuyPrice) /  firstBuyPrice * 100)

sp500_df = pd.read_csv("sp500.txt", sep=",")
stock_tickers = sp500_df["Symbol"].values

pdb.set_trace()
calculator("TGT")
calculator("ICAGY")
calculator("AAPL")
calculator("ICAGY")
calculator("UAL")
calculator("LULU")
calculator("MMM")
calculator("DIS")
calculator("SBUX")
calculator("LUV")
calculator("DAL")
calculator("U")
calculator("UBER")
calculator("PLTR")
calculator("TSLA")
calculator("UNG")
calculator("NVDA")
calculator("RYCEY")
calculator("PINS")
calculator("NET")
calculator("GM")
calculator("GE")
calculator("BA")
calculator("INTC")
calculator("ADBE")
calculator("UPST")
calculator("GOOG")
calculator("AMZN")
calculator("EXPE")


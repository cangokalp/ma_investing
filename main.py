import pdb
import yfinance as yf
import numpy as np
import pandas as pd
from prettytable import PrettyTable

def calculator(stockList, period='400d' , wantShort = False):

    profitList = []
    endMoneyList = []
    mrAndersonGainList = []
    buyandholdList = []
    firstbuypricelist = []
    firstbuydatelist = []
    lastsalepricelist = []
    lastsalepricedate = []
    actionCountList = []
    close2actionlist = []

    for stockName in stockList:

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
        # hist['Flip'] = np.where((hist['Close_vs_MA_200'] != hist['Close_vs_MA_200'].shift(1)), 'Yes', 'No')
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
        holdingShort = False
        shortCount = 0
        firstBuyDate = 0
        actionCount = 0


        flipDF = flipDF.reset_index(drop=True)

        for index,row in flipDF.iterrows():

            date = row["Date"]



            if(not holdingStock and (row["Close_vs_MA_50"] == 'Higher'  or row["Close_vs_MA_200"] == 'Higher')): # alis


                if row["Flip50"] == "Yes":
                   if row['Open'] > row["MA_50"] * 1.15:
                        continue
                else:
                    if row['Open'] > row["MA_200"] * 1.15:
                        continue


                if row["Flip50"] == 'Yes':
                    # print("buying " , row[['Date', 'Close', 'MA_50']], row["Close"] / row["MA_50"])
                    price =  row["MA_50"] if row['Open'] < row["MA_50"] else row['Open']
                    shortProfit = 0 if not holdingShort else initialMoney - price * shortCount
                    initialMoney = initialMoney + shortProfit
                    stockCount = initialMoney / price


                else:
                    # print("buying " , row[['Date', 'Close', 'MA_200']], row["Close"] / row["MA_200"])
                    price =  row["MA_200"] if row['Open'] < row["MA_200"] else row['Open']
                    shortProfit = 0 if not holdingShort else initialMoney -  price * shortCount
                    initialMoney = initialMoney + shortProfit
                    stockCount = initialMoney / price

                firstBuyPrice = price if firstBuyPrice == 0 else firstBuyPrice
                firstBuyDate = date if firstBuyDate == 0 else firstBuyDate

                shortCount = 0
                holdingShort = False
                holdingStock = True

                actionCount += 1



                # print("buying" , row[['Date', 'Open', 'Close', 'MA_50', 'MA_200', "Flip50"]])
            elif(holdingStock and (row["Close_vs_MA_50"] == 'Lower' or row["Close_vs_MA_200"] == 'Lower') ):
                if row["Flip50"]  == 'Yes' :
                    if  row['Open'] >  row["MA_50"]:
                        # print("selling  ", row[['Date', 'Close', 'Open', 'MA_50']], row["MA_50"]/row["Close"])

                        price = row["MA_50"]
                        initialMoney = price * stockCount
                        lastSellPrice = price
                        shortCount = initialMoney/ price

                    else:
                        initialMoney = row['Open'] * stockCount
                        lastSellPrice =  row['Open']
                        shortCount = initialMoney/ row['Open']


                else:
                    if row['Open'] >  row["MA_200"]:
                        # print("selling  ", row[['Date', 'Close', 'MA_200']], row["MA_200"]/row["Close"])
                        price = row["MA_200"]
                        initialMoney = price * stockCount
                        lastSellPrice = price
                        shortCount = initialMoney/ price

                    else:
                        initialMoney = row['Open'] * stockCount
                        lastSellPrice = row['Open']
                        shortCount = initialMoney/ row['Open']



                holdingStock = False
                holdingShort = wantShort
                # print("hareket deltasi", initialMoney - currentPrice, initialMoney)
                # print("selling" ,  row[['Date', 'Open','Close', 'MA_50', 'MA_200']])
                actionCount += 1

        ##
        last_row = hist.iloc[-1,:]

        price = last_row["Close"]
        date = last_row["Date"]

        if holdingStock:
            initialMoney = price * stockCount
            lastSellPrice = price

        else:
            shortProfit = 0 if not holdingShort else initialMoney - price * shortCount
            initialMoney = initialMoney + shortProfit




        close2actionlist.append(min(abs(last_row["MA_50"] - last_row["Close"])/last_row["Close"], abs(last_row["MA_200"] - last_row["Close"])/last_row["Close"]))
        firstbuypricelist.append(firstBuyPrice)
        firstbuydatelist.append(firstBuyDate)
        lastsalepricelist.append(lastSellPrice)
        lastsalepricedate.append(date)
        profitList.append(initialMoney - 1000)
        endMoneyList.append(initialMoney)
        mrAndersonGainList.append("{:.2%}".format((initialMoney - 1000)/ 1000))
        buyandholdList.append("{:.2%}".format((lastSellPrice - firstBuyPrice) /  firstBuyPrice))
        actionCountList.append(actionCount)


    calc_df = pd.DataFrame({"stockName": stockList,
                            "profit": profitList,
                            "EndMoney": endMoneyList,
                            "Mr.Anderson": mrAndersonGainList,
                            "B&H": buyandholdList,
                            'num_actions': actionCountList,
                            'yakinlik': close2actionlist,
                            "firstBuyPrice": firstbuypricelist,
                            "firstBuyDate": firstbuydatelist,
                            "lastSalePrice": lastsalepricelist,
                            "lastSaleDate": lastsalepricedate
                            })

    # print(firstBuyPrice)
    # print(lastSellPrice)
    #t = PrettyTable(['Stock', 'Mr.Anderson', 'Buy&Hold'])
    #t.add_row([stockName, "{:.2%}".format((initialMoney - 1000)/ 1000), "{:.2%}".format((lastSellPrice - firstBuyPrice) /  firstBuyPrice)])
    #print(t)
    # print(stockName, initialMoney - 1000, initialMoney, (initialMoney - 1000)/ 1000 * 100, (lastSellPrice - firstBuyPrice) /  firstBuyPrice * 100)
    calc_df = calc_df.sort_values(by='yakinlik', ascending=True)
    return calc_df


ticker_list = ['TGT', 'ICAGY', 'AAPL', 'UAL', 'LULU', 'MMM', 'DIS', 'SBUX', 'LUV', 'DAL', 'U', 'UBER', 'PLTR', 'TSLA', 'UNG',
        'NVDA', 'RYCEY', 'PINS', 'NET', 'GM', 'GE', 'BA', 'INTC', 'ADBE', 'UPST', 'GOOG', 'AMZN', 'EXPE', "META", "NFLX",
                "DDOG", 'T', 'AXP', 'UNH']


calc_df = calculator(ticker_list)
print(calc_df)
pdb.set_trace()

# calculator("SPY")
# calculator("TGT")
# calculator("ICAGY")
# calculator("AAPL")
# calculator("ICAGY")
# calculator("UAL")
# calculator("LULU")
# calculator("MMM")
# calculator("DIS")
# calculator("SBUX")
# calculator("LUV")
# calculator("DAL")
# calculator("U")
# calculator("UBER")
# calculator("PLTR")
# calculator("TSLA")
# calculator("UNG")
# calculator("NVDA")
# calculator("RYCEY")
# calculator("PINS")
# calculator("NET")
# calculator("GM")
# calculator("GE")
# calculator("BA")
# calculator("INTC")
# calculator("ADBE")
# calculator("UPST")
# calculator("GOOG")
# calculator("AMZN")
# calculator("EXPE")


# -*- coding: utf-8 -*-
"""Stock Scraper

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12DHn1FKPCfx1f-BkIi_5nqtjg4_jnZiY
"""

import yfinance as yf
import pandas as pd
import shutil
import os 
import glob
import requests
import time
import ssl
import smtplib
import sys
import bs4 as bs

def scrape_tickers():
    #scrape for tickers from s&p500
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    industries = []
    for row in table.findAll('tr')[1:]:
            ticker = row.findAll('td')[0].text
            #fourth element is the sector
            industry = row.findAll('td')[4].text        
            tickers.append(ticker)
            industries.append(industry)
    tickers = list(map(lambda s: s.strip(), tickers))
    industries = list(map(lambda s: s.strip(), industries))
    print("The amount of stocks chosen to observe: " + str(len(tickers)))
    return tickers

def scrape_tickers_info(tickers):
    # These two lines remove the Stocks folder and then recreate it in order to remove old stocks.
    if os.path.isdir("./Stock_Report/Stocks/"):
        shutil.rmtree("./Stock_Report/Stocks/")
    os.mkdir("./Stock_Report/Stocks/")
    # API_Calls = 0
    failure = 0
    # Used to iterate through our list of tickers
    i=0

    while (i < len(tickers)):
        try:
            stock = tickers[i]  
            temp = yf.Ticker(stock)
            hist_data = temp.history(period="1y")  
            hist_data.to_csv("./Stock_Report/Stocks/"+stock+".csv")  
            time.sleep(2) 
            # API_Calls += 1 
            i += 1  
        except ValueError:
            print("Yahoo Error")
            failure += 1
    print("Successfully imported: " + str(i - failure))
    # print("API calls = " + str(API_calls))

def OBV_analysis():
    # OBV Analysis
    stocklist_file = (glob.glob("./Stock_Report/Stocks/*.csv")) 
    new_data = [] 
    i = 0
    while i < len(stocklist_file):
        data = pd.read_csv(stocklist_file[i])
        movement = [] 
        OBV_Value = 0  # Sets the initial OBV_Value to zero
        count = 0
        data = data.tail(10)
        Moving_Average = 0
        if(data.empty == False):
            while (count < 10):  # 10 because we are looking at the last 10 trading days
                Moving_Average += data.iloc[count,4]
                if data.iloc[count,1] < data.iloc[count,4]:  # True if the stock increased in price
                    volume = data.iloc[count,5]/data.iloc[count,1]
                    movement.append(volume)
                elif data.iloc[count,1] > data.iloc[count,4]:  # True if the stock decreased in price
                    volume = data.iloc[count,5]/data.iloc[count,1] * -1
                    movement.append(volume)
                count += 1
            for j in movement:
                OBV_Value = round(OBV_Value + j)
            file_name = os.path.basename(stocklist_file[i])  # Get the name of the current stock we are analyzing
            Stock_Name = file_name.split(".csv")
            Stock_Name = Stock_Name[0]
            Moving_Average = Moving_Average / 10 
            new_data.append([Stock_Name, OBV_Value, Moving_Average])  
        i += 1
    df = pd.DataFrame(new_data, columns = ['Stock', 'OBV_Value', 'Moving_Average'])  # Creates a new dataframe from the new_data list
    df.sort_values("OBV_Value", inplace = True, ascending = False)  # Sort the ranked stocks
    df.to_csv("./Stock_Report/OBV_Ranked.csv", index = False)  # Save the dataframe to a csv without the index column

def big_change():
    stocklist_file = (glob.glob("./Stock_Report/Stocks/*.csv")) 
    pos_move = []
    neg_move = []
    i = 0
    while i < len(stocklist_file):
        data = pd.read_csv(stocklist_file[i])
        if(not data.empty):
            file_name = os.path.basename(stocklist_file[i])  # Get the name of the current stock we are analyzing
            Stock_Name = file_name.split(".csv")
            Stock_Name = Stock_Name[0]
            if data.iloc[count,1] < data.iloc[count,4]:  # True if the stock increased in price
                change = (data.iloc[count,4] / data.iloc[count,1]) - 1
                pos_move.append([Stock_Name, change])
            elif data.iloc[count,1] > data.iloc[count,4]:  # True if the stock decreased in price
                change = (data.iloc[count,4] / data.iloc[count,1]) - 1
                neg_move.append([Stock_Name, change])
        i += 1
    df = pd.DataFrame(pos_move, columns = ['Stock', '% Increase'])  # Creates a new dataframe from the new_data list
    df.sort_values("% Increase", inplace = True, ascending = False)  # Sort the ranked stocks
    df.to_csv("./Stock_Report/% Increase_Ranked.csv", index = False)  # Save the dataframe to a csv without the index column
    df2 = pd.DataFrame(neg_move, columns = ['Stock', '% Decrease'])  # Creates a new dataframe from the new_data list
    df2.sort_values("% Decrease", inplace = True, ascending = False)  # Sort the ranked stocks
    df2.to_csv("./Stock_Report/% Decrease_Ranked.csv", index = False)  # Save the dataframe to a csv without the index column
             
             
if __name__ == "__main__":
    tickers = scrape_tickers() # a list of all the ticker names we scraped
    scrape_tickers_info(tickers) #generate the info on tickers
    #analysis
    if(len(sys.argv) < 2):
        print("Usage: " + str(sys.argv[0]) + " OBV/Change")
        sys.exit(1)
    if(sys.argv[1] == "OBV"):
        OBV_analysis()
    elif(sys.argc[1] == "Change"):
        big_change()
    else:
        print("Usage: " + str(sys.argv[0]) + " OBV/Change")
        sys.exit(1)



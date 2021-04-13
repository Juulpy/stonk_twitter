import tweepy
from collections import Counter
import datetime
from matplotlib import pyplot as plt
import yfinance as yf
import pandas as pd
import numpy as np

'''
Created by KiloDelta

do with it what you want idc but do not use this for investment advice etc
am not responsible
'''

screenName = "TheRoaringKitty" #enter twitter handle here
ticker = "GME" #enter ticker here

api_key = "" #REDACTED LOL
api_secret = "" #this too.

plt.style.use('seaborn')



#Yahoo voodoo
GME = yf.Ticker(ticker)
GME_hist = GME.history(period="1y")

#slice dates
df_dates = list(GME_hist.index)

#slice the closing prices and volume
df_close = list(GME_hist["Close"])
df_volume = list(GME_hist["Volume"])


for i in range(0,len(df_dates)): #convert pandas Timestamps to python datetime
    pdt = df_dates[i].to_pydatetime()
    df_dates[i] = pdt




def get_all_tweets(screen_name): #copied magic to bypass API limit of 200 tweets per call
    #Twitter only allows access to a users most recent 3240 tweets with this method

    #authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(api_key, api_secret)
    api = tweepy.API(auth)

    #initialize a list to hold all the tweepy Tweets
    alltweets = []

    #make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name = screen_name,count=200)

    #save most recent tweets
    alltweets.extend(new_tweets)

    #save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    #keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        print(f"getting tweets before {oldest}")

        #all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)

        #save most recent tweets
        alltweets.extend(new_tweets)

        #update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        print(f"...{len(alltweets)} tweets downloaded so far")

    #transform the tweepy tweets into a 2D array that will populate the csv
    outtweets = [[tweet.id_str, tweet.created_at, tweet.text] for tweet in alltweets]

    return outtweets

all_tweets = get_all_tweets(screenName)


tweet_dates = []
for tweet in all_tweets: #convert dates to YMD format
    tweet_dates.append(tweet[1].strftime('%Y-%m-%d'))

tweetdate_freq = dict(Counter(tweet_dates)) #count how many tweets on each date

#very concisely named variables incoming
values = []
dates=[]
for key,value in tweetdate_freq.items():
    dates.append(datetime.datetime.strptime(key,'%Y-%m-%d' )) #extract YMD dates from the counter
    values.append(value) #extract matching amount of tweets on that date (index of both lists match)

#some copied matplotlib things that plot two graphs in one figure with different y scales.
fig,ax1 = plt.subplots()
color='tab:red'
ax1.set_xlabel('Date')
ax1.set_ylabel('@{name} Tweet Frequency'.format(name=screenName),color=color)
ax1.bar(np.array(dates),np.array(values),color=color)
ax2 = ax1.twinx()

color = 'tab:blue'
ax2.set_ylabel('${ticker} price'.format(ticker=ticker), color=color)
ax2.plot(df_dates,df_close,color=color)

#For volume comparison: unquote the two lines below, quote the two lines above.

#ax2.set_ylabel('${ticker} volume'.format(ticker=ticker), color=color)
#ax2.plot(df_dates,df_volume,color=color)

plt.show()

#from tweepy import Stream
#from tweepy import OAuthHandler
import tweepy
import sys
import json
import time
import datetime
import csv

tweets_file = open('23-06-2018.csv','w')

#consumer key, consumer secret, access token, access secret.
ckey="pOMNpj3Xx4XvE3R05PsaCQvGC"
csecret="Us8BJVVOwZBCUzsS2CcucWKrlTWXBe1DyiH5JUq7arZUkxKGlX"
atoken="1007179644825726976-MAheIsNgl1BD8KHMipFIwKDwVMEkqm"
asecret="UC1TGjitkxcdctIZiWPzv3gmAaDWiwU3ow9VBX3ScOrSi"

auth = tweepy.OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

api = tweepy.API(auth)
keywords = "Bitcoin OR bitcoin"
csvWriter = csv.writer(tweets_file)

c = tweepy.Cursor(api.search,q=keywords, since = "2018-06-22", until = "2018-06-23",lang="en").items()
counter = 0
while True:
    try:
        tweet = c.next()
        all_data = tweet._json
        tweet = all_data["text"]
        tweet = tweet.replace('\n','')
        tweet = tweet.replace('&amp','')
        date = all_data["created_at"]
        dt_object = datetime.datetime.strptime(date,'%a %b %d %X %z %Y')
        dt2_object = datetime.datetime.strftime(dt_object,'%Y-%m-%d %H:%M:%S')
        datetime_object = datetime.datetime.strptime(dt2_object,'%Y-%m-%d %H:%M:%S')
        tweets_file.write(str(datetime_object)+'\t'+tweet+'\n')
        counter += 1
        print(counter)
    except tweepy.TweepError:
        time.sleep(60 * 15)
        continue
    except StopIteration:
        break

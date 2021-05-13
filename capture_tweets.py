import boto3
import json
from datetime import datetime
import calendar
import random
import time
import sys
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

#Variables that contains the user credentials to access Twitter API
consumer_key = 'GvkPbXiIo2RvqHLqWtzNENvF8'
consumer_secret ='J8oRD18WUKSRhWfHVERsc4e6oOtN3gUphLQBuI0qqsGzDZ0JU7'
access_token = '899598739979075585-OgoZ56xPz6fOnnhtT5t4pcv5Eh8gqT3'
access_token_secret = '16dXmH8dCY8uoQR9uSmJPQHqI5ICOEzc0wK8eLpSrE1B2'
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAJczOgEAAAAAvWP%2BRvu%2B8%2BVmKCrqteXFZXduoCo%3DH8X7PeNg81ZuEP4tMuhmbp0yHlOmuTNAQeft7Ob1fUWRxlItRe'


class TweetStreamListener(StreamListener):        
    # on success
    def on_data(self, data):
        # decode json
        tweet = json.loads(data)
        # print(tweet)
        if "text" in tweet.keys():
            payload = {'id': str(tweet['id']),
                                  'tweet': str(tweet['text'].encode('utf8', 'replace')),
                                  'ts': str(tweet['created_at']),
            },
            print(payload)
            try:
                put_response = kinesis_client.put_record(
                                StreamName=stream_name,
                                Data=json.dumps(payload),
                                PartitionKey=str(tweet['user']['screen_name']))
            except (AttributeError, Exception) as e:
                print (e)
                pass
        return True
        
    # on failure
    def on_error(self, status):
        print(status)


stream_name = 'CSP554'  # fill the name of Kinesis data stream you created

if __name__ == '__main__':
    # create kinesis client connection
    kinesis_client = boto3.client('kinesis', 
                                  region_name='us-east-2',  # enter the region
                                  aws_access_key_id='AKIA3QG5W4IX75ORCYOY',  # fill your AWS access key id
                                  aws_secret_access_key='Go7F/RA2FJAls5BuH3yYO5EL39sU9+ZXpKB2gXzt')  # fill you aws secret access key
    # create instance of the tweepy tweet stream listener
    listener = TweetStreamListener()
    # set twitter keys/tokens
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    # create instance of the tweepy stream
    stream = Stream(auth, listener)
    # search twitter for tags or keywords from cli parameters

    # edit here to change from command line interface input to dashboard input
    query = sys.argv[1:] # list of CLI arguments 
    query_fname = ' '.join(query) # string
    stream.filter(track=query)
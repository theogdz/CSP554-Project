# spark_app.py is going to collect the tweets from the stream, preprocess them, and then put into the mllib model to predict its sentiment
# we will create the dataframe with tweet, timestamp, positive sentiment score, negative sentiment score
import pickle
import sys
import time
import numpy as np
import pandas as pd
from pyspark.mllib.classification import (LogisticRegressionModel,
                                          LogisticRegressionWithLBFGS)
from pyspark.mllib.regression import LabeledPoint
from pyspark.sql.types import *
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def send_df_to_dashboard(df):
    sentiment = [str(t.sentiment) for t in df.select("sentiment").collect()]
    sentiments_count = [p.sentiment_count for p in df.select("sentiment_count").collect()]
    url = 'http://localhost:9999/updateData'
    request_data = {'label': str(sentiment).replace('bytearray', ''), 'data': str(sentiment_count)}
    response = requests.post(url, data=request_data)

def parse_tweet(text):
    data = json.loads(text)
    id = data[0]['id']
    ts = data[0]['ts']
    tweet = data[0]['tweet'] 
    return (id, ts, tweet)

analyzer = SentimentIntensityAnalyzer()
def vader(x):
    return analyzer.polarity_scores(x)['compound']

def textblob(x):
    return TextBlob(x).sentiment.polarity

def create_input_tensor(data):
    # labels need to be one hot encoded
    input_tensor = pd.DataFrame()
    input_tensor['vader'] = data['Tweet'].apply(vader)
    input_tensor['textblob'] = data['Tweet'].apply(textblob)

    return input_tensor

pythonSchema = StructType() \
          .add("id", StringType(), True) \
          .add("tweet", StringType(), True) \
          .add("ts", StringType(), True)
          
          
awsAccessKeyId = "AKIA3QG5W4IX75ORCYOY" # update the access key
awsSecretKey = "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"   # update the secret key
kinesisStreamName = "CSP554"  # update the kinesis stream name


kinesisRegion = "us-east-2"

kinesis_client = boto3.client('kinesis', 
                                  region_name='us-east-2',  # enter the region
                                  aws_access_key_id='AKIA3QG5W4IX75ORCYOY',  # fill your AWS access key id
                                  aws_secret_access_key='Go7F/RA2FJAls5BuH3yYO5EL39sU9+ZXpKB2gXzt')  # fill you aws secret access key
    

spark.sql("select cast(data as string) from tweets")

# Define your function
getID = UserDefinedFunction(lambda x: parse_tweet(x)[0], StringType())
getTs = UserDefinedFunction(lambda x: parse_tweet(x)[1], StringType())
getTweet = UserDefinedFunction(lambda x: parse_tweet(x)[2], StringType())

# Apply the UDF using withColumn
tweets = (tweets.withColumn('id', getID(col("data")))
               .withColumn('ts', getTs(col("data")))
               .withColumn('Tweet', getTweet(col("data")))
         ).toPandas()       # tweets is now a pandas df 

convert tweets pandas df into input tensor for logistic regression model
    
# df = pd.read_csv()
input_tensor = create_input_tensor(tweets)

# load MlLib model
sameModel = LogisticRegressionModel.load(sc,"hdfs:///user/project/llib_logistic.model")
# retrieve sentiments from input tensor using model
tweet_f = input_tensor.to_numpy()
pred = sameModel.predict(tweet_f)
# create DF to send to dashboard

dashboard_df = pd.DataFrame()
dashboard_df['tweet'] = tweets['Tweet']
dashboard_df['ts'] = tweets['ts']
dashboard_df['prediction'] = pred
print(pred)
# send created DF to dashboard
# send_df_to_dashboard(df)




#button action = 'exec(python capture.py' + userinput+')' runs this in EMR instance, 

#then also runs spark_app.py in pyspark instance



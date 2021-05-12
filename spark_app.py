# spark_app.py is going to collect the tweets from the stream, preprocess them, and then put into the mllib model to predict its sentiment
# we will create the dataframe with tweet, timestamp, positive sentiment score, negative sentiment score
import pickle
import sys
import time

import pandas
import text
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
          
          
awsAccessKeyId = "" # update the access key
awsSecretKey = ""   # update the secret key
kinesisStreamName = ""  # update the kinesis stream name


kinesisRegion = ""


kinesisDF = spark \
  .readStream \
  .format("kinesis") \
  .option("streamName", kinesisStreamName)\
  .option("region", kinesisRegion) \
  .option("initialPosition", "LATEST") \
  .option("format", "json") \
  .option("awsAccessKey", awsAccessKeyId)\
  .option("awsSecretKey", awsSecretKey) \
  .option("inferSchema", "true") \
  .load()

df = kinesisDF \
  .writeStream \
  .format("memory") \
  .outputMode("append") \
  .queryName("tweets")  \
  .start()

tweets = spark.sql("select cast(data as string) from tweets")


# Define your function
getID = UserDefinedFunction(lambda x: parse_tweet(x)[0], StringType())
getTs = UserDefinedFunction(lambda x: parse_tweet(x)[1], StringType())
getTweet = UserDefinedFunction(lambda x: parse_tweet(x)[2], StringType())

# Apply the UDF using withColumn
tweets = (tweets.withColumn('id', getID(col("data")))
               .withColumn('ts', getTs(col("data")))
               .withColumn('Tweet', getTweet(col("data")))
         ).toPandas()       # tweets is now a pandas df 

# convert tweets pandas df into input tensor for logistic regression model

input_tensor = create_input_tensor(tweets)

# load MlLib model
sameModel = LogisticRegressionModel.load(sc,"target/tmp/pythonLogisticRegressionWithLBFGSModel")
# retrieve sentiments from input tensor using model

# create DF to send to dashboard

dashboard_df = pd.DataFrame()
dashboard_df['tweet'] = tweets['Tweet']
dashboard_df['ts'] = tweets['ts']
dashboard_df['positive'] = #model score
dashboard_df['negative'] = #model score


# send created DF to dashboard
send_df_to_dashboard(df)




#button action = 'exec(python capture.py' + userinput+')' runs this in EMR instance, 

#then also runs spark_app.py in pyspark instance



import tensorflow as tf
import pandas as pd
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import regularizers
from tensorflow.keras import initializers
from tensorflow.python.keras.backend import log
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import time
import pickle
import sys

analyzer = SentimentIntensityAnalyzer()
 
def vader(x):
    return analyzer.polarity_scores(x)['compound']

def textblob(x):
    return TextBlob(x).sentiment.polarity

def create_input_tensor(data):
    # labels need to be one hot encoded
    y = pd.get_dummies(data['Sentiment'])
    input_tensor = pd.DataFrame()
    input_tensor['vader'] = data['Tweet'].apply(vader)
    input_tensor['textblob'] = data['Tweet'].apply(textblob)
    input_tensor['negative'] = y[-1]
    input_tensor['positive'] = y[1]

    return input_tensor

# logistic regression model using keras
def create_model():
    model = keras.Sequential(
            [
            layers.Dense(2, 
                        activation="softmax", 
                        kernel_initializer=initializers.RandomNormal(stddev=0.01),
                        kernel_regularizer= regularizers.l1_l2(l1=0.01, l2=0.01),
                        input_shape=(2,))
            ]
        )

    model.compile(
                'sgd',
                'categorical_crossentropy',
                ['accuracy']
    )
    model.build()
    #print(model.summary())
    return model

def train_test(df,labels):
    msk = np.random.rand(len(df)) < 0.8
    train_data,train_labels = df[msk],labels[msk]
    validation_data,validation_labels = df[~msk],labels[~msk]
    return train_data,train_labels, validation_data,validation_labels

def train_dl(model, train_data, train_labels, vd,vl):
    history = model.fit(train_data,
                    train_labels,
                    epochs=50,
                    batch_size=512,
                    validation_data = (vd,vl))

def run(input_tensor):
    train_data,train_labels,vd,vl = train_test(input_tensor[['vader','textblob']],input_tensor[['negative','positive']])
    model = create_model()
    print('training')
    train_dl(model, train_data.to_numpy(), train_labels.to_numpy(), vd.to_numpy(),vl.to_numpy())
    return model




if __name__ == '__main__':
    if len(sys.argv) != 1:
        filename = sys.argv[1]
        df = pd.read_csv(filename)
        df.Tweet = df.Tweet.astype(str)
        input_tensor = create_input_tensor(df)
        input_tensor.to_csv('input_tensor.csv', header = ['vader','textblob','negative','positive'], index=False)
    else:
        df = pd.read_csv('input_tensor.csv', header = ['vader','textblob','negative','positive'])
    start = time.time()
    trained_model = run(df)
    trained_model.save('tf_logistic')
    runtime = start - time.time()
    print(runtime)
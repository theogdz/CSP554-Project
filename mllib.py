from pyspark.mllib.classification import LogisticRegressionWithLBFGS, LogisticRegressionModel
from pyspark.mllib.regression import LabeledPoint
from pyspark.sql.types import *
import time

# Load and parse the data
def parsePoint(line):
    values = [float(x) for x in line.split(',')]
    return LabeledPoint(values[2], values[:1])

start = time.time()

struct = StructType().add("vader", DoubleType(), True).add("textblob",DoubleType(), True).add("negative",IntegerType(), True).add("positive",IntegerType(), True)

data = sc.textFile("hdfs:///user/project/mllib.csv")
'''
data = spark.read.csv('hdfs:///user/project/input_tensor.csv',header=True)    # data is an RDD
data = data.withColumn("label", (data.positive*2)-1)
col = ['positive','negative']
data = data.drop(*col)
print(data.show(5))

data.write.csv('mllib_input.csv')
'''

parsedData = data.map(parsePoint)

# Build the model
model = LogisticRegressionWithLBFGS.train(parsedData, iterations = 50)

# Evaluating the model on training data
start = time.time()
labelsAndPreds = parsedData.map(lambda p: (p.label, model.predict(p.features)))
trainErr = labelsAndPreds.filter(lambda lp: lp[0] != lp[1]).count() / float(parsedData.count())
print("Training Error = " + str(trainErr))
# model.save(sc, "hdfs:///user/project/llib_logistic.model")

runtime = time.time() - start
print("The runtime of MLlib training is:, ",runtime)

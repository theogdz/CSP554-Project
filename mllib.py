from pyspark.mllib.classification import LogisticRegressionWithLBFGS, LogisticRegressionModel
from pyspark.mllib.regression import LabeledPoint
from pyspark.sql.types import *
import time

# Load and parse the data
def parsePoint(line):
    values = line.split(',')
    if values[2] == 1:
        return LabeledPoint(-1,values[0:1])
    else:
        return LabeledPoint(1,values[0:1])

start = time.time()

struct = StructType().add("vader", DoubleType(), True).add("textblob",DoubleType(), True).add("negative",IntegerType(), True).add("positive",IntegerType(), True)

data = spark.read.schema(struct).csv('hdfs:///user/hadoop/input_tensor.csv')    # data is an RDD

parsedData = data.map(parsePoint)

# Build the model
model = LogisticRegressionWithLBFGS.train(parsedData)

# Evaluating the model on training data
labelsAndPreds = parsedData.map(lambda p: (p.label, model.predict(p.features)))
trainErr = labelsAndPreds.filter(lambda lp: lp[0] != lp[1]).count() / float(parsedData.count())
print("Training Error = " + str(trainErr))

model.save(sc, "mllib_logistic")

runtime = time.time() - start
print(runtime)
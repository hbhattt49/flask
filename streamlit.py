#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ======================================================================
# FIX: numpy.dtype Pickle issue in PySpark (PickleException workaround)
# ======================================================================
import numpy as np
import copyreg

def _reduce_dtype(dt):
    """Serialize numpy.dtype safely for PySpark <-> Java (Pyrolite)"""
    return (np.dtype, (dt.str,))

copyreg.pickle(np.dtype, _reduce_dtype)

# ======================================================================
# Standard PySpark imports
# ======================================================================
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, FloatType, StringType
from pyspark.sql.functions import col
import pandas as pd

# ======================================================================
# Initialize Spark session
# ======================================================================
spark = (
    SparkSession.builder
    .appName("IrisSample")
    .getOrCreate()
)

# ======================================================================
# Define schema and load dataset
# ======================================================================
schema = StructType([
    StructField("sepal_length", FloatType(), True),
    StructField("sepal_width", FloatType(), True),
    StructField("petal_length", FloatType(), True),
    StructField("petal_width", FloatType(), True),
    StructField("label_str", StringType(), True)
])

# Replace this path with your own or use inline sample data
data = [
    (5.1, 3.5, 1.4, 0.2, "setosa"),
    (4.9, 3.0, 1.4, 0.2, "setosa"),
    (6.2, 3.4, 5.4, 2.3, "virginica"),
    (5.9, 3.0, 5.1, 1.8, "virginica"),
    (5.5, 2.3, 4.0, 1.3, "versicolor"),
    (6.5, 2.8, 4.6, 1.5, "versicolor"),
]

df = spark.createDataFrame(data, schema=schema)

# ======================================================================
# Display schema and basic data
# ======================================================================
print("Schema:")
df.printSchema()

print("\nClass distribution:")
df.groupBy("label_str").count().show()

# ======================================================================
# Example transformation
# ======================================================================
df_filtered = df.filter(col("sepal_length") > 5.0)

# ======================================================================
# Convert Spark DataFrame → Pandas DataFrame safely
# ======================================================================
pdf = df_filtered.toPandas()
print("\nConverted Pandas DataFrame:")
print(pdf.head())

# ======================================================================
# Stop Spark session
# ======================================================================
spark.stop()

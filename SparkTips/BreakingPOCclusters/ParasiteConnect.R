
library("sparklyr")
library("dplyr")

sc <- spark_connect(
  master= "spark://127.0.0.1:53670",
  spark_home= "/Users/johnmount/Library/Caches/spark/spark-2.1.0-bin-hadoop2.7" # from sc$spark_home
)

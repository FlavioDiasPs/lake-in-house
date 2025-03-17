from databricks.connect import DatabricksSession
from pyspark.sql import SparkSession


def get_spark() -> SparkSession:
    try:
        return DatabricksSession.builder.getOrCreate()
    except ImportError:
        return SparkSession.Builder().getOrCreate()

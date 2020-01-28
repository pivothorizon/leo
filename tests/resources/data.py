from pyspark.sql import DataFrame
from .spark_util import SparkUtil

def training_data() -> DataFrame:
    spark = SparkUtil().get_spark_session()
    # TODO Create a spark DataFrame using spark session above and return it
    raise NotImplementedError('training_data method has not been implemented yet')


def test_data() -> DataFrame:
    spark = SparkUtil().get_spark_session()
    # TODO Create a spark DataFrame using spark session above and return it
    raise NotImplementedError('test_data method has not been implemented yet')

from pyspark.ml import Pipeline
from .model import testleoModel
from .data import training_data


def build_pipeline() -> Pipeline:
    # TODO implement pyspark.ml.Pipeline here
    raise NotImplementedError('Pipeline has not been implemented yet!')


def train_model() -> testleoModel:
    training_df = training_data()
    return testleoModel(build_pipeline().fit(training_df))

from abc import ABCMeta, abstractmethod
from .config import version
from .data import test_data

from pyspark.sql import SparkSession
import pandas


class BaseModel(metaclass=ABCMeta):
    """
    A base class for any kind of model which can be used for prediction.
    """

    def __init__(self, model):
        """

        :param model: Trained model to be used for prediction and test

        """
        assert model is not None, 'Model instance cannot be None'
        self._model = model

    @property
    def model_name(self) -> str:
        """
        :return: The name of this model.
        """
        return type(self).__name__

    @property
    def model_version(self) -> str:
        """
        :return: The model's version string.
        """
        return version

    def get_model(self):
        """
        :return: The underlying model instance.
        """
        return self._model

    @abstractmethod
    def test_model(self) -> list:
        """
        Evaluate fitted model with given test data set

        :return: list of evaluation results.
        """

    @abstractmethod
    def predict(self, inputs) -> list:
        """
        Runs the trained model on the given input, and returns the model's output.
        Both the input and output are in serialized form.

        :param inputs:  input data

        :return: list of predictions

        :exception ModelException: If the prediction cannot be completed,
                                   for example because of erroneous or missing data.

        :exception ModelNotTrainedException: Raised if underlying model is not trained yet.
        """


class SparkModel(BaseModel):

    def test_model(self) -> list:
        test_df = test_data()
        return self._model.transform(test_df).select('prediction').collect()

    def predict(self, inputs) -> list:
        return [x.prediction for x in self._model.transform(inputs).select('prediction').collect()]


class testleoModel(SparkModel):

    def do_predict(self, spark: SparkSession, input_data: list):
        df = pandas.DataFrame(input_data)
        return {'predictions': self.predict(spark.createDataFrame(df))}

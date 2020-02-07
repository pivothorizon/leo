from pyspark.ml.pipeline import PipelineModel
from threading import Lock
from .model import testleoModel
from .config import model_repo_path


class ModelRepo:

    def __init__(self):
        self._lock = Lock()

    def load_model(self) -> testleoModel:
        """
        Loads the model (which is assumed to be a pyspark.ml.PipelineModel) from the models directory.

        :exception ModelException: If the model cannot be loaded.

        """
        with self._lock:
            try:
                return testleoModel(PipelineModel.load(model_repo_path))
            except Exception as ex:
                raise ModelException(f'Unable to load model: {ex}')

    def save_model(self, _model: testleoModel) -> None:
        """
        Save given model to model repository.
        :param _model: Model to be saved.
        :exception ModelException: if an error occurred while saving the model.

        """
        with self._lock:
            try:
                _model.get_model().write().overwrite().save(model_repo_path)
            except Exception as ex:
                raise ModelException(f'Unable to save model: {ex}')


class ModelException(Exception):
    pass

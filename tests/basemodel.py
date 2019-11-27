from abc import ABCMeta, abstractmethod
from typing import Mapping, Any, Optional, Tuple
from threading import Lock

import pickle
import os


class BaseModel(metaclass=ABCMeta):
    """
    A base class for any kind of model which can be used with Leo.
    """

    def __init__(self):
        self._loaded_model = None
        self._model_path = os.path.join(os.path.dirname(__file__), '..', 'models', self.model_name)
        self._lock = Lock()

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
        return 'TEST'

    def reset(self) -> None:
        """
        Resets the model by reloading it from the same source it was loaded from originally.
        """
        self.load_model(force_reload=True)

    @abstractmethod
    def predict(self, input_data: bytes, args: Mapping[str, Any]) -> Tuple[str, Mapping[str, Any]]:
        """
        Runs the model on the given input, and returns the model's output.
        Both the input and output are in serialized form.

        :param input_data: The serialized input data.
        :param args: A dictionary of additional parameters, if there are any.

        :return: A message and, optionally, the model's output in serialized form.

        :exception ModelException: If the prediction cannot be completed,
                                   for example because of erroneous or missing data.

        """

    def load_model(self, force_reload: bool = False) -> None:
        """
        Initializes the model from a models directory.
        If force_reload is True then reads from models directory and overrides the _loaded_model property value,
        else if _loaded_model is None then reads it from models directory
        else returns _loaded_model property value.

        :param force_reload Reload the model even if _loaded_model is not None

        :exception ModelException: If the model cannot be loaded. In the default implementation, either if the
                                   file is not found, or if a PicklingError is raised when loading the file.

        """
        if force_reload or self._loaded_model is None:
            with self._lock:
                if os.access(self._model_path, os.O_RDONLY):
                    with open(self._model_path, 'rb') as f:
                        try:
                            binary = f.read()
                            self._loaded_model = pickle.loads(binary)
                        except pickle.PicklingError as ex:
                            raise ModelException('The model could not be unpickled.', 400, {'original_error': ex})
                else:
                    raise ModelException(f'Could not find file {self.model_name} or {self._model_path}.', 404)

    def save_model(self) -> None:
        """
        Serialize trained model.
        The default implementation will attempt to pickle the trained model. If the trained model does not support pickling,
        an exception will be raised.

        :exception ModelException: If the default implementation of this method is used,
                                   but the model does not support pickling.
        """
        with self._lock:
            if self._loaded_model is None:
                raise ModelException('The model has not yet been trained.', 409)
            try:
                binary = pickle.dumps(self._loaded_model)
                with open(self._model_path, 'wb') as f:
                    f.write(binary)
            except pickle.PicklingError:
                raise ModelException('This model cannot be saved by the default method (pickling) - please provide a'
                                     ' custom implementation of the save_model method.', 501)


class ModelNotTrainedException(Exception):
    pass


class ModelException(Exception):
    """
    Exception type used to indicate that a model could not be initialized,
    or that a requested prediction could not be completed.

    :param msg: The message to return to the caller.
    :param status: The HTTP status code to use in the response to the caller. Code 400 (Bad Request) is the default. Invalid codes will result in an exception.
    :param extra_data: Any additional data to pass along in the response.
    :param reset_model: Whether or not the model should be reset after processing this exception. Defaults to False.

    """

    def __init__(self,
                 msg: str,
                 status: int = 400,
                 extra_data: Optional[Mapping[str, Any]] = None,
                 reset_model: bool = False):
        """

        """
        self.msg = msg
        self.status = status
        self.extra_data = extra_data
        self.reset_model = reset_model

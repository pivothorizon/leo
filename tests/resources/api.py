from flask import jsonify
import flask_rest_api as rest
from flask.views import MethodView
from typing import Mapping, Any, Optional, Tuple
import marshmallow as ma
import logging
import logstash
from prometheus_client import Summary, Counter

from .model import BaseModel
from .modelrepo import ModelRepo, ModelException
from .schema import testleoRequestSchema, testleoResponseSchema
from .spark_util import SparkUtil

namespace = 'testleo'
_blp = rest.Blueprint(namespace, __name__)

RESPONSE_TIME = Summary(name='response_time_seconds', documentation='Response time for each request', namespace=namespace)
ERROR_COUNTER = Counter(name='failed_requests', documentation='Failed requests', labelnames=['exception_type'], namespace=namespace)

logger = logging.getLogger('testleo')
logger.setLevel(logging.INFO)
logger.addHandler(logstash.TCPLogstashHandler('testleo-logstash-service', 5959, version=1))

class _PredictSchema(ma.Schema):
    """
    The schema for POST requests to the prediction method.
    """
    class Meta:
        strict = True

    inputs = ma.fields.Nested(testleoRequestSchema(many=True), required=True)


class _ResponseSchema(testleoResponseSchema):
    """
    The schema for the responses.
    """


@_blp.route('/testleo')
class testleoApp(MethodView):
    """
    Provides the API to instantiate and access testleo models.
    """

    def __init__(self):
        super().__init__()
        self._model = None
        self._spark = SparkUtil().get_spark_session()

    def _get_model(self):
        """
        Lazy loaded model
        :return: Model instance
        """
        if self._model is None:
            self._model = ModelRepo().load_model()
        return self._model

    @RESPONSE_TIME.time()
    @_blp.arguments(_PredictSchema)
    @_blp.response(_ResponseSchema)
    def post(self, args):
        """
        Invoke the testleoModel model.
        ---

        Calls underlying model prediction with given output and returns the predictions

        """
        logger.info(f'Querying testleo with {args}')
        result = self._get_model().do_predict(self._spark,  args['inputs'])
        return make_response(result, 200)


@_blp.app_errorhandler(ModelException)
def handle_model_exception(ex: ModelException, model: Optional[BaseModel] = None) -> Tuple[Any, int]:
    """
    Sends an error response to the client, and depending on the values in the exception also resets the model.

    :param ex: The exception which was raised.
    :param model: The instance of the model in which the exception was raised, if applicable.

    :return: The Flask Response which contains the error message.
    """
    logger.exception(ex)
    ERROR_COUNTER.labels(ex.__class__.__name__).inc()
    return make_error_response(ex, 400)


def make_response(results: list, status: int) -> Tuple[Any, int]:
    response_data = {
        'results': results
    }
    return jsonify(response_data), status


def make_error_response(ex: Exception, status: int) -> Tuple[Any, int]:
    """
     Formats an API response.

     :param ex: Exception
     :param status: The status code to use in the response.

     :return: The (Flask) Response object.

     """

    response_data = {
        'message': str(ex),
    }
    return jsonify(response_data), status


def get_blp():
    """
    :return: The Blueprint defined in this file.
    """
    return _blp

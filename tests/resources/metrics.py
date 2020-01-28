from flask import Response
from flask.views import MethodView
import flask_rest_api as rest
from prometheus_client import CollectorRegistry, multiprocess, generate_latest, CONTENT_TYPE_LATEST, REGISTRY

_blp = rest.Blueprint('metrics', 'metrics')


@_blp.route('/')
class Metrics(MethodView):
    """
    Exposes APM metrics as an api endpoint to be consumed by Prometheus.
    It handles multiprocess deployment of the api
    """

    def __init__(self):
        for collector, names in tuple(REGISTRY._collector_to_names.items()):
            REGISTRY.unregister(collector)

    @_blp.response(headers={"Content-Type": "text/plain"})
    def get(self):
        """
        Invoked by a GET request to the metrics endpoint.
        ---
        """
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        data = generate_latest(registry)
        return Response(data, mimetype=CONTENT_TYPE_LATEST)


def get_blp():
    return _blp

import flask
import flask_rest_api as rest
from .config import version

application = flask.Flask('testleo')
application.config['API_VERSION'] = version
application.config['OPENAPI_VERSION'] = '3.0.2'
application.config['OPENAPI_URL_PREFIX'] = 'api'
application.config['OPENAPI_JSON_PATH'] = 'openapi.json'
application.config['OPENAPI_SWAGGER_UI_PATH'] = '/docs'
application.config['OPENAPI_SWAGGER_UI_VERSION'] = '3.23.5'
application.config['APPLICATION_ROOT'] = '/application'

_api = rest.Api(application)

from . import api, metrics
_api.register_blueprint(api.get_blp(), url_prefix='/model')
_api.register_blueprint(metrics.get_blp(), url_prefix='/metrics')

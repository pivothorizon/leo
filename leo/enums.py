from enum import Enum


class MonitoringOptions(Enum):
    PROMETHEUS = 'prometheus'
    GRAPHITE = 'graphite'


class LoggingOptions(Enum):
    ELK = 'elk'


class GatewayOptions(Enum):
    KONG = 'kong'


class WSGIOptions(Enum):
    GUNICORN = 'gunicorn'
    uWSGI = 'uwsgi'


class WebFrameworkOptions(Enum):
    FLASK = 'flask'
    FALCON = 'falcon'


class EnvironmentOptions(Enum):
    VIRTUALENV = 'virtualenv'
    CONDA = 'conda'


class OSType(Enum):
    POSIX = 'posix'
    WINDOWS = 'windows'
    UNKNOWN = 'unknown'


class LibrarySupport(Enum):
    PYSPARK = 'pyspark'
    MLEAP = 'mleap'

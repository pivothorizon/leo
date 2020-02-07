# Place project specific configuration parameters here
import logging
from prometheus_client import multiprocess
import os

version = '1.0.0'
model_repo_path = os.getcwd() + '/models'
spark_app_name = 'testleo'
spark_master = 'local'
spark_hive_support = False
spark_config = {
# For example:
#     'spark.some.option': 'value'
}
spark_config_include_defaults = True

def child_exit(server, worker):
    """
    This method is added for Gunicorn support.
    The prometheus_multiproc_dir environment variable must be set to a directory that the client library can use for metrics.
    """
    logging.info('Calling multiprocess.mark_process_dead')
    multiprocess.mark_process_dead(worker.pid)

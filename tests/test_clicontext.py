import unittest
from .shared import *
import os


class CliContextTest(unittest.TestCase):

    def test_get_cli_dict(self):
        assert test_context.name == project_name
        assert test_context.version == version
        assert test_context.author == author
        assert test_context.kubernetes == True
        assert test_context.docker == True
        assert test_context.web_framework == web
        assert test_context.use_flask == True
        assert test_context.use_falcon == False
        assert test_context.monitor == monitor
        assert test_context.log == log
        assert test_context.use_pyspark == True
        assert test_context.use_elk == True
        assert test_context.use_graphite == False
        assert test_context.use_mleap == False
        assert test_context.app_object_name == 'application'
        assert test_context.root_dir_name == 'testleo'
        assert test_context.project_name == 'testleo'
        assert test_context.package_path == os.path.join('testleo', 'testleo')
        assert test_context.environment_type == environ
        assert test_context.use_conda == True
        assert test_context.use_virtualenv == False

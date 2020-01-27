import unittest
from leo.clicontext import CliContext
import os


class CliContextTest(unittest.TestCase):

    def test_get_cli_dict(self):
        project_name = "testleo"
        version = "1.0.0"
        author = "vdogan"
        log = "elk"
        monitor = "prometheus"
        gateway = "kong"
        wsgi = "gunicorn"
        web = "flask"
        environ = "conda"
        libraries = "pyspark"
        args = {
            "name": project_name,
            "version": version,
            "author": author,
            "log": log,
            "monitor": monitor,
            "gateway": gateway,
            "wsgi": wsgi,
            "web_framework": web,
            "environment_type": environ,
            "libraries": libraries,
            "kubernetes": True,
            "docker": True
        }

        context = CliContext(args)

        assert context.name == project_name
        assert context.version == version
        assert context.author == author
        assert context.kubernetes == True
        assert context.docker == True
        assert context.web_framework == web
        assert context.use_flask == True
        assert context.use_falcon == False
        assert context.monitor == monitor
        assert context.log == log
        assert context.use_pyspark == True
        assert context.use_elk == True
        assert context.use_graphite == False
        assert context.use_mleap == False
        assert context.app_object_name == 'application'
        assert context.root_dir_name == 'testleo'
        assert context.project_name == 'testleo'
        assert context.package_path == os.path.join('testleo', 'testleo')
        assert context.environment_type == environ
        assert context.use_conda == True
        assert context.use_virtualenv == False




import unittest
import subprocess
import sys
import os
import yaml


_do_docker_tests = False


class testleoTester(unittest.TestCase):

    def test_importable(self):
        """
        Tests that various auto-generated elements are properly importable.
        """
        try:
            from testleo.model import testleo
        except (ImportError, SyntaxError, NameError) as ex:
            raise AssertionError('Failed to import testleo object', ex)
        try:
            from testleo import application
        except (ImportError, SyntaxError, NameError) as ex:
            raise AssertionError('Failed to import Flask object (flask)', ex)

        try:
            from testleo import _api
        except (ImportError, SyntaxError, NameError) as ex:
            raise AssertionError('Failed to import API object', ex)

        try:
            from testleo.api import _blp
        except (ImportError, SyntaxError, NameError) as ex:
            raise AssertionError('Failed to import blueprint object', ex)

        try:
            from testleo.api import testleoApp
        except (ImportError, SyntaxError, NameError) as ex:
            raise AssertionError('Failed to import API class', ex)

        try:
            from testleo.api import _PredictSchema
        except (ImportError, SyntaxError, NameError) as ex:
            raise AssertionError('Failed to import prediction schema class', ex)

        try:
            from testleo.api import _ResponseSchema
        except (ImportError, SyntaxError, NameError) as ex:
            raise AssertionError('Failed to import response schema class', ex)


    def test_docker(self):
        """
        If enabled, tests that the Dockerfile is (at least syntactically) correct by attempting to build it.
        The same will be done for the docker-compose.yml file.
        """
        if not _do_docker_tests:
            self.skipTest('--include-docker-test not specified')
        build_result = subprocess.run(['docker', 'build', '-q', '--force-rm', '-t', 'tmp_testleo_test', '.'],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        self.assertEqual(0, build_result.returncode, 'Failed to use Dockerfile, either it was not created correctly, or'
                                                     ' Docker is not installed.')
        try:
            compose_result = subprocess.run(['docker-compose', 'up', '--no-start', '--no-deps'],
                                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.assertEqual(0, compose_result.returncode, 'Failed to use docker-compose.yml, either it was not created'
                                                           ' correctly, or docker-compose is not installed.')
        finally:
            subprocess.run(['docker-compose', 'rm', '-f', '-s', '-v'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['docker', 'rmi', 'tmp_testleo_test'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def test_yaml_structure(self):
        """
        Tests that generated YAML files are syntactically correct.
        """
        def _test_file(name, stream):
            try:
                yaml.safe_load(stream)
            except yaml.YAMLError as ex:
                self.fail(f'Failed to parse {name} YAML configuration: {ex}')

        kubernetes_files = [
            'db_pod_template',
            'db_service',
            'kong_pod_template',
            'kong_service',
            'elastic_pod_template',
            'elastic_service',
            'kibana_pod_template',
            'kibana_service',
            'logstash_pod_template',
            'logstash_service',
            'main_pod_template',
            'main_service',
            'grafana_pod_template',
            'grafana_service',
            'prometheus_pod_template',
            'prometheus_service',
        ]
        elk_files = [
            'elasticsearch',
            'logstash',
            'kibana'
        ]
        for file_name in kubernetes_files:
            full = os.path.join(os.path.dirname(__file__), '..', 'kubernetes', f'{file_name}.yml')
            with open(full, 'r') as f:
                _test_file(file_name, f)

        for file_name in elk_files:
            full = os.path.join(os.path.dirname(__file__), '..', 'elk', f'{file_name}.yml')
            with open(full, 'r') as f:
                _test_file(file_name, f)

        with open(os.path.join(os.path.dirname(__file__), '..', 'prometheus', 'prometheus.yml')) as f:
            _test_file('prometheus', f)


if __name__ == '__main__':
    if '--include-docker-test' in sys.argv:
        sys.argv.remove('--include-docker-test')
        _do_docker_tests = True
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    unittest.main()

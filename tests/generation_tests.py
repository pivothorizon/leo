import os
import unittest
import itertools
from typing import Tuple
from shutil import rmtree
import inspect
import importlib
import sys

import leo.cli
from leo.enums import *

_do_docker_tests = False  # This will take about 35-45 seconds per configuration on my machine if set to True
leo.cli.download_dependencies = False


class GenerationTests(unittest.TestCase):

    def test_project_creation(self):
        options = {
            'log': [None, *LoggingOptions.__members__.values()],
            'monitor': [None, *MonitoringOptions.__members__.values()],
            'gateway': [None, *GatewayOptions.__members__.values()],
            'wsgi': [None, *WSGIOptions.__members__.values()],
            'web_framework': [*WebFrameworkOptions.__members__.values()],
            'environment_type': [*EnvironmentOptions.__members__.values()],
            'libraries':
                itertools.chain.from_iterable([
                    itertools.combinations(LibrarySupport.__members__.values(), r)
                    for r in range(len(LibrarySupport.__members__) + 1)])

        }

        configurations = [(*zip(options.keys(), conf),) for conf in itertools.product(*options.values())]

        i = 1
        for config in configurations:
            print(f'{i} / {len(configurations)}')
            i += 1
            self._test_creation_with_configuration(config)

    @staticmethod
    def _convert_param(param):
        if param is None:
            return 'None'
        if issubclass(type(param), Enum):
            return param.value
        if isinstance(param, tuple):
            return [*param]
        raise AssertionError('Unexpected parameter')

    def _test_creation_with_configuration(self, config: Tuple[Tuple[str, Enum], ...]):
        params = {opt: self._convert_param(param) for opt, param in config}
        with self.subTest(None, **params):
            args = {
                'name': 'TestProject',
                'author': 'tester',
                'docker': True,
                'kubernetes': True,
                'version': 'test',
                **params
            }
            print(args)
            old_cwd = os.getcwd()
            new_cwd = os.path.join(old_cwd, 'TestProject', 'tests')
            try:
                leo.cli.create(args)
                os.chdir(new_cwd)
                sys.path.append(new_cwd)
                test_module = importlib.import_module(name='testproject_tests')
                self.assertIsNotNone(test_module)
                self.assertTrue(hasattr(test_module, 'TestProjectTester'))
                test_cls = getattr(test_module, 'TestProjectTester')
                test_obj = test_cls()
                self.assertTrue(isinstance(test_obj, unittest.TestCase))

                setattr(test_module, '_do_docker_tests', _do_docker_tests)

                sys.modules['tests'].__file__ = os.path.abspath(new_cwd)

                for test_fn in [fn for name, fn
                                in inspect.getmembers(test_obj, inspect.ismethod)
                                if name.startswith('test')]:
                    with self.subTest(f'Generated {test_fn.__name__}', **params):
                        if test_fn.__name__ == 'test_docker':
                            sys.argv.append('--include-docker-test')
                        test_fn()

            finally:
                os.chdir(old_cwd)
                # rmtree('TestProject')
                # if new_cwd in sys.path:
                #     sys.path.remove(new_cwd)


if __name__ == '__main__':
    unittest.main()

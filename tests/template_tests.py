import shutil
import unittest
import sys
import os
from argparse import Namespace
from typing import Optional

import marshmallow as ma

from leo.helper import make_api_template, make_model_template, make_cli_template


class _TestSchema(ma.Schema):
    some_field = ma.fields.String()


class _CliArgs(Namespace):

    def __init__(self, **kwargs):
        if 'init_args' not in kwargs:
            kwargs['init_args'] = None
        if 'input_args' not in kwargs:
            kwargs['input_args'] = None
        if 'log' not in kwargs:
            kwargs['log'] = False
        if 'monitor' not in kwargs:
            kwargs['monitor'] = False
        if 'gateway' not in kwargs:
            kwargs['gateway'] = False
        super().__init__(**kwargs)


class TemplateTestCase(unittest.TestCase):

    def load_generated_module(self, fq_name: str, content: str,
                              expected_err: Optional[type] = None,
                              header: str = '',
                              include_basemodel: bool = True):
        package = fq_name.split('.')[:-1]
        dir_name = os.path.join(os.path.dirname(__file__), '.'.join(package))
        mod_name = fq_name.split('.')[-1]
        file_name = os.path.join(dir_name, mod_name + '.py')
        os.makedirs(dir_name, exist_ok=True)
        try:
            if include_basemodel:
                shutil.copyfile(os.path.join(os.path.dirname(__file__), 'basemodel.py'),
                                os.path.join(dir_name, 'basemodel.py'))
                basemod = __import__('.'.join([*package, 'basemodel']), fromlist=['*'])
                self._BaseModel = getattr(basemod, 'BaseModel')
                self._ModelException = getattr(basemod, 'ModelException')

            with open(file_name, 'w') as f:
                f.write(header)
                f.write(content)
                f.close()

                if expected_err:
                    with self.assertRaises(expected_err):
                        __import__(fq_name, fromlist=['*'])
                else:
                    module = __import__(fq_name, fromlist=['*'])
                    return module
        finally:
            os.unlink(file_name)
            if include_basemodel:
                os.unlink(os.path.join(dir_name, 'basemodel.py'))
            os.removedirs(dir_name)


class TempModule:
    def __init__(self, test, fq_name: str, content: str,
                 header: str = '',
                 include_basemodel: bool = True):
        self._test = test
        self._name = fq_name
        self._content = content
        self._header = header
        self._base = include_basemodel
            
    def __enter__(self):
        return self._test.load_generated_module(self._name, self._content, header=self._header, include_basemodel=self._base)
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._name in sys.modules:
            del sys.modules[self._name]
        if exc_val:
            raise exc_type(exc_val).with_traceback(exc_tb)
            

class SchemaTemplateTests(TemplateTestCase):

    def test_basic_template(self):
        from leo.helper import _schema_template
        rendered = _schema_template('TestModel', 'Init', None)
        with TempModule(self, 'testmodel.schema', rendered, 'import marshmallow as ma\n\n', False) as module:
            self.assertTrue(hasattr(module, 'TestModelInitSchema'), 'Schema not found in imported module.')

    def test_template_with_reference(self):
        from leo.helper import _schema_template
        rendered = _schema_template('TestModel', 'Init', 'tests.template_tests._TestSchema')
        with TempModule(self, 'testmodel.schema', rendered,
                        'import marshmallow as ma\n\nimport tests.template_tests\n\n', False) as module:
            self.assertTrue(hasattr(module, 'TestModelInitSchema'), 'Schema not found in imported module.')
            schema = getattr(module, 'TestModelInitSchema')
            self.assertEqual(schema.__name__, _TestSchema.__name__)

    def test_template_with_json_spec(self):
        from leo.helper import _schema_template
        rendered = _schema_template('TestModel', 'Init', '{"arg": "ma.fields.Integer(required=True)"}')
        with TempModule(self, 'testmodel.schema', rendered, 'import marshmallow as ma\n\n', False) as module:
            self.assertTrue(hasattr(module, 'TestModelInitSchema'), 'Schema not found in imported module.')
            schema = getattr(module, 'TestModelInitSchema')
            instance = schema()
            fields = instance.declared_fields
            self.assertIn('arg', fields)
            self.assertEqual(ma.fields.Integer, type(fields['arg']))


class ModelTemplateTests(TemplateTestCase):

    def test_template(self):
        rendered = make_model_template('TestModel', _CliArgs())
        with TempModule(self, 'testmodel.model', rendered) as module:
            self.assertTrue(hasattr(module, 'TestModelInitSchema'))
            self.assertTrue(hasattr(module, 'TestModelInputSchema'))
            self.assertTrue(hasattr(module, 'TestModel'))

            model_class = getattr(module, 'TestModel')
            self.assertIn(self._BaseModel, model_class.__bases__)

            model = model_class('TestInstance')
            for member in ['model_name', 'init_schema', 'input_schema', 'initialize',
                           'fit', 'evaluate', 'predict', 'save_model']:
                self.assertTrue(hasattr(model, member))

            self.assertEqual('TestModel', model.model_name)

            with self.assertRaises(self._ModelException):
                model.initialize(None)

            with self.assertRaises(self._ModelException):
                model.predict(b'', None, None)

    def test_invalid_name(self):
        rendered = make_model_template('Not a valid name', _CliArgs())
        self.load_generated_module('tempmodel.model', rendered, SyntaxError)

    def test_invalid_schema(self):
        rendered = make_model_template('TestModel', _CliArgs(init_args=['I am not a valid definition.']))
        self.load_generated_module('tempmodel.model', rendered, SyntaxError)

        rendered = make_model_template('TestModel', _CliArgs(input_args=['i.am.syntactically.valid.but.don_t.Exist']))
        self.load_generated_module('tempmodel.model', rendered, NameError)


class APITemplateTests(TemplateTestCase):

    def test_template(self):
        if 'testmodel' in sys.modules:
            del sys.modules['testmodel']
        with TempModule(self, 'testmodel.__init__', 'make_response = None\n', include_basemodel=False) as package:
            with TempModule(self, 'testmodel.model', make_model_template('TestModel', _CliArgs())) as model_module:
                with TempModule(self, 'testmodel.api', make_api_template('TestModel', _CliArgs()),
                                include_basemodel=False) as api_module:
                    self.assertTrue(hasattr(api_module, '_model_type'))

                    model_class = getattr(model_module, 'TestModel')
                    self.assertEqual(model_class.__name__, getattr(api_module, '_model_type').__name__)

    def test_invalid_name(self):
        rendered = make_api_template('Not a valid name', _CliArgs())
        with TempModule(self, 'testmodel.model', make_model_template('TestModel', _CliArgs())):
            self.load_generated_module('testmodel.api', rendered, SyntaxError, include_basemodel=False)

    def test_missing_model(self):
        rendered = make_api_template('TestModel', _CliArgs())
        self.load_generated_module('testmodel.api', rendered, ImportError, include_basemodel=False)


class CLITemplateTests(TemplateTestCase):

    def test_cli(self):
        if 'testmodel' in sys.modules:
            del sys.modules['testmodel']
        with TempModule(self, 'testmodel.__init__', 'app = None\n', include_basemodel=False):
            with TempModule(self, 'testmodel.cli', make_cli_template('TestModel'),
                            include_basemodel=False) as cli_module:
                self.assertTrue(hasattr(cli_module, 'TestModelCli'))
                cli_class = cli_module.TestModelCli
                self.assertTrue(hasattr(cli_class, 'test'))

    def test_invalid_name(self):
        if 'testmodel' in sys.modules:
            del sys.modules['testmodel']
        with TempModule(self, 'testmodel.__init__', 'app = None\n', include_basemodel=False):
            self.load_generated_module('testmodel.cli', make_cli_template('Invalid Project Name!'),
                                       SyntaxError, include_basemodel=False)


if __name__ == '__main__':
    unittest.main()

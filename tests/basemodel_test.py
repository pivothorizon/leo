import unittest
from .basemodel import *


class BaseModelTest(unittest.TestCase):
    class _DummyModel(BaseModel):

        def initialize(self, **kwargs) -> None:
            self._init_params = kwargs
            self._model = kwargs['arg']

        def fit(self, *args, **kwargs) -> Any:
            pass

        def evaluate(self, *args, **kwargs) -> Any:
            pass

        def predict(self, input_data: bytes, args: Mapping[str, Any]) -> Tuple[str, Mapping[str, Any]]:
            self._model += input_data
            return 'Incremented', {'current': self._model}

    def test_init_and_reset(self):
        model = self._DummyModel('dummy')
        model.initialize(arg=42)

        (msg, result) = model.predict(5, {})
        self.assertEqual(47, result['current'])

        (msg, result) = model.predict(5, {})
        self.assertEqual(52, result['current'])

        model.reset()
        (msg, result) = model.predict(5, {})
        self.assertEqual(47, result['current'])




if __name__ == '__main__':
    unittest.main()

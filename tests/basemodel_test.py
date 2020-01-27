import unittest
from .basemodel import *


class BaseModelTest(unittest.TestCase):
    class _DummyModel(BaseModel):

        def test_model(self) -> list:
            pass

        def predict(self, inputs) -> list:
            self._model += inputs
            return ['Incremented', {'current': self._model}]

    def test_predict(self):
        model = self._DummyModel(42)

        (msg, result) = model.predict(5)
        self.assertEqual(47, result['current'])

        (msg, result) = model.predict(5)
        self.assertEqual(52, result['current'])




if __name__ == '__main__':
    unittest.main()

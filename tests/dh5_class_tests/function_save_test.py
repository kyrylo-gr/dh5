# flake8: noqa: D100, D101, D102


import unittest
from dh5.dh5_class.transformation_types.function_save import Function, function_to_str


class FunctionClassTest(unittest.TestCase):
    def test_function_initialization(self):
        code = "def test_func(a, b): return a + b"
        func = Function(code)
        self.assertEqual(func.code, "def current_func(a, b): return a + b\n")

    def test_function_evaluation(self):
        code = "def test_func(a, b): return a + b"
        func = Function(code)
        result = func.eval(1, 2)
        self.assertEqual(result, 3)

    def test_call_before_eval(self):
        code = "def test_func(a, b): return a + b"
        func = Function(code)
        with self.assertRaises(ImportError):
            func(1, 2)

    def test_call_after_eval(self):
        code = "def test_func(a, b): return a + b"
        func = Function(code)
        func.eval(1, 2)
        result = func(1, 2)
        self.assertEqual(result, 3)

    def test_function_to_str(self):
        def sample_function():
            return "Hello, World!"

        code = function_to_str(sample_function)
        self.assertIn('return "Hello, World!"', code)

    def test_function_to_error(self):
        sample_val = 2

        with self.assertRaises(ValueError):
            function_to_str(sample_val)

    def test_syntax_error(self):
        code = "def test_func(a, b): return a + "
        func = Function(code)
        with self.assertRaises(SyntaxError):
            func.eval(1, 2)

    def test_empty_value_error(self):
        code = ""
        func = Function(code)
        with self.assertRaises(ValueError):
            func.eval(1, 2)

    # Additional tests can be added here


if __name__ == "__main__":
    unittest.main()

# flake8: noqa: D101, D102
import unittest
from dh5 import jsn
import os
import shutil

TEST_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(TEST_DIR, "tmp_test_data")
DATA_FILE_PATH = os.path.join(DATA_DIR, "some_data.json")


class JsonTest(unittest.TestCase):
    def write_read_assert(self, data, check=None):
        if check is None:
            check = data
        jsn.write(DATA_FILE_PATH, data)

        read_data = jsn.read(DATA_FILE_PATH)
        self.assertDictEqual(read_data, check)

    def test_simple(self):
        # Test writing to and reading from a file
        data_to_write = {"key3": "a", "key1": "b", "key2": "c"}
        self.write_read_assert(data_to_write)

    def test_numeric(self):
        # Test writing to and reading from a file
        data_to_write = {"key3": 3, "key1": 1, "key2": 2}
        self.write_read_assert(data_to_write)

    def test_float(self):
        # Test writing to and reading from a file
        data_to_write = {"key3": 3.123, "key1": -123.213, "key2": 2.31421}
        self.write_read_assert(data_to_write)

    def test_dict(self):
        # Test writing to and reading from a file
        data_to_write = {"d": {"key3": 3.123, "key1": -123.213, "key2": 2}}
        self.write_read_assert(data_to_write)

    def test_stringable(self):
        # Test writing to and reading from a file
        class Stringable:
            def __str__(self):
                return "some_value"

        data_to_write = {"key3": Stringable(), "key1": 1, "key2": 2}
        data_to_check = {"key3": "some_value", "key1": 1, "key2": 2}
        self.write_read_assert(data_to_write, data_to_check)

    def test_iterable(self):
        data_to_write = {"key3": [1, 2, 3], "key1": 1, "key2": 2}
        self.write_read_assert(data_to_write)

    def test_iterable_class(self):
        class Stringable:
            def __init__(self, val) -> None:
                self.val = val

            def __str__(self):
                return f"{self.val}"

        class Iterable:
            def __iter__(self):
                return iter(
                    [
                        Stringable(1.5),
                        Stringable(2),
                        Stringable("abc"),
                        Stringable("--123"),
                    ]
                )

        data_to_write = {"key3": Iterable(), "key1": 1, "key2": 2}
        data_to_check = {"key3": [1.5, 2, "abc", "--123"], "key1": 1, "key2": 2}
        self.write_read_assert(data_to_write, data_to_check)

    def tearDown(self):
        if os.path.exists(DATA_DIR):
            shutil.rmtree(DATA_DIR)

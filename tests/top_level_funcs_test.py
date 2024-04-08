# flake8: noqa: D101, D102
import os
import shutil
import unittest

import dh5
from dh5.errors import ReadOnlyKeyError

TEST_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(TEST_DIR, "tmp_test_data")
DATA_FILE_PATH = os.path.join(DATA_DIR, "some_data.h5")


class LoadTest(unittest.TestCase):
    """Testing dh5.load()."""

    data = {"a": 1, "b": 2}

    def setUp(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        dh5.DH5(data=self.data).save(filepath=DATA_FILE_PATH)

    def test_load_read(self):
        file = dh5.load(filepath=DATA_FILE_PATH, mode="r")
        for key, value in self.data.items():
            self.assertEqual(file[key], value)

        with self.assertRaises(ReadOnlyKeyError):
            file["c"] = 3

    def test_load_write(self):
        file = dh5.load(filepath=DATA_FILE_PATH, mode="w", overwrite=True)
        for key in self.data.keys():
            self.assertFalse(key in file)
        file["c"] = 3
        self.assertEqual(file["c"], 3)
        file.save()

        file2 = dh5.load(filepath=DATA_FILE_PATH, mode="r")
        self.assertEqual(file2["c"], 3)

    def test_load_append(self):
        file = dh5.load(filepath=DATA_FILE_PATH, mode="a")
        for key, value in self.data.items():
            self.assertEqual(file[key], value)
        file["c"] = 3
        file.save()

        file2 = dh5.load(filepath=DATA_FILE_PATH, mode="r")
        self.assertEqual(file2["c"], 3)
        for key, value in self.data.items():
            self.assertEqual(file2[key], value)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(DATA_DIR)


class SaveTest(unittest.TestCase):
    """Testing dh5.load()."""

    data = {"a": 1, "b": 2}

    def setUp(self):
        os.makedirs(DATA_DIR, exist_ok=True)

    def test_save(self):
        file = dh5.save(DATA_FILE_PATH, self.data)
        for key, value in self.data.items():
            self.assertEqual(file[key], value)

        file2 = dh5.load(filepath=DATA_FILE_PATH, mode="r")
        for key, value in self.data.items():
            self.assertEqual(file2[key], value)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(DATA_DIR)

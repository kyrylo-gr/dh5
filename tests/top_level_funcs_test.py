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
    data2 = {"c": 3, "d": 4}

    def setUp(self):
        os.makedirs(DATA_DIR, exist_ok=True)

    def test_save_new(self):
        file = dh5.save(self.data, DATA_FILE_PATH)
        for key, value in self.data.items():
            self.assertEqual(file[key], value)

        file2 = dh5.load(filepath=DATA_FILE_PATH, mode="r")
        for key, value in self.data.items():
            self.assertEqual(file2[key], value)

    def test_save_overwrite_unset(self):
        dh5.save(self.data, DATA_FILE_PATH)

        with self.assertRaises(FileExistsError):
            dh5.save(self.data, DATA_FILE_PATH)

    def test_save_overwrite_false(self):
        dh5.save(self.data, DATA_FILE_PATH)
        file = dh5.save(self.data2, DATA_FILE_PATH, overwrite=False).load()

        for key, value in {**self.data, **self.data2}.items():
            self.assertEqual(file[key], value)

        file2 = dh5.load(filepath=DATA_FILE_PATH, mode="r")
        for key, value in {**self.data, **self.data2}.items():
            self.assertEqual(file2[key], value)

    def test_save_overwrite_true(self):
        dh5.save(self.data, DATA_FILE_PATH, overwrite=True)
        file = dh5.save(self.data2, DATA_FILE_PATH, overwrite=True).load()
        for key, value in self.data2.items():
            self.assertEqual(file[key], value)
        for key in self.data.keys():
            self.assertFalse(key in file, msg=f"key: {key} in file: {file}")

        file2 = dh5.load(filepath=DATA_FILE_PATH, mode="r")
        for key, value in self.data2.items():
            self.assertEqual(file2[key], value)
        for key in self.data:
            self.assertFalse(key in file2)

    def test_save_append(self):
        dh5.save(self.data, DATA_FILE_PATH)
        file = dh5.save(self.data2, DATA_FILE_PATH, mode="a").load()
        for key, value in {**self.data, **self.data2}.items():
            self.assertEqual(file[key], value)

        file2 = dh5.load(filepath=DATA_FILE_PATH, mode="r")
        for key, value in {**self.data, **self.data2}.items():
            self.assertEqual(file2[key], value)

    def tearDown(self):
        if os.path.exists(DATA_FILE_PATH):
            os.remove(DATA_FILE_PATH)
        # shutil.rmtree(DATA_DIR)

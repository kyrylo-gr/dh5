# flake8: noqa: D100, D101, D102
import os
import shutil

# import shutil

import unittest

import numpy as np

from dh5 import DH5
from dh5.dh5_types import SyncNp

TEST_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(TEST_DIR, "tmp_test_data")
DATA_FILE_PATH = os.path.join(DATA_DIR, "some_data.h5")


class H5NpArraySaveOnEditTest(unittest.TestCase):
    """Saving different type of variables inside h5."""

    check: np.ndarray

    def setUp(self):
        self.create_file("test")

    def create_file(self, key):
        self.sd = DH5(DATA_FILE_PATH, save_on_edit=True, overwrite=True)
        self.size = (100, 1000)
        self.check = np.zeros(shape=self.size)
        self.sd[key] = SyncNp(self.check)

    def assert_arrays_equal(self, data, check):
        self.assertTrue(
            self.compare_np_array(data, check),
            msg=f"In loaded file:\n {data}\n vs\n {check}",
        )

    def compare(self):
        self.assert_arrays_equal(self.sd["test"], self.check)
        sd = DH5(DATA_FILE_PATH)
        self.assert_arrays_equal(sd["test"], self.check)

    @staticmethod
    def compare_np_array(a1, a2):
        return np.all(a1 == a2)

    @staticmethod
    def create_random_data(size=1000):
        return np.random.randint(0, 100, size)

    def test_zeros(self):
        self.compare()

    def test_file_is_overwritten(self):
        self.create_file("test2")
        self.assertNotIn("test", self.sd)
        self.assertIn("test2", self.sd)

    def test_new_from_list(self):
        self.check = np.array([1, 2, 3])
        self.sd["test"] = SyncNp([1, 2, 3])
        self.compare()

    def test_new_from_shape(self):
        self.check = np.zeros((1, 2, 3))
        self.sd["test"] = SyncNp((1, 2, 3))
        self.compare()

    def test_new_from_np_array(self):
        self.check = np.array([1, 2, 3])
        self.sd["test"] = SyncNp(self.check)
        self.compare()

    def test_new_from_syncnp(self):
        self.check = SyncNp(np.array([1, 2, 3]))
        self.sd["test"] = SyncNp(self.check)
        self.compare()

    def test_horizontal_change(self):
        data = self.create_random_data(self.size[1])
        self.sd["test"][1, :] = data
        self.check[1, :] = data

        self.compare()

    def test_vertical_change(self):
        data = self.create_random_data(self.size[0])
        self.sd["test"][:, 2] = data
        self.check[:, 2] = data

        self.compare()

    def test_sequential_run(self):
        self.check = np.array([1, 2, 3])
        self.sd["test"] = SyncNp([1, 2, 3])
        self.compare()

        self.check = np.array([4, 5, 6])
        self.sd["test"] = SyncNp([4, 5, 6])
        self.compare()

    def test_for_data(self):
        for i in range(self.size[0]):
            data = self.create_random_data(self.size[1])
            self.sd["test"][i, :] = data
            self.check[i, :] = data

        self.compare()

    def test_changing_before_assign(self):
        data = SyncNp(np.array([1, 2, 3]))
        data[0] = 4

        self.check = data
        self.sd["test"] = data
        self.compare()

    def test_saving_before_assign(self):
        data = SyncNp(np.array([1, 2, 3]))
        data.save()

        data[0] = 4

        with self.assertRaises(ValueError):
            data.save()

    @classmethod
    def tearDownClass(cls):
        """Remove tmp_test_data directory ones all test finished."""
        # data_directory = os.path.join(os.path.dirname(__file__), DATA_DIR)
        if os.path.exists(DATA_DIR):
            shutil.rmtree(DATA_DIR)
        return super().tearDownClass()


class H5NpArrayTest(H5NpArraySaveOnEditTest):
    def setUp(self):
        self.sd = DH5(DATA_FILE_PATH, save_on_edit=False, overwrite=True)
        self.size = (100, 1000)
        self.check = np.zeros(shape=self.size)
        self.sd["test"] = SyncNp(self.check)

    def compare(self):  # pylint: disable=W0221
        self.sd["test"].save()  # pylint: disable=E1101 # type: ignore
        return super().compare()


class H5NpArrayGlobalSaveTest(H5NpArrayTest):
    def setUp(self):
        super().setUp()
        self.sd.save()

    def compare(self):
        self.sd.save()
        return super().compare()


class H5NpArrayForceGlobalSaveTest(H5NpArraySaveOnEditTest):
    def compare(self):  # pylint: disable=W0221
        self.sd.save(force=True)
        return super().compare()


if __name__ == "__main__":
    unittest.main()

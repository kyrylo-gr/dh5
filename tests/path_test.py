# flake8: noqa: D101, D102
import unittest
from dh5.path import Path, get_file_path
import os
import shutil

TEST_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(TEST_DIR, "tmp_test_data")


class TestPath(unittest.TestCase):
    def test_addition(self):
        # Test the addition of two paths
        path1 = Path("/path/to")
        path2 = "directory"
        self.assertEqual((path1 + path2).str, "/path/todirectory")

    def test_path_addition(self):
        # Test the addition of two paths
        path1 = Path("/path/to")
        path2 = Path("directory")
        self.assertEqual((path1 + path2).str, "/path/todirectory")

    def test_makedirs(self):
        # Test the makedirs functionality
        # You might need to use a temporary directory for this
        path = Path(DATA_DIR) / "test_folder"
        path.makedirs()
        self.assertTrue(os.path.exists(path.absolute().str))

    def test_make_extension(self):
        # Test the make_extension functionality
        path = Path("some_file")
        self.assertEqual(path.make_extension(".txt").str, "some_file.txt")

    def test_make_list_extension(self):
        # Test the make_extension functionality
        path = Path("some_file")
        self.assertEqual(path.make_extension([".txt", ".pdf"]).str, "some_file.txt")

    def test_make_extension_error(self):
        # Test the make_extension functionality
        path = Path("some_file")
        with self.assertRaises(ValueError):
            path.make_extension(1)

    def test_make_second_extension(self):
        # Test the make_extension functionality
        path = Path("some_file.pdf")
        self.assertEqual(path.make_extension(".txt").str, "some_file.pdf.txt")

    def test_make_existed_extension(self):
        # Test the make_extension functionality
        path = Path("some_file.txt")
        self.assertEqual(path.make_extension(".txt").str, "some_file.txt")

    def test_make_list_existed_extension(self):
        # Test the make_extension functionality
        path = Path("some_file.txt")
        self.assertEqual(path.make_extension([".txt", ".pdf"]).str, "some_file.txt")

    def test_dirname(self):
        # Test the dirname property
        path = Path("/path/to/file.txt")
        self.assertEqual(path.dirname.str, "/path/to")

    def test_basename(self):
        # Test the basename property
        path = Path("/path/to/file.txt")
        self.assertEqual(path.basename.str, "file.txt")

    @classmethod
    def tearDownClass(cls):
        """Remove tmp_test_data directory ones all test finished."""
        # data_directory = os.path.join(os.path.dirname(__file__), DATA_DIR)
        if os.path.exists(DATA_DIR):
            shutil.rmtree(DATA_DIR)
        return super().tearDownClass()


class TestGetFilePath(unittest.TestCase):
    def test_filename_only(self):
        # Test with only a filename
        filename = "testfile"
        result = get_file_path(filename)
        self.assertEqual(result.str, "testfile")

    def test_filename_with_extension(self):
        # Test with a filename and extension
        filename = "testfile"
        result = get_file_path(filename, extension=".txt")
        self.assertEqual(result.str, "testfile.txt")

    def test_filename_with_path(self):
        # Test with a filename and path
        filename = "testfile"
        path = "/path/to"
        result = get_file_path(filename, path=path)
        self.assertEqual(result.str, "/path/to/testfile")

    def test_filename_with_path_and_extension(self):
        # Test with a filename, path, and extension
        filename = "testfile"
        path = "/path/to"
        result = get_file_path(filename, path=path, extension=".txt")
        self.assertEqual(result.str, "/path/to/testfile.txt")


if __name__ == "__main__":
    unittest.main()

# flake8: noqa: D101, D102
import unittest
from dh5.utils import random_utils


class RandomUtilsTestCase(unittest.TestCase):
    def test_get_timestamp(self):
        timestamp = random_utils.get_timestamp()
        self.assertIsInstance(timestamp, str)
        self.assertRegex(timestamp, r"\d{4}_\d{2}_\d{2}__\d{2}_\d{2}_\d{2}")


class TestLstripInt(unittest.TestCase):
    def test_valid_timestamp(self):
        # Test case with valid timestamp
        self.assertEqual(random_utils.lstrip_int("12345__Abc__678"), ("12345", "Abc", "678"))
        self.assertEqual(
            random_utils.lstrip_int("123-456__Abc__789"), ("123-456", "Abc", "789")
        )  # Timestamp with hyphen
        self.assertEqual(
            random_utils.lstrip_int("2023_01_10__12_14_15__some_name__1"),
            ("2023_01_10__12_14_15", "some_name", "1"),
        )  # Timestamp with underscore

        self.assertEqual(
            random_utils.lstrip_int("2023_01_10__12_14_15__some_name__a"),
            ("2023_01_10__12_14_15", "some_name__a", ""),
        )  # No numerical suffix

    def test_no_timestamp(self):
        # Test case with no timestamp
        self.assertIsNone(random_utils.lstrip_int("NoTimeStampHere"))

    def test_invalid_timestamp_format(self):
        # Test case with invalid timestamp format
        self.assertIsNone(random_utils.lstrip_int("invalid_123_timestamp"))

    def test_edge_cases(self):
        # Test cases with different edge cases
        self.assertIsNone(random_utils.lstrip_int(""))  # Empty string
        self.assertIsNone(random_utils.lstrip_int("_123__456"))  # No main part


class TestGetPathFromFilename(unittest.TestCase):
    def test_with_full_path(self):
        # Test case with full path
        self.assertEqual(
            random_utils.get_path_from_filename("/path/to/file.h5"), "/path/to/file.h5"
        )
        self.assertEqual(
            random_utils.get_path_from_filename("C:\\path\\to\\file.h5"), "C:\\path\\to\\file.h5"
        )

    def test_with_h5_extension(self):
        # Test case with '.h5' extension
        self.assertEqual(random_utils.get_path_from_filename("file.h5"), "file")

    def test_with_timestamp_and_suffix(self):
        # Test case with timestamp and suffix
        self.assertEqual(
            random_utils.get_path_from_filename("12345__Abc__678.h5"), ("Abc", "12345__Abc__678")
        )

    def test_plain_filename(self):
        # Test case with plain filename
        self.assertEqual(random_utils.get_path_from_filename("plainfile"), "plainfile")

    def test_edge_cases(self):
        # Test cases with different edge cases
        self.assertEqual(random_utils.get_path_from_filename(""), "")  # Empty string
        self.assertEqual(
            random_utils.get_path_from_filename("12345_"), "12345_"
        )  # Timestamp without main part


if __name__ == "__main__":
    unittest.main()

import unittest
from mock import mock_open, patch, call

from main import set_mocks_folder


class TestMain(unittest.TestCase):
    def test_set_mocks_folder(self):
        with patch("builtins.open", mock_open(read_data="data")) as mock_file:
            set_mocks_folder("test_mock_folder")
            mock_file.assert_has_calls([call().write("test_mock_folder")])


if __name__ == '__main__':
    unittest.main()
import unittest
from mock import mock_open, patch, call

from main import set_mocks_folder, set_mock_output, ENDPOINT_SET_MOCKS_FOLDER, ENDPOINT_SET_MOCK_OUTPUT


class TestMain(unittest.TestCase):
    def test_set_mocks_folder(self):
        with patch("builtins.open", mock_open(read_data="data")) as mock_file:
            set_mocks_folder("test_mock_folder")
            mock_file.assert_called_with(ENDPOINT_SET_MOCKS_FOLDER, 'w')
            mock_file.assert_has_calls([call().write("test_mock_folder")])

    def test_set_mock_output(self):
        with patch("builtins.open", mock_open(read_data="data")) as mock_file:
            set_mock_output("test_mock_output")
            mock_file.assert_called_with(ENDPOINT_SET_MOCK_OUTPUT, 'w')
            mock_file.assert_has_calls([call().write("test_mock_output")])


if __name__ == '__main__':
    unittest.main()
import unittest
from mock import mock_open, patch, call, MagicMock

from main import set_mocks_folder, set_mock_output, ENDPOINT_SET_MOCKS_FOLDER, ENDPOINT_SET_MOCK_OUTPUT, get_response, \
    get_mocks_folder, MOCKS_FOLDER_FILE_NAME


class TestMainSetMocksFolder(unittest.TestCase):
    def test_set_mocks_folder(self):
        with patch("builtins.open", mock_open(read_data="data")) as mock_file:
            set_mocks_folder("test_mock_folder")
            mock_file.assert_called_with(ENDPOINT_SET_MOCKS_FOLDER, 'w')
            mock_file.assert_has_calls([call().write("test_mock_folder")])


class TestMainSetMockOutput(unittest.TestCase):

    def test_set_mock_output(self):
        with patch("builtins.open", mock_open(read_data="data")) as mock_file:
            set_mock_output("test_mock_output")
            mock_file.assert_called_with(ENDPOINT_SET_MOCK_OUTPUT, 'w')
            mock_file.assert_has_calls([call().write("test_mock_output")])


class TestMainGetResponse(unittest.TestCase):
    def test_get_response_empty_request(self):
        with patch("builtins.open", mock_open(read_data='test: testaja')) as mock_file:
            get_response("testfile.txt", {}, {})
            mock_file.assert_called_with('testfile.txt')

    def test_get_response_method_but_empty_request(self):
        with patch("builtins.open", mock_open(read_data='method: POST')) as mock_file:
            get_response("testfile.txt", {}, {})
            mock_file.assert_called_with('testfile.txt')

    def test_get_response_path_but_empty_request(self):
        with patch("builtins.open", mock_open(read_data='path: sample_path')) as mock_file:
            get_response("testfile.txt", {}, {})
            mock_file.assert_called_with('testfile.txt')

    def test_get_response_path_and_current_req(self):
        with patch("builtins.open", mock_open(read_data='path: sample_path')) as mock_file:
            get_response("testfile.txt", {'path': "different_sample_path"}, {})
            mock_file.assert_called_with('testfile.txt')

    def test_get_response_body_but_empty_request(self):
        with patch("builtins.open", mock_open(read_data='body: sample_body')) as mock_file:
            get_response("testfile.txt", {}, {})
            mock_file.assert_called_with('testfile.txt')

    def test_get_response_body_and_current_req(self):
        with patch("builtins.open", mock_open(read_data='body: sample_body')) as mock_file:
            get_response("testfile.txt", {'body': 'diff_sample_body'}, {})
            mock_file.assert_called_with('testfile.txt')

    @patch('requests.request')
    @patch('main.write_mock_yaml_file')
    def test_get_response_reference(self, mock_write: MagicMock, mock_requests: MagicMock):
        with patch("builtins.open", mock_open(read_data='reference: test_reference')) as mock_file:
            mock_origin_request = MagicMock()
            get_response("testfile.txt", {}, mock_origin_request)
            mock_file.assert_called_with('testfile.txt')

            calls = [call.get_data()]
            mock_origin_request.assert_has_calls(calls=calls, any_order=True)

            mock_requests.assert_called_once()
            mock_write.assert_called_once()


class TestMainGetMocksFolder(unittest.TestCase):
    @patch('main.path')
    def test_get_mocks_folder_path_exist(self, mock_path: MagicMock):
        with patch("builtins.open", mock_open(read_data="data_result")) as mock_file:
            mock_path.exists.return_value = True
            result = get_mocks_folder()
            mock_file.assert_called_with(MOCKS_FOLDER_FILE_NAME, 'r')
            assert result == 'data_result'
            
    @patch('main.path')
    def test_get_mocks_folder_path_not_exist(self, mock_path: MagicMock):
        with patch("builtins.open", mock_open(read_data="data")) as mock_file:
            mock_path.exists.return_value = False
            result = get_mocks_folder()
            assert result == "mocks"


if __name__ == '__main__':
    unittest.main()

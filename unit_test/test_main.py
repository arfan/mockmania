import unittest
from mock import mock_open, patch, call, MagicMock

from main import set_mocks_folder, set_mock_output, ENDPOINT_SET_MOCKS_FOLDER, ENDPOINT_SET_MOCK_OUTPUT, get_response, \
    get_mocks_folder, MOCKS_FOLDER_FILE_NAME, read_mock_list, get_mock_filename, represent_int, write_mock_yaml_file, \
    write_raw_mock_yaml_file


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

    @patch('os.remove')
    def test_get_response_with_delete(self, mock_os_remove: MagicMock):
        with patch("builtins.open", mock_open(read_data='delete: true')) as mock_file:
            get_response("testfile.txt", {}, {})
            mock_os_remove.assert_called_once_with('testfile.txt')

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


class TestMainReadMockList(unittest.TestCase):
    @patch('os.walk')
    @patch('os.path.join')
    def test_read_mock_list(self, mock_os_path_join: MagicMock, mock_os_walk: MagicMock):
        mock_os_walk.return_value = [('t_root', 't_directories', ['file1', 'file2'])]
        read_mock_list('test_mock_list_folder')
        mock_os_walk.assert_called_with("test_mock_list_folder")
        calls = [
            call('t_root', 'file1'),
            call('t_root', 'file2')
        ]
        mock_os_path_join.assert_has_calls(calls=calls, any_order=True)


class TestMainGetMockFilename(unittest.TestCase):
    @patch('time.time')
    def test_get_mock_filename(self,
                               mock_time_time: MagicMock):
        mock_time_time.return_value = 1583603908950.12332234
        result = get_mock_filename('test_path', 'test_mock_list_folder', 'POST')
        self.assertEqual(result, 'test_mock_list_folder/POST_test_path_1583603908950123.yaml')


class TestMainRepresentInt(unittest.TestCase):
    def test_represent_int_false(self):
        result = represent_int('1231231xxxx')
        self.assertEqual(result, False)

    def test_represent_int_true(self):
        result = represent_int('1231231')
        self.assertEqual(result, True)


class TestMainWriteMockYamlFile(unittest.TestCase):
    def test_write_mock_yaml_file(self):
        with patch("builtins.open", mock_open(read_data="data")) as mock_file:
            write_mock_yaml_file("test_file_name.yaml", {}, "response")
            mock_file.assert_called_with("test_file_name.yaml", 'w')
            mock_file.assert_has_calls([call().write('response: response\n')])

    @patch('yaml.dump')
    def test_write_mock_yaml_file_exception_when_writing(self, mock_yaml_dump):
        mock_openfile = mock_open(read_data="data")
        mock_yaml_dump.side_effect = [Exception]
        with patch("builtins.open", mock_openfile) as mock_file:
            with self.assertRaises(Exception): write_mock_yaml_file("test_file_name.yaml", {}, "response")


class TestMainWriteRawMockYamlFile(unittest.TestCase):
    def test_write_raw_mock_yaml_file(self):
        with patch("builtins.open", mock_open(read_data="data")) as mock_file:
            write_raw_mock_yaml_file("test_file_name.yaml", {})
            mock_file.assert_called_with("test_file_name.yaml", 'w')

    def test_write_raw_mock_yaml_file_exception(self):
        with self.assertRaises(Exception): write_raw_mock_yaml_file("asjfalsdjflaksjdflasdf/test_file_name.yaml", {})


if __name__ == '__main__':
    unittest.main()

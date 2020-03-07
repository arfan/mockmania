import unittest

from mock import patch, MagicMock, mock_open

from main import app, MOCK_OUTPUT_FILE_NAME


class HandlerTests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################

    # executed prior to each test
    def setUp(self):
        # app.config['TESTING'] = True
        # app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

    # executed after each test
    def tearDown(self):
        pass

    ###############
    #### tests ####
    ###############

    @patch('os.path.isfile')
    @patch('os.remove')
    def test_handler_default_output_true(self,
                                         mock_os_remove: MagicMock,
                                         mock_os_path_isfile: MagicMock):
        with patch("builtins.open", mock_open(read_data="default_output")) as mock_file:
            mock_os_path_isfile.return_value = True
            response = self.app.get('/', follow_redirects=True)
            mock_os_remove.assert_called_with(MOCK_OUTPUT_FILE_NAME)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, b'default_output')

    @patch('main.write_mock_yaml_file')
    @patch('main.get_mocks_folder')
    @patch('main.read_mock_list')
    @patch('main.get_mock_filename')
    @patch('os.path.isfile')
    def test_handler_root_url(self,
                              mock_os_path_isfile: MagicMock,
                              mock_get_mock_filename: MagicMock,
                              mock_read_mock_list: MagicMock,
                              mock_get_mocks_folder: MagicMock,
                              mock_write_mock_yaml_file: MagicMock):
        mock_os_path_isfile.return_value = False
        mock_get_mocks_folder.return_value = "test_mock_folder"
        mock_read_mock_list.return_value = []
        mock_get_mock_filename.return_value = "test_mock_file_name"

        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"CHANGEME in file test_mock_file_name")
        mock_write_mock_yaml_file.assert_called_with('test_mock_file_name',
                                                     {'method': 'GET', 'path': ''},
                                                     'CHANGEME in file test_mock_file_name')

    @patch('main.write_mock_yaml_file')
    @patch('main.get_mocks_folder')
    @patch('main.read_mock_list')
    @patch('main.get_mock_filename')
    @patch('os.path.isfile')
    def test_handler_root_url_with_query_string(self,
                                                mock_os_path_isfile: MagicMock,
                                                mock_get_mock_filename: MagicMock,
                                                mock_read_mock_list: MagicMock,
                                                mock_get_mocks_folder: MagicMock,
                                                mock_write_mock_yaml_file: MagicMock):
        mock_os_path_isfile.return_value = False
        mock_get_mocks_folder.return_value = "test_mock_folder"
        mock_read_mock_list.return_value = []
        mock_get_mock_filename.return_value = "test_mock_file_name"

        response = self.app.get('/?query=12345', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"CHANGEME in file test_mock_file_name")
        mock_write_mock_yaml_file.assert_called_with('test_mock_file_name',
                                                     {'method': 'GET', 'path': '?query=12345'},
                                                     'CHANGEME in file test_mock_file_name')

    @patch('os.path.isfile')
    @patch('main.set_mocks_folder')
    def test_handler_root_url_special_command_set_mocks_folder(self,
                                                               mock_set_mocks_folder: MagicMock,
                                                               mock_os_path_isfile: MagicMock):
        mock_os_path_isfile.return_value = False
        response = self.app.put('/mocks_folder', follow_redirects=True, data="test_mocks_folder")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"msg":"ok"}')
        mock_set_mocks_folder.assert_called_once_with("test_mocks_folder")

    @patch('os.path.isfile')
    @patch('main.set_mock_output')
    def test_handler_root_url_special_command_set_mock_output(self,
                                                               set_mock_output: MagicMock,
                                                               mock_os_path_isfile: MagicMock):
        mock_os_path_isfile.return_value = False
        response = self.app.put('/mock_output', follow_redirects=True, data="test_mock_output")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"msg":"ok"}')
        set_mock_output.assert_called_once_with("test_mock_output")

    @patch('os.path.isfile')
    @patch('main.write_raw_mock_yaml_file')
    def test_handler_root_url_special_command_write_mock_bad_request(self,
                                                               mock_write_raw_mock_yaml_file: MagicMock,
                                                               mock_os_path_isfile: MagicMock):
        mock_os_path_isfile.return_value = False
        response = self.app.put('/mock_write', follow_redirects=True, data="test_mock_output: test")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'{"msg":"location not valid"}')

    @patch('os.path.isfile')
    @patch('main.write_raw_mock_yaml_file')
    def test_handler_root_url_special_command_write_mock_valid_location(self,
                                                               mock_write_raw_mock_yaml_file: MagicMock,
                                                               mock_os_path_isfile: MagicMock):
        mock_os_path_isfile.return_value = False
        response = self.app.put('/mock_write', follow_redirects=True, data='location: test_location.yaml')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{"msg":"ok"}')
        mock_write_raw_mock_yaml_file.assert_called_once_with('test_location.yaml', 'location: test_location.yaml')

if __name__ == "__main__":
    unittest.main()

# project/test_basic.py


import os
import unittest

from mock import patch, MagicMock, mock_open

from main import app, MOCK_OUTPUT_FILE_NAME

TEST_DB = 'test.db'


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

    @patch('main.write_mock_yaml_file')
    @patch('main.get_mocks_folder')
    @patch('main.read_mock_list')
    @patch('main.get_mock_filename')
    @patch('os.path.isfile')
    @patch('os.remove')
    def test_handler_default_output_true(self,
                       mock_os_remove: MagicMock,
                       mock_os_path_isfile: MagicMock,
                       mock_get_mock_filename: MagicMock,
                       mock_read_mock_list:MagicMock,
                       mock_get_mocks_folder:MagicMock,
                       mock_write_mock_yaml_file: MagicMock):
        with patch("builtins.open", mock_open(read_data="default_output")) as mock_file:
            mock_os_path_isfile.return_value = True
            response = self.app.get('/', follow_redirects=True)
            mock_os_remove.assert_called_with(MOCK_OUTPUT_FILE_NAME)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, b'default_output')


if __name__ == "__main__":
    unittest.main()
import sys
import unittest

import mock
from mock import patch, MagicMock

import main


class TestMainBoilerplate(unittest.TestCase):
    def test_init_boilerplate(self):
        with mock.patch.object(main, "main", return_value=42):
            with mock.patch.object(main, "__name__", "__main__"):
                with mock.patch.object(main.sys, 'exit') as mock_exit:
                    main.init()
                    assert mock_exit.call_args[0][0] == 42

    @patch('main.app')
    def test_main_boilerplate(self, mock_app: MagicMock):
        old_sys_argv = sys.argv
        sys.argv = ['main.py']

        try:
            main.main()
            mock_app.run.assert_called_with(host='0.0.0.0', port=7000)
        finally:
            sys.argv = old_sys_argv

    @patch('main.app')
    def test_main_boilerplate_with_argument(self, mock_app: MagicMock):
        old_sys_argv = sys.argv
        sys.argv = ['main.py', "7777"]

        try:
            main.main()
            mock_app.run.assert_called_with(host='0.0.0.0', port=7777)
        finally:
            sys.argv = old_sys_argv


    @patch('main.app')
    @patch('builtins.print')
    def test_main_boilerplate_with_argument_error(self, mock_print:MagicMock, mock_app: MagicMock):
        old_sys_argv = sys.argv
        sys.argv = ['main.py', "asdfasdkfajlsdfjlds"]

        try:
            main.main()
            mock_app.run.assert_not_called()
        finally:
            sys.argv = old_sys_argv



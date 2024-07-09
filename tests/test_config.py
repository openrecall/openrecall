import pytest, sys
from unittest import mock
from openrecall.config import get_appdata_folder, screenshots_path, db_path

def test_get_appdata_folder_windows(tmp_path):
    with mock.patch('sys.platform', 'win32'):
        with mock.patch.dict('os.environ', {'APPDATA': str(tmp_path)}):
            expected_path = tmp_path / 'openrecall'
            assert get_appdata_folder() == str(expected_path)
            assert expected_path.exists()

def test_get_appdata_folder_windows_no_appdata():
    with mock.patch('sys.platform', 'win32'):
        with mock.patch.dict('os.environ', {}, clear=True):
            with pytest.raises(EnvironmentError, match="APPDATA environment variable is not set."):
                get_appdata_folder()

def test_get_appdata_folder_darwin(tmp_path):
    with mock.patch('sys.platform', 'darwin'):
        with mock.patch('os.path.expanduser', return_value=str(tmp_path)):
            expected_path = tmp_path / 'Library' / 'Application Support' / 'openrecall'
            assert get_appdata_folder() == str(expected_path)
            assert expected_path.exists()

def test_get_appdata_folder_linux(tmp_path):
    with mock.patch('sys.platform', 'linux'):
        with mock.patch('os.path.expanduser', return_value=str(tmp_path)):
            expected_path = tmp_path / '.local' / 'share' / 'openrecall'
            assert get_appdata_folder() == str(expected_path)
            assert expected_path.exists()

def test_check_python_version():
    with pytest.raises(SystemExit) :
        check_python_version(version="3.12")
    check_python_version("3.11")
    check_python_version(version="3.9")
   
#Test if database exists
def test_if_database_exists (tmp_path):
    assert (tmp_path / db_path).exists()
#Test if screenshot file exists

def test_if_screenshot_path_exists (tmp_path):
    assert (tmp_path / screenshots_path).exists()


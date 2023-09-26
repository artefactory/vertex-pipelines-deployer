from pathlib import Path
from unittest.mock import patch

import pytest

from deployer.utils.utils import make_enum_from_python_package_dir


class TestMakeEnumFromPythonPackageDir:
    @patch(
        "pathlib.Path.glob", return_value=[Path("file1.py"), Path("file2.py"), Path("__init__.py")]
    )
    @patch("pathlib.Path.exists", return_value=True)
    def test_enum_created_succesfully(self, mock_exists, mock_glob):
        # Given
        dir_path = Path("path/to/directory")

        # When
        enum = make_enum_from_python_package_dir(dir_path, raise_if_not_found=True)

        # Then
        assert len(enum) == 2
        mock_glob.assert_called_once_with("*.py")
        mock_exists.assert_called_once()

    @patch("pathlib.Path.glob", return_value=[Path("__init__.py")])
    @patch("pathlib.Path.exists", return_value=True)
    def test_enum_created_only_init_in_directory(self, mock_exists, mock_glob):
        # Given
        dir_path = Path("path/to/directory")

        # When
        enum = make_enum_from_python_package_dir(dir_path, raise_if_not_found=True)

        # Then
        assert len(enum) == 0
        mock_glob.assert_called_once_with("*.py")
        mock_exists.assert_called_once()

    @patch("pathlib.Path.glob", return_value=[Path("file1.py"), Path("file2.py")])
    @patch("pathlib.Path.exists", return_value=True)
    def test_enum_values_match_file_names(self, mock_exists, mock_glob):
        # Given
        dir_path = Path("path/to/directory")

        # When
        enum = make_enum_from_python_package_dir(dir_path, raise_if_not_found=True)

        # Then
        assert enum.file1.value == "file1"
        assert enum.file2.value == "file2"
        mock_glob.assert_called_once_with("*.py")
        mock_exists.assert_called_once()

    @patch("pathlib.Path.glob", return_value=[Path("file1.py"), Path("file2.py")])
    def test_directory_does_not_exist(self, mock_glob):
        # Given
        dir_path = Path("path/to/directory")

        # When
        dir_path = Path("nonexistent/directory")
        with pytest.raises(FileNotFoundError):
            make_enum_from_python_package_dir(dir_path, raise_if_not_found=True)

        mock_glob.assert_not_called()

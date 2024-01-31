from pathlib import Path
from unittest.mock import patch

import pytest
from conftest import exception_traceback

from deployer.utils.utils import filter_lines_from, make_enum_from_python_package_dir


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


class TestFilterLinesFrom:
    try:
        raise Exception("This is an exception.")
    except Exception as e:
        traceback = e.__traceback__

    def test_pathlib_input(self):
        # Given
        internal_path = Path(__file__)
        external_path = Path("tests/conftest.py")

        # When
        internal_output = filter_lines_from(self.traceback, internal_path)
        external_output = filter_lines_from(exception_traceback, external_path)
        assert internal_output == (
            f'  File "{internal_path}", line 71, in TestFilterLinesFrom\n'
            '    raise Exception("This is an exception.")\n'
        )
        assert external_output == (
            f'  File "{external_path.resolve()}", line 19, in <module>\n'
            '    raise Exception("This is an exception.")\n'
        )

    def test_string_input(self):
        # Given
        internal_path = str(Path(__file__))
        external_path = "tests/conftest.py"

        # When
        internal_output = filter_lines_from(self.traceback, internal_path)
        external_output = filter_lines_from(exception_traceback, external_path)
        print(internal_output)
        assert internal_output == (
            f'  File "{internal_path}", line 71, in TestFilterLinesFrom\n'
            '    raise Exception("This is an exception.")\n'
        )
        assert external_output == (
            f'  File "{Path(external_path).resolve()}", line 19, in <module>\n'
            '    raise Exception("This is an exception.")\n'
        )

    def test_empty_result(self):
        # Given
        path = Path(__file__)

        # When
        output = filter_lines_from(exception_traceback, path)
        assert output == "Could not find potential source of error."

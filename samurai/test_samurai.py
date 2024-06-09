import shutil
import re
import pytest

from . import file_patterns, get_files, exclude_file, get_module_path, get_url


@pytest.fixture(scope="session", autouse=True)
def copy_views():
    """Copy the views folder of the demo_project project to this folder."""
    shutil.copytree("tests/demo_project/demo/views", "views")
    yield
    shutil.rmtree("views")


def test_get_files():
    """Test returned files in views folder"""
    views = [item.as_posix() for item in get_files("views")]
    output = [
        'views/current_time.py',
        'views/colors/add.py',
        'views/colors/__init__.py',
        'views/colors/<slug:slug>.py',
        'views/__init__.py',
    ]
    assert output == views


def test_exclude_file():
    """Test exclude file in views folder"""
    file_path = get_files("views")[0]
    excluded = exclude_file(file=file_path, exclude="*time.py")
    assert excluded


def test_get_module_path():
    """Test get module path function"""
    file_path = get_files("views")[1]
    module = get_module_path(file=file_path)
    assert "views.colors.add" == module


def test_get_url():
    """Test get url from file path"""
    file = get_files("views")[1]
    start_dir_re = re.compile("^views")
    url = get_url(file, start_dir_re, append_slash=False, view_fn="view_fn")
    assert url == "colors/add"


def test_append_slash():
    patterns = file_patterns("views", append_slash=True, exclude="")
    output = [(str(p.pattern), p.name) for p in patterns]
    assert output == [
        ("current_time/", "current_time"),
        ("colors/add/", "colors_add"),
        ("colors/", "colors"),
        ("colors/<slug:slug>/", "colors_slug"),
        ("", "home"),
    ]


def test_exclude_path():
    patterns = file_patterns("views", append_slash=False, exclude="*time.py")
    output = [(str(p.pattern), p.name) for p in patterns]
    assert output == [
        ("colors/add", "colors_add"),
        ("colors", "colors"),
        ("colors/<slug:slug>", "colors_slug"),
        ("", "home"),
    ]

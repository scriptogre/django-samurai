import re
from importlib import import_module

from samurai import get_files, exclude_file, get_module_path, get_url, file_patterns, \
    render_response


def test_get_files():
    """Test returned files in views folder"""
    views = [item.as_posix() for item in get_files("tests/views")]
    output = [
        'tests/views/current_time.py',
        'tests/views/colors/add.py',
        'tests/views/colors/__init__.py',
        'tests/views/colors/<slug:slug>.py',
        'tests/views/__init__.py',
    ]
    assert output == views


def test_exclude_file():
    """Test exclude file in views folder"""
    file_path = get_files("tests/views")[0]
    excluded = exclude_file(file=file_path, exclude="*time.py")
    assert excluded


def test_get_module_path():
    """Test get module path function"""
    file_path = get_files("tests/views")[1]
    module = get_module_path(file=file_path)
    assert "tests.views.colors.add" == module


def test_get_url():
    """Test get url from file path"""
    file = get_files("tests/views")[1]
    start_dir_re = re.compile("^tests/views")
    url = get_url(file, start_dir_re, append_slash=False, view_fn="view_fn")
    assert url == "colors/add"


def test_render_response():
    """Test render response function"""
    module_path = "tests.views"
    module = import_module(module_path)
    response = render_response(module, None)
    assert response is not None
    assert response.status_code == 200


def test_append_slash():
    patterns = file_patterns("tests/views", append_slash=True, exclude="")
    output = [(str(p.pattern), p.name) for p in patterns]
    assert output == [
        ("current_time/", "current_time"),
        ("colors/add/", "colors_add"),
        ("colors/", "colors"),
        ("colors/<slug:slug>/", "colors_slug"),
        ("/", "index"),
    ]


def test_exclude_path():
    patterns = file_patterns("tests/views", append_slash=False, exclude="*time.py")
    output = [(str(p.pattern), p.name) for p in patterns]
    assert output == [
        ("colors/add", "colors_add"),
        ("colors", "colors"),
        ("colors/<slug:slug>", "colors_slug"),
        ("", "index"),
    ]

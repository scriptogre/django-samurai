import pathlib
import re
from importlib import import_module

from django.http import HttpResponse
from django.template import RequestContext
from django.template.base import Template
from django.urls import path

__version__ = "0.1.0"

DISALLOWED_CHARS = re.compile(
    "|".join(
        [
            r"^_+",  # Leading underscores
            r"[<>]",  # Angle brackets (url param wrapper)
            r"\w+\:",  # Letters followed by colon (path converters)
            r"_+$",  # Trailing underscores
        ]
    )
)
TO_UNDERSCORES = re.compile("[/-]")  # Slash and dash


def file_patterns(start_dir: str, append_slash: bool = False, exclude: str = ""):
    """
    Create urlpatterns from a directory structure
    """
    patterns = []
    start_dir_re = re.compile(f"^{start_dir}")
    files = get_files(start_dir, exclude)

    for file in files:
        if exclude_file(file, exclude):
            continue

        module_path = get_module_path(file)
        module = import_module(module_path)
        view_fn = get_view_fn(module)

        if not is_callable(view_fn):
            continue

        url = get_url(file, start_dir_re, append_slash, view_fn)
        urlname = get_urlname(view_fn, url)

        patterns.append(path(url, view_fn, name=urlname))

    return patterns


def get_files(start_dir: str, exclude: str):
    """
    Get a list of files in the directory structure
    """
    files = pathlib.Path(start_dir).glob("**/*.py")
    return sorted(files, reverse=True, key=str)


def exclude_file(file: pathlib.Path, exclude: str):
    """
    Check if a file should be excluded
    """
    return exclude and pathlib.Path.match(file, exclude)


def get_module_path(file: pathlib.Path):
    """
    Get the module path from the file path
    """
    return str(file).replace(".py", "").replace("/", ".")


def get_view_fn(module):
    """
    Get the view function from the module
    """
    return getattr(module, "view", None)


def is_callable(fn):
    """
    Check if a function is callable
    """
    return callable(fn)


def get_url(file: pathlib.Path, start_dir_re: re.Pattern, append_slash: bool, view_fn):
    """
    Get the URL for the file
    """
    url = getattr(view_fn, "url", "")
    if not url:
        url = "" if file.name == "__init__.py" else file.name.replace(".py", "")
        url = start_dir_re.sub("", f"{file.parent}/{url}").strip("/")
        url = (url + "/") if append_slash and url != "" else url
    return url


def get_urlname(view_fn, url):
    """
    Get the URL name for the view function
    """
    urlname = getattr(view_fn, "urlname", "")
    if not urlname:
        urlname = DISALLOWED_CHARS.sub("", TO_UNDERSCORES.sub("_", url))
    return urlname


def render_str(source, request, context=None):
    """
    Take a string and respond with a fully rendered template
    """
    rendered = Template(source).render(RequestContext(request, context))
    return HttpResponse(rendered)

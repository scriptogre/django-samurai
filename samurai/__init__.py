import pathlib
import re
from importlib import import_module

from django.http import HttpResponse
from django.template import Context
from django.template.base import Template
from django.urls import path

__version__ = "0.1.0"

DISALLOWED_CHARS = re.compile(
    "|".join(
        [
            r"^_+",  # Leading underscores
            r"[<>]",  # Angle brackets (url param wrapper)
            r"\w+\:",  # Letters followed by a colon (path converters)
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
    files = get_files(start_dir)

    for file in files:
        if exclude_file(file, exclude):
            continue

        module_path = get_module_path(file)
        module = import_module(module_path)
        context = get_members(module)

        def view_fn(request, view_module=module, view_context=context):
            view_module.request = request
            return render_response(request, view_module, view_context)

        url = get_url(file, start_dir_re, append_slash, view_fn)
        url_name = get_url_name(url)

        patterns.append(path(url, view_fn, name=url_name))

    return patterns


def get_files(start_dir: str):
    """
    Get a list of files in the directory structure
    """
    files = pathlib.Path(start_dir).glob("**/*.py")
    return sorted(files, reverse=True, key=str)


def exclude_file(file: pathlib.Path, exclude: str):
    """
    Check if a file match excluded
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
        if file.name == "__init__.py" and file.parent.name == "views":
            url = ""
        elif file.name == "__init__.py":
            url = file.parent.name
        else:
            url = start_dir_re.sub("", f"{file.parent}/{file.stem}").strip("/")

    return url + "/" if append_slash else url


def get_url_name(url):
    """
    Get the URL name for the view function
    """
    if not url or url == "/":
        return "index"

    return DISALLOWED_CHARS.sub("", TO_UNDERSCORES.sub("_", url))


def get_members(module) -> dict[str, str]:
    """
    Return all members of a module.
    """
    excluded_members = [
        "__builtins__",
        "__cached__",
        "__doc__",
        "__file__",
        "__loader__",
        "__name__",
        "__package__",
        "__spec__",
        "template",
        "request",
    ]
    members = {
        name: getattr(module, name)
        for name in dir(module)
        if name not in excluded_members
    }
    return members


def render_response(request, module, context) -> HttpResponse:
    """
    Take a module and render the template with its docs.
    """
    # inject request into module
    module.request = request

    # get the template and render it
    template_str = module.template
    response = HttpResponse()
    template = Template(template_str)
    response.content = template.render(Context(context))
    return response

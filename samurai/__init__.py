import inspect
import pathlib
import re
from importlib import import_module

from django.http import HttpResponse
from django.template import RequestContext, Context
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
    files = get_files(start_dir)

    for file in files:
        if exclude_file(file, exclude):
            continue

        module_path = get_module_path(file)
        module = import_module(module_path)
        context = get_members(module)
        view_fn = render_response
        view_fn.module = module
        view_fn.context = context

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
    Check if a file should be excluded
    """
    return exclude and pathlib.Path.match(file, exclude)


def get_module_path(file: pathlib.Path):
    """
    Get the module path from the file path
    """
    return str(file).replace(".py", "").replace("/", ".")


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

    if append_slash:
        url += "/"

    return url


def get_url_name(url):
    """
    Get the URL name for the view function
    """
    if not url or url == "/":
        return "index"

    return DISALLOWED_CHARS.sub("", TO_UNDERSCORES.sub("_", url))


def render_str(source, request, context=None):
    """
    Take a string and respond with a fully rendered template
    """
    rendered = Template(source).render(RequestContext(request, context))
    return HttpResponse(rendered)


def get_members(module) -> dict[str, str]:
    """
    Return all members of a module.
    """
    members = {name: getattr(module, name) for name in dir(module)}
    return members


def extract_template_string(source_code: str) -> None | str:
    # Regular expression to find triple-quoted strings
    triple_quote_pattern = r'\"\"\"(.*?)\"\"\"|\'\'\'(.*?)\'\'\''
    matches = re.findall(triple_quote_pattern, source_code, re.DOTALL)

    # Assuming the template string is the last triple-quoted string in the source code
    if matches:
        template_string = matches[-1][0] if matches[-1][0] else matches[-1][1]
        return template_string.strip()
    return None


def render_response(module, context=None) -> HttpResponse:
    """
    Take a module and render the template string in the module
    """
    # Get the module's source code
    source_code = inspect.getsource(module)

    # Extract the template string from the source code
    template_str = extract_template_string(source_code)

    # Empty response if no template
    if not template_str:
        return HttpResponse(status=204)

    # Create a response object
    response = HttpResponse()

    # Create a template object
    template = Template(template_str)

    # Set the response content to the rendered template
    response.content = template.render(Context(context))

    return response

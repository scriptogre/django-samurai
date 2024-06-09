# Django Samurai
Django Samurai combines views & templates into a single `.py` file. It also provides type-safety using Pydantic, and 
adds file-based routing.

Why?:
- It make doing simple things simpler.
- An equivalent "modern" feel that you get when working with FastAPI, but for working with HTML.
- It pairs nicely with htmx.
- Why not.
 
This idea is heavily inspired by Astro's `.astro` file extension syntax.

How?:
Lets see two examples of doing the same thing with a traditional setup, and with django-samurai:

# Traditional Setup

## urls.py
Define the /add-user-message route

```python
from django.urls import path
from . import views

urlpatterns = [
    path('add-user-message/', views.add_user_message_view, name='add_user_message_view'),
]
```

## views.py
Get the message from form data, add HX-Trigger header to response

```python
from django import forms
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(["POST"])
def add_user_message_view(request):
	message = request.POST.get("message")
	context = {'message': message}
	headers = {'HX-Trigger': 'chatMessageAdded'}
    return render(request, context, headers=headers)
```

```html
## template

    <div class="chat-message">
        <span>{{ message }}</span>
    </div>
```

# django-samurai setup
```python
## views/add-user-message.py
# view logic goes here

response: HttpResponse
message: Form[str]

response.headers['HX-Trigger'] = 'chatMessageAdded'

"""
<!-- Response is the HTML defined here -->

<div class="chat-message">
	<span>{{ message }}</span>
</div>
"""
```

Explanation:
1. Route is defined using file-based routing:
	- <app>/views/add-user-message.py -> /add-user-message
2. message form data is retrieved using Form[str], like FastAPI/django-ninja (https://django-ninja.dev/guides/input/form-params/?h=form)
3. Response can be accessed and modified by having the response defined with response: HttpRespone. This would require some magic to work, but is doable.
4. The request could be accessed in the same way.
5. The returned response would always be an HTML template, which will be delimited/defined at the bottom of the file using triple quotes """You can think of these new files as view functions as files. Argument are defined using type hints, and the return value is always the HTML at the bottom.There's already an existing library that does 50% of what we need: https://github.com/jerivas/django-file-router/tree/main.
We can fork this and make it better.
We can also piggy back on django-ninja for the Pydantic validation.
The "magic"  would require most of the work.

## Installation

```
pip install django-samurai
```

Add this to your `urls.py`:

```python
from samurai import file_patterns

urlpatterns = [
	path("admin/", admin.site.urls),
	*file_patterns("myapp/views"),
]
```

With that single call to `file_patterns` the function will generate URL patterns for all your views automatically based on their folder structure inside `myapp/views`. For the file we created earlier at `myapp/views/mymodel/add.py` this will result in a url of `/mymodel/add`. Then by simply creating more files and folders the URL patterns will be updated without any manual input.

## Configuration

The `file_patterns` function accepts the following arguments:

| Arg | Description |
|---|---|
| `append_slash` | Boolean. If `True` will add a trailing slash to the generated patterns. |
| `exclude` | String (glob). If set each file will be checked against this pattern and excluded from the pattern generation process altogether. Useful if you want to completely avoid importing certain files (like tests). |

Alternatively you can add `url` and `urlname` properties to your `view`:

```python
def view(request):
    ...

view.url = "custom/url/path"
view.urlname = "my_custom_name"
```

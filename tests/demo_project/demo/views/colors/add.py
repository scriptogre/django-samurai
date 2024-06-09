"""
<h1>Add a new color</h1>

<form method="POST">
    {% csrf_token %}
    {{ form.as_p }}
    <input type="submit">
</form>
"""

from samurai import render_str


def view(request):
    return render_str(__doc__, request)

"""
<h1>{{ color.name }}</h1>
<p>The code is {{ color.code }}</p>
"""

from samurai import render_str


def view(request, slug):
    # color = get_object_or_404(Color, slug=slug)
    color = "test"
    return render_str(__doc__, request, {"color": color})
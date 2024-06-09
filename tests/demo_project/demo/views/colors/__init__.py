"""
<h1> Colors Home Page</h1>
"""


from samurai import render_str


def view(request):
    return render_str(__doc__, request)
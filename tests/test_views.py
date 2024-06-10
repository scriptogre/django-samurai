from samurai import render_response
from tests.views import colors as colors_list_view


def test_module_with_context():
    response = render_response(colors_list_view, context={"colors": ["red", "yellow", "blue"]})
    assert "Colors: red yellow blue" in response.content.decode()


def test_module_without_context():
    response = render_response(colors_list_view)
    assert "Colors:" in response.content.decode()
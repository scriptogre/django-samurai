"""
<h1>Add a new color</h1>

<form method="POST">
    {% csrf_token %}
    {{ form.as_p }}
    <input type="submit">
</form>
"""

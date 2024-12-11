{% extends "base.html" %}

{% block title %}Launch Session{% endblock %}

{% block content %}
<h1>Session Launch</h1>
<iframe src="{{ url }}" style="width: 100%; height: 500px; border: none;"></iframe>
<p>Session is launched in the iframe. URL is hidden for security purposes.</p>
{% endblock %}

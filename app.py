<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %} My Website {% endblock %}</title>
    <!-- Add your CSS/JS links here -->
</head>
<body>
    <!-- Navigation Pane -->
    <nav>
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/about">About</a></li>
            <li><a href="/contact">Contact</a></li>
        </ul>
    </nav>

    <!-- Main Content -->
    <div class="content">
        {% block content %}
        <!-- Content from child templates will go here -->
        {% endblock %}
    </div>
</body>
</html>

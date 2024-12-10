<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My Website{% endblock %}</title>
    <style type="text/css">
        /* Style for the navigation bar */
        nav ul {
            list-style-type: none;
            margin: 0;
            padding: 0;
            overflow: hidden;
            background-color: #333; /* Dark background color */
        }

        nav ul li {
            float: left; /* Align links horizontally */
        }

        nav ul li a {
            display: block;
            color: white;
            text-align: center;
            padding: 14px 16px;
            text-decoration: none; /* Remove underline */
        }

        nav ul li a:hover {
            background-color: #575757; /* Add hover effect */
        }

        /* Style for the main content */
        .content {
            margin: 20px;
            font-family: Arial, sans-serif;
        }
    </style>
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

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Pod Manager{% endblock %}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f9;
        }
        nav {
            background-color: #4CAF50;
            padding: 10px 20px;
            color: white;
        }
        nav ul {
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
        }
        nav ul li {
            margin-right: 20px;
        }
        nav ul li a {
            color: white;
            text-decoration: none;
        }
        nav ul li a:hover {
            text-decoration: underline;
        }
        main {
            padding: 20px;
        }
    </style>
</head>
<body>
    <nav>
        <ul>
            <li><a href="/index">Home</a></li>
            <li><a href="/status">Status</a></li>
            <li><a href="/launch">Launch</a></li>
            <li><a href="/logout">Logout</a></li>
        </ul>
    </nav>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>

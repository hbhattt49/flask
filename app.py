<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Pod Manager{% endblock %}</title>
</head>
<body>
    <nav>
        <ul>
            <li><a href="/index">Home</a></li>
            <li><a href="#" id="deploy-nav">Deploy</a></li>
            <li><a href="#" id="status-nav">Status</a></li>
            <li><a href="/logout">Logout</a></li>
        </ul>
    </nav>
    <div>
        {% block content %}{% endblock %}
    </div>
    <script>
        document.getElementById('deploy-nav').addEventListener('click', async () => {
            const response = await fetch('/deploy', { method: 'POST' });
            const result = await response.json();
            alert(JSON.stringify(result, null, 2));
        });

        document.getElementById('status-nav').addEventListener('click', async () => {
            const response = await fetch('/status');
            const result = await response.json();
            alert(JSON.stringify(result, null, 2));
        });
    </script>
</body>
</html>

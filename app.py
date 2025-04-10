<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Manage Custom Routes</title>
    <style>
        .flash-success {
            color: green;
        }
        .flash-error {
            color: red;
        }
    </style>
</head>
<body>
    <h1>Manage Custom Routes</h1>

    <!-- Flash Messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <ul>
                {% for category, message in messages %}
                    <li class="flash-{{ category }}">{{ message }}</li>
                {% endfor %}
            </ul>
        {% endif %}
    {% endwith %}

    <!-- Form to Create New Route -->
    <h2>Create New Route</h2>
    <form method="post" action="{{ url_for('custom_routes') }}">
        <label for="app_name">Application Name:</label>
        <input type="text" id="app_name" name="app_name" required>
        <br>
        <label for="custom_url">Custom URL:</label>
        <input type="text" id="custom_url" name="custom_url" required>
        <br>
        <label for="port">Port Number:</label>
        <input type="text" id="port" name="port" required>
        <br>
        <button type="submit">Create Route</button>
    </form>

    <!-- List of Active Routes -->
    <h2>Active Routes</h2>
    <table border="1">
        <thead>
            <tr>
                <th>Application</th>
                <th>URL</th>
                <th>Port</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            {% for route in routes %}
                <tr>
                    <td>{{ route.application }}</td>
                    <td>{{ route.url }}</td>
                    <td>{{ route.port }}</td>
                    <td>
                        <form method="post" action="{{ url_for('delete_route', route_name=route.application) }}" style="display:inline;">
                            <button type="submit" onclick="return confirm('Are you sure you want to delete this route?');">Delete</button>
                        </form>
                    </td>
                </tr>
            {% else %}
                <tr>
                    <td colspan="4">No active routes found.</td>
                </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Manage Routes</title>
    <script>
        function deleteRoute(routeName) {
            if (confirm(`Are you sure you want to delete the route '${routeName}'?`)) {
                fetch(`/delete_route/${routeName}`, {
                    method: 'DELETE',
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        alert(data.message);
                        location.reload(); // Refresh the page to update the list of routes
                    } else if (data.error) {
                        alert(`Error: ${data.error}`);
                    }
                })
                .catch(error => {
                    alert(`Request failed: ${error}`);
                });
            }
        }
    </script>
</head>
<body>
    <h1>Active Routes</h1>
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
            <!-- Example row; dynamically generate rows based on your routes data -->
            <tr>
                <td>example-app</td>
                <td>example.com</td>
                <td>8080</td>
                <td><button onclick="deleteRoute('example-app')">Delete</button></td>
            </tr>
            <!-- Repeat rows as needed -->
        </tbody>
    </table>
</body>
</html>

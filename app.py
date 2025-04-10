{% extends "base.html" %}

{% block title %}Custom Routes{% endblock %}

{% block content %}
<h1>Custom Route Management</h1>

<!-- Existing Routes Table -->
<h2>Active Routes</h2>
<table border="1">
    <thead>
        <tr>
            <th>Application</th>
            <th>URL</th>
            <th>Port</th>
        </tr>
    </thead>
    <tbody id="route-list">
        <tr><td colspan="3">Loading...</td></tr>
    </tbody>
</table>

<!-- Create Custom Route Form -->
<h2>Create a Custom Route</h2>
<form id="create-route-form">
    <label for="app-name">Application Name:</label>
    <input type="text" id="app-name" name="app_name" required>

    <label for="custom-url">Custom URL:</label>
    <input type="text" id="custom-url" name="custom_url" required>

    <label for="port">Port Number:</label>
    <input type="number" id="port" name="port" required>

    <button type="submit">Create Route</button>
</form>

<p id="form-message"></p>

<script>
    async function loadRoutes() {
        const response = await fetch('/get_active_routes');
        const data = await response.json();
        const routeList = document.getElementById("route-list");
        routeList.innerHTML = "";

        if (data.routes.length === 0) {
            routeList.innerHTML = "<tr><td colspan='3'>No active routes found.</td></tr>";
            return;
        }

        data.routes.forEach(route => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${route.application}</td>
                <td><a href="http://${route.url}" target="_blank">${route.url}</a></td>
                <td>${route.port}</td>
            `;
            routeList.appendChild(row);
        });
    }

    document.getElementById("create-route-form").addEventListener("submit", async function(event) {
        event.preventDefault();

        const formData = {
            app_name: document.getElementById("app-name").value,
            custom_url: document.getElementById("custom-url").value,
            port: document.getElementById("port").value
        };

        const response = await fetch("/create_custom_route", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData)
        });

        const result = await response.json();
        document.getElementById("form-message").textContent = result.message;
        if (response.ok) {
            loadRoutes();
            document.getElementById("create-route-form").reset();
        }
    });

    loadRoutes();
</script>
{% endblock %}

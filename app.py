{% extends "base.html" %}

{% block title %}Resource List{% endblock %}

{% block content %}
<h1>Cluster Resources</h1>

<!-- Routes List -->
<h2>Route List</h2>
<table border="1">
    <thead>
        <tr>
            <th>Select</th>
            <th>Route Name</th>
            <th>URL</th>
        </tr>
    </thead>
    <tbody id="route-list">
        <tr><td colspan="3">Loading...</td></tr>
    </tbody>
</table>

<button id="delete-routes-btn" style="margin-top: 10px;" disabled>Delete Selected Routes</button>

<script>
    async function fetchData(endpoint, elementId, callback = null) {
        const response = await fetch(endpoint);
        const data = await response.json();
        if (callback) {
            callback(data);
        } else {
            document.getElementById(elementId).innerText = data.output;
        }
    }

    function loadRoutes(data) {
        const routeList = document.getElementById("route-list");
        routeList.innerHTML = "";

        if (data.routes.length === 0) {
            routeList.innerHTML = "<tr><td colspan='3'>No Routes Found</td></tr>";
            return;
        }

        data.routes.forEach(route => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td><input type="checkbox" class="route-checkbox" value="${route.name}"></td>
                <td>${route.name}</td>
                <td><a href="http://${route.url}" target="_blank">${route.url}</a></td>
            `;
            routeList.appendChild(row);
        });

        // Enable Delete Button
        document.querySelectorAll(".route-checkbox").forEach(checkbox => {
            checkbox.addEventListener("change", () => {
                document.getElementById("delete-routes-btn").disabled = !document.querySelectorAll(".route-checkbox:checked").length;
            });
        });
    }

    fetchData("/get_routes", null, loadRoutes);
</script>

{% endblock %}

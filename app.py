{% extends "base.html" %}

{% block title %}Resource List{% endblock %}

{% block content %}
<h1>Cluster Resources</h1>

<!-- PODS -->
<h2>Pod List</h2>
<table border="1">
    <thead>
        <tr>
            <th>Select</th>
            <th>Pod Name</th>
            <th>Status</th>
        </tr>
    </thead>
    <tbody id="pod-list">
        <tr><td colspan="3">Loading...</td></tr>
    </tbody>
</table>
<button id="delete-pods-btn" style="margin-top: 10px;" disabled>Delete Selected Pods</button>

<!-- ROUTES -->
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

<!-- SERVICES -->
<h2>Service List</h2>
<pre id="service-list">Loading...</pre>

<!-- PVCs -->
<h2>PVC List</h2>
<pre id="pvc-list">Loading...</pre>

<script>
    async function fetchData(endpoint, callback) {
        const response = await fetch(endpoint);
        const data = await response.json();
        callback(data);
    }

    function loadPods(data) {
        const podList = document.getElementById("pod-list");
        podList.innerHTML = "";

        if (data.pods.length === 0) {
            podList.innerHTML = "<tr><td colspan='3'>No Pods Found</td></tr>";
            return;
        }

        data.pods.forEach(pod => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td><input type="checkbox" class="pod-checkbox" value="${pod.name}"></td>
                <td>${pod.name}</td>
                <td>${pod.status}</td>
            `;
            podList.appendChild(row);
        });

        document.querySelectorAll(".pod-checkbox").forEach(checkbox => {
            checkbox.addEventListener("change", () => {
                document.getElementById("delete-pods-btn").disabled = !document.querySelectorAll(".pod-checkbox:checked").length;
            });
        });
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

        document.querySelectorAll(".route-checkbox").forEach(checkbox => {
            checkbox.addEventListener("change", () => {
                document.getElementById("delete-routes-btn").disabled = !document.querySelectorAll(".route-checkbox:checked").length;
            });
        });
    }

    async function deleteResources(endpoint, checkboxesClass, successMessage) {
        const selectedItems = Array.from(document.querySelectorAll(checkboxesClass + ":checked"))
            .map(checkbox => ({ name: checkbox.value }));

        if (selectedItems.length === 0) {
            alert("No items selected.");
            return;
        }

        if (!confirm("Are you sure you want to delete the selected items?")) return;

        const response = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ items: selectedItems })
        });

        const result = await response.json();
        alert(result.message);
        window.location.reload();
    }

    document.getElementById("delete-pods-btn").addEventListener("click", () => {
        deleteResources("/delete_pods", ".pod-checkbox", "Selected pods deleted successfully.");
    });

    document.getElementById("delete-routes-btn").addEventListener("click", () => {
        deleteResources("/delete_routes", ".route-checkbox", "Selected routes deleted successfully.");
    });

    fetchData("/get_pods", loadPods);
    fetchData("/get_routes", loadRoutes);
    fetchData("/get_services", data => document.getElementById("service-list").innerText = data.output);
    fetchData("/get_pvc", data => document.getElementById("pvc-list").innerText = data.output);
</script>

{% endblock %}

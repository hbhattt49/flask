{% extends "base.html" %}

{% block title %}Resource List{% endblock %}

{% block content %}
<h1>Cluster Resources</h1>

<!-- Pod List with Checkboxes -->
<h2>Pod List</h2>
<table border="1">
    <thead>
        <tr>
            <th>Select</th>
            <th>Pod Name</th>
            <th>Namespace</th>
            <th>Status</th>
        </tr>
    </thead>
    <tbody id="pod-list">
        <tr><td colspan="4">Loading...</td></tr>
    </tbody>
</table>

<button id="delete-pods-btn" style="margin-top: 10px;" disabled>Delete Selected Pods</button>

<!-- Route List -->
<h2>Route List</h2>
<pre id="route-list">Loading...</pre>

<!-- Service List -->
<h2>Service List</h2>
<pre id="service-list">Loading...</pre>

<!-- PVC List -->
<h2>PVC List</h2>
<pre id="pvc-list">Loading...</pre>

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

    // Load Pod List with Checkboxes
    function loadPods(data) {
        const podList = document.getElementById("pod-list");
        podList.innerHTML = "";

        if (data.pods.length === 0) {
            podList.innerHTML = "<tr><td colspan='4'>No Pods Found</td></tr>";
            return;
        }

        data.pods.forEach(pod => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td><input type="checkbox" class="pod-checkbox" value="${pod.name}" data-namespace="${pod.namespace}"></td>
                <td>${pod.name}</td>
                <td>${pod.namespace}</td>
                <td>${pod.status}</td>
            `;
            podList.appendChild(row);
        });

        // Enable Delete Button
        document.querySelectorAll(".pod-checkbox").forEach(checkbox => {
            checkbox.addEventListener("change", () => {
                document.getElementById("delete-pods-btn").disabled = !document.querySelectorAll(".pod-checkbox:checked").length;
            });
        });
    }

    // Delete Selected Pods
    document.getElementById("delete-pods-btn").addEventListener("click", async () => {
        const selectedPods = Array.from(document.querySelectorAll(".pod-checkbox:checked"))
            .map(checkbox => ({
                name: checkbox.value,
                namespace: checkbox.dataset.namespace
            }));

        if (selectedPods.length === 0) {
            alert("No pods selected.");
            return;
        }

        if (!confirm("Are you sure you want to delete the selected pods?")) return;

        const response = await fetch("/delete_pods", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pods: selectedPods })
        });

        const result = await response.json();
        alert(result.message);

        // Reload Pod List
        fetchData("/get_pods", null, loadPods);
    });

    // Fetch Data
    fetchData("/get_pods", null, loadPods);
    fetchData("/get_routes", "route-list");
    fetchData("/get_services", "service-list");
    fetchData("/get_pvc", "pvc-list");
</script>

{% endblock %}

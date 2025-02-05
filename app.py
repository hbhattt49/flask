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
<h2>PVC List (Modify Size)</h2>
<table border="1">
    <thead>
        <tr>
            <th>PVC Name</th>
            <th>Current Size</th>
            <th>New Size (GB)</th>
            <th>Modify</th>
        </tr>
    </thead>
    <tbody id="pvc-list">
        <tr><td colspan="4">Loading...</td></tr>
    </tbody>
</table>

<script>
    async function fetchData(endpoint, callback) {
        const response = await fetch(endpoint);
        const data = await response.json();
        callback(data);
    }

    function loadPVCs(data) {
        const pvcList = document.getElementById("pvc-list");
        pvcList.innerHTML = "";

        if (data.pvcs.length === 0) {
            pvcList.innerHTML = "<tr><td colspan='4'>No PVCs Found</td></tr>";
            return;
        }

        data.pvcs.forEach(pvc => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${pvc.name}</td>
                <td>${pvc.size}</td>
                <td><input type="number" min="1" class="new-size" data-pvc="${pvc.name}" placeholder="Enter new size"></td>
                <td><button class="resize-btn" data-pvc="${pvc.name}">Modify</button></td>
            `;
            pvcList.appendChild(row);
        });

        document.querySelectorAll(".resize-btn").forEach(button => {
            button.addEventListener("click", async () => {
                const pvcName = button.dataset.pvc;
                const newSize = document.querySelector(`input[data-pvc='${pvcName}']`).value;

                if (!newSize || newSize <= 0) {
                    alert("Please enter a valid size.");
                    return;
                }

                const response = await fetch("/modify_pvc", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ pvc_name: pvcName, new_size: newSize + "Gi" })
                });

                const result = await response.json();
                alert(result.message);
                window.location.reload();
            });
        });
    }

    fetchData("/get_pvc", loadPVCs);
    fetchData("/get_pods", data => document.getElementById("pod-list").innerText = data.output);
    fetchData("/get_routes", data => document.getElementById("route-list").innerText = data.output);
    fetchData("/get_services", data => document.getElementById("service-list").innerText = data.output);
</script>

{% endblock %}

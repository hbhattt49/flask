{% extends "base.html" %}

{% block title %}Home{% endblock %}

{% block content %}
<h1>Welcome, {{ username }}</h1>
<p>You are logged in under the LOB: {{ lob }}</p>

<h2>Status Widget</h2>
<div id="status-widget"
     style="width: 120px; height: 120px; border-radius: 10px; text-align: center; line-height: 120px; font-weight: bold; color: white; background-color: gray; cursor: pointer;">
    Loading...
</div>

<script>
    const statusWidget = document.getElementById('status-widget');

    // Flag to indicate whether a setup process is ongoing
    let isSetupInProgress = false;

    // Function to fetch the current status
    async function updateStatusWidget() {
        statusWidget.textContent = 'Loading...';
        statusWidget.style.backgroundColor = 'gray';
        statusWidget.style.cursor = 'default';

        try {
            const response = await fetch('/status_check'); // Fetch the current status from the backend
            const data = await response.json();

            if (data.status) {
                // If status is healthy
                statusWidget.textContent = 'Healthy';
                statusWidget.style.backgroundColor = 'green';
                statusWidget.style.cursor = 'default'; // Disable pointer cursor if healthy
                statusWidget.onclick = null; // Disable click if already healthy
            } else {
                // If status indicates setup is needed
                statusWidget.textContent = 'Setup Needed';
                statusWidget.style.backgroundColor = 'red';
                statusWidget.style.cursor = 'pointer'; // Enable pointer cursor for setup
                statusWidget.onclick = handleSetup; // Allow click to initiate setup
            }
        } catch (err) {
            // Handle errors (e.g., network issues)
            statusWidget.textContent = 'Error';
            statusWidget.style.backgroundColor = 'gray';
            statusWidget.style.cursor = 'default';
        }
    }

    // Function to handle setup when the widget is clicked
    async function handleSetup() {
        if (isSetupInProgress) {
            return; // Prevent multiple clicks during setup
        }

        isSetupInProgress = true; // Set the flag to true
        statusWidget.textContent = 'Setting up...';
        statusWidget.style.backgroundColor = 'orange';
        statusWidget.style.cursor = 'default'; // Disable pointer cursor

        try {
            const response = await fetch('/one_time_setup', { method: 'POST' });
            const data = await response.json();

            if (response.ok) {
                // On successful setup
                statusWidget.textContent = 'Healthy';
                statusWidget.style.backgroundColor = 'green';
                statusWidget.style.cursor = 'default';
                statusWidget.onclick = null; // Disable further clicks
                alert(data.message); // Show success message
            } else {
                // On failed setup
                statusWidget.textContent = 'Setup Failed';
                statusWidget.style.backgroundColor = 'red';
                statusWidget.style.cursor = 'pointer';
                alert(`Error: ${data.error}\nDetails: ${data.details}`);
            }
        } catch (err) {
            // Handle network or unexpected errors
            statusWidget.textContent = 'Error';
            statusWidget.style.backgroundColor = 'gray';
            statusWidget.style.cursor = 'default';
            alert('Error connecting to the server.');
        } finally {
            isSetupInProgress = false; // Reset the flag after setup completes
        }
    }

    // Initial call to fetch the status
    updateStatusWidget();
</script>
{% endblock %}

{% extends "base.html" %}

{% block title %}Home{% endblock %}

{% block content %}
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-top: 20px;">
    <div style="flex: 1; margin-right: 20px;">
        <h1>Welcome, {{ username }}</h1>
        <p>You are logged in under the LOB: {{ lob }}</p>

        <h2>Deployment Logs</h2>
        <button id="deploy-btn">Deploy</button>
        <textarea id="deploy-output" readonly style="width: 100%; height: 300px; margin-top: 10px;"></textarea>
    </div>

    <div id="status-widget-container" style="width: 120px;">
        <h2>Status Widget</h2>
        <div id="status-widget"
             style="width: 100px; height: 100px; border-radius: 10px; text-align: center; line-height: 100px; font-weight: bold; color: white; background-color: gray;">
            Loading...
        </div>
    </div>
</div>

<script>
    const statusWidget = document.getElementById('status-widget');

    // Function to update the status widget color and behavior
    async function updateStatusWidget() {
        try {
            const response = await fetch('/status_check');
            const data = await response.json();

            if (data.status) {
                // Green for true status
                statusWidget.style.backgroundColor = 'green';
                statusWidget.textContent = 'Healthy';
                statusWidget.onclick = null; // Disable clicking
            } else {
                // Red for false status
                statusWidget.style.backgroundColor = 'red';
                statusWidget.textContent = 'Setup Needed';
                statusWidget.onclick = async () => {
                    statusWidget.textContent = 'Setting up...';
                    try {
                        const setupResponse = await fetch('/one_time_setup', { method: 'POST' });
                        const setupData = await setupResponse.json();
                        if (setupData.message) {
                            alert(setupData.message);
                            updateStatusWidget(); // Recheck the status after setup
                        } else {
                            alert('Setup failed: ' + setupData.error);
                        }
                    } catch (err) {
                        alert('Error executing setup.');
                    }
                };
            }
        } catch (err) {
            statusWidget.style.backgroundColor = 'gray';
            statusWidget.textContent = 'Error';
        }
    }

    // Call the update function on page load
    updateStatusWidget();

    // Deploy button logic
    document.getElementById('deploy-btn').addEventListener('click', () => {
        const outputBox = document.getElementById('deploy-output');
        outputBox.value = ''; // Clear previous output

        const eventSource = new EventSource('/deploy');
        eventSource.onmessage = (event) => {
            outputBox.value += event.data + '\\n'; // Append new data to the output box
            outputBox.scrollTop = outputBox.scrollHeight; // Scroll to the bottom
        };
        eventSource.onerror = () => {
            outputBox.value += '\\n[ERROR] Connection to the server lost.';
            eventSource.close();
        };
    });
</script>
{% endblock %}

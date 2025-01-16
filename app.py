{% extends "base.html" %}

{% block title %}Home{% endblock %}

{% block content %}
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-top: 20px;">
    <!-- Left Section -->
    <div style="flex: 3; margin-right: 20px;">
        <h1>Welcome, {{ username }}</h1>
        <p>You are logged in under the LOB: {{ lob }}</p>

        <!-- Deployment Section -->
        <h2>Deployment Logs</h2>
        <div>
            <button id="deploy-btn" style="margin-bottom: 10px;">Start Deployment</button>
            <button id="run-setup-btn" style="margin-bottom: 10px;">Run Setup</button>
            <textarea id="output-box" readonly style="width: 600px; height: 300px;"></textarea>
        </div>
    </div>

    <!-- Right Section -->
    <div style="flex: 1; display: flex; flex-direction: column; align-items: flex-start;">
        <!-- Widget Section -->
        <div id="status-widget"
             style="width: 120px; height: 120px; border-radius: 10px; text-align: center; line-height: 120px; font-weight: bold; color: white; background-color: gray; margin-bottom: 10px;">
            Loading...
        </div>
        <h2 style="font-size: 16px; text-align: left; margin: 5px 0;">Widget for One-Time Setup</h2>
    </div>
</div>

<script>
    const deployBtn = document.getElementById('deploy-btn');
    const runSetupBtn = document.getElementById('run-setup-btn');
    const outputBox = document.getElementById('output-box');
    const statusWidget = document.getElementById('status-widget');
    let isSetupInProgress = false; // Flag to prevent multiple setup runs

    // Deployment Section Logic
    deployBtn.addEventListener('click', () => {
        outputBox.value = ''; // Clear previous logs
        const eventSource = new EventSource('/deploy');
        let connectionClosedByServer = false;

        eventSource.onmessage = (event) => {
            if (event.data === '[done]') {
                connectionClosedByServer = true;
                outputBox.value += 'Deployment completed successfully.\n';
                eventSource.close();
                updateStatusWidget(); // Refresh widget status after deployment
            } else {
                outputBox.value += event.data + '\n'; // Append logs
            }
            outputBox.scrollTop = outputBox.scrollHeight; // Auto-scroll to bottom
        };

        eventSource.onerror = () => {
            if (!connectionClosedByServer) {
                outputBox.value += '\n[ERROR] Connection to the server lost.';
            }
            eventSource.close();
        };
    });

    // One-Time Setup Button Logic
    runSetupBtn.addEventListener('click', () => {
        if (isSetupInProgress) return; // Prevent multiple clicks

        isSetupInProgress = true;
        statusWidget.textContent = 'Setting up...';
        statusWidget.style.backgroundColor = 'orange';
        outputBox.value = ''; // Clear previous logs

        const eventSource = new EventSource('/one_time_setup');
        let connectionClosedByServer = false;

        eventSource.onmessage = (event) => {
            if (event.data === '[done]') {
                connectionClosedByServer = true;
                outputBox.value += 'Setup completed successfully.\n';
                eventSource.close();
                updateStatusWidget(); // Refresh widget status after setup
                isSetupInProgress = false;
            } else {
                outputBox.value += event.data + '\n'; // Append logs to output box
            }
            outputBox.scrollTop = outputBox.scrollHeight; // Auto-scroll to bottom
        };

        eventSource.onerror = () => {
            if (!connectionClosedByServer) {
                outputBox.value += '\n[ERROR] Connection to the server lost.';
            }
            eventSource.close();
            isSetupInProgress = false;
        };
    });

    // Status Widget Logic
    async function updateStatusWidget() {
        statusWidget.textContent = 'Loading...';
        statusWidget.style.backgroundColor = 'gray';

        try {
            const response = await fetch('/status_check');
            const data = await response.json();

            if (data.status) {
                // If status is healthy, update widget and disable setup button
                statusWidget.textContent = 'Healthy';
                statusWidget.style.backgroundColor = 'green';
                runSetupBtn.disabled = true; // Disable setup button
                runSetupBtn.style.cursor = 'not-allowed'; // Update cursor
            } else {
                // If setup is needed, update widget and enable setup button
                statusWidget.textContent = 'Setup Needed';
                statusWidget.style.backgroundColor = 'red';
                runSetupBtn.disabled = false; // Enable setup button
                runSetupBtn.style.cursor = 'pointer'; // Update cursor
            }
        } catch (err) {
            statusWidget.textContent = 'Error';
            statusWidget.style.backgroundColor = 'gray';
            runSetupBtn.disabled = true; // Disable setup button on error
            runSetupBtn.style.cursor = 'not-allowed';
        }
    }

    // Initial call to fetch the widget status
    updateStatusWidget();
</script>
{% endblock %}

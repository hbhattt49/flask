{% extends "base.html" %}

{% block title %}Home{% endblock %}

{% block content %}
<h1>Welcome, {{ username }}</h1>
<p>You are logged in under the LOB: {{ lob }}</p>

<!-- Deployment Section -->
<h2>Deployment Logs</h2>
<div>
    <button id="deploy-btn" style="margin-bottom: 10px;">Start Deployment</button>
    <textarea id="output-box" readonly style="width: 100%; height: 300px;"></textarea>
</div>

<!-- One-Time Setup Widget Section -->
<h2>One-Time Setup</h2>
<div id="status-widget"
     style="width: 120px; height: 120px; border-radius: 10px; text-align: center; line-height: 120px; font-weight: bold; color: white; background-color: gray; cursor: pointer;">
    Loading...
</div>

<script>
    const deployBtn = document.getElementById('deploy-btn');
    const outputBox = document.getElementById('output-box');
    const statusWidget = document.getElementById('status-widget');
    let isSetupInProgress = false; // Flag to prevent multiple clicks

    // Deployment Section Logic
    deployBtn.addEventListener('click', () => {
        outputBox.value = ''; // Clear previous logs
        const eventSource = new EventSource('/deploy');

        eventSource.onmessage = (event) => {
            outputBox.value += event.data + '\\n'; // Append new logs to output box
            outputBox.scrollTop = outputBox.scrollHeight; // Auto-scroll to bottom
        };

        eventSource.onerror = () => {
            outputBox.value += '\\n[ERROR] Connection to the server lost.';
            eventSource.close();
        };
    });

    // One-Time Setup Widget Logic
    async function updateStatusWidget() {
        statusWidget.textContent = 'Loading...';
        statusWidget.style.backgroundColor = 'gray';
        statusWidget.style.cursor = 'default';

        try {
            const response = await fetch('/status_check');
            const data = await response.json();

            if (data.status) {
                statusWidget.textContent = 'Healthy';
                statusWidget.style.backgroundColor = 'green';
                statusWidget.style.cursor = 'default';
                statusWidget.onclick = null; // Disable click if already healthy
            } else {
                statusWidget.textContent = 'Setup Needed';
                statusWidget.style.backgroundColor = 'red';
                statusWidget.style.cursor = 'pointer';
                statusWidget.onclick = handleSetup;
            }
        } catch (err) {
            statusWidget.textContent = 'Error';
            statusWidget.style.backgroundColor = 'gray';
            statusWidget.style.cursor = 'default';
        }
    }

    async function handleSetup() {
        if (isSetupInProgress) return; // Prevent multiple clicks

        isSetupInProgress = true;
        statusWidget.textContent = 'Setting up...';
        statusWidget.style.backgroundColor = 'orange';
        statusWidget.style.cursor = 'default';

        outputBox.value = ''; // Clear previous logs
        try {
            const eventSource = new EventSource('/one_time_setup');

            eventSource.onmessage = (event) => {
                outputBox.value += event.data + '\\n'; // Append setup logs to the output box
                outputBox.scrollTop = outputBox.scrollHeight; // Auto-scroll to bottom
            };

            eventSource.onerror = () => {
                outputBox.value += '\\n[ERROR] Connection to the server lost during setup.';
                eventSource.close();
                isSetupInProgress = false; // Allow retry if there's an error
            };

            eventSource.addEventListener('close', () => {
                // Ensure the event source is closed after completion
                eventSource.close();
                updateStatusWidget(); // Refresh the widget status
                isSetupInProgress = false;
            });
        } catch (err) {
            outputBox.value += 'Error connecting to the server.';
            statusWidget.textContent = 'Error';
            statusWidget.style.backgroundColor = 'gray';
            statusWidget.style.cursor = 'default';
            isSetupInProgress = false;
        }
    }

    // Initial call to fetch the status
    updateStatusWidget();
</script>
{% endblock %}

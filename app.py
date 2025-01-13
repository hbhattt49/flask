<script>
    const deployBtn = document.getElementById('deploy-btn');
    const outputBox = document.getElementById('deploy-output');

    deployBtn.addEventListener('click', () => {
        outputBox.value = ''; // Clear previous output

        const eventSource = new EventSource('/deploy');

        // Append received messages to the textarea
        eventSource.onmessage = (event) => {
            outputBox.value += event.data + '\\n';
            outputBox.scrollTop = outputBox.scrollHeight; // Scroll to the bottom
        };

        // Handle errors and attempt to reconnect
        eventSource.onerror = () => {
            outputBox.value += '\\n[ERROR] Connection to the server lost. Retrying...';
            eventSource.close();

            // Retry connection after a delay
            setTimeout(() => {
                deployBtn.click();
            }, 5000);
        };
    });
</script>

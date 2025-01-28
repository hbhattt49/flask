<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dynamic JupyterLab iframe</title>
</head>
<body>
    <iframe
        id="jupyterlabIframe"
        src="https://example.com/jupyterlab"  <!-- Replace with your JupyterLab URL -->
        frameborder="0"
        style="width: 100%; height: 500px;"> <!-- Default height -->
    </iframe>

    <script>
        function resizeIframe() {
            const iframe = document.getElementById('jupyterlabIframe');
            
            // Poll until the content has loaded and height is available
            const interval = setInterval(() => {
                try {
                    const contentHeight = iframe.contentWindow.document.body.scrollHeight;

                    // If a valid height is detected, update the iframe's height
                    if (contentHeight > 0) {
                        iframe.style.height = contentHeight + 'px';
                        clearInterval(interval); // Stop polling once height is set
                    }
                } catch (error) {
                    // Cross-origin restriction handling (if any)
                    console.error('Error accessing iframe content:', error);
                }
            }, 500); // Poll every 500ms
        }

        // Trigger resizing once the iframe loads
        const iframe = document.getElementById('jupyterlabIframe');
        iframe.onload = resizeIframe;
    </script>
</body>
</html>

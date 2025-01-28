<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Full-Screen Dynamic iframe</title>
    <style>
        /* Ensure the iframe covers the full viewport */
        html, body {
            margin: 0;
            padding: 0;
            height: 100%;
            overflow: hidden; /* Prevent scrollbars */
        }
        iframe {
            border: none; /* Remove border for full-screen look */
        }
    </style>
</head>
<body>
    <iframe
        id="dynamicIframe"
        src="https://example.com/jupyterlab" <!-- Replace with your JupyterLab URL -->
        style="width: 100%; height: 100%;"></iframe>

    <script>
        // Function to adjust iframe dimensions to the full screen
        function adjustIframeSize() {
            const iframe = document.getElementById('dynamicIframe');
            iframe.style.width = window.innerWidth + 'px'; // Set width to full viewport
            iframe.style.height = window.innerHeight + 'px'; // Set height to full viewport
        }

        // Adjust the iframe size on page load
        window.onload = adjustIframeSize;

        // Adjust the iframe size dynamically when the window is resized
        window.onresize = adjustIframeSize;
    </script>
</body>
</html>

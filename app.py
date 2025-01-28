<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dynamic iframe</title>
</head>
<body>
    <iframe id="dynamicIframe" src="your-content.html" frameborder="0" style="width: 100%;"></iframe>

    <script>
        function resizeIframe() {
            const iframe = document.getElementById('dynamicIframe');
            iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';
        }

        // Listen for the iframe to load its content
        const iframe = document.getElementById('dynamicIframe');
        iframe.onload = resizeIframe;
    </script>
</body>
</html>

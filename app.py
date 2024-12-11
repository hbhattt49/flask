<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pod Manager</title>
</head>
<body>
    <h1>Welcome, {{ username }}</h1>
    <form id="deploy-form" method="POST" action="/deploy">
        <button type="submit">Deploy</button>
    </form>
    <button id="status-btn">Check Status</button>
    <a href="/logout">Logout</a>
    <pre id="output"></pre>
    <script>
        const form = document.getElementById('deploy-form');
        const statusBtn = document.getElementById('status-btn');
        const output = document.getElementById('output');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const response = await fetch('/deploy', {
                method: 'POST',
            });
            const result = await response.json();
            output.textContent = JSON.stringify(result, null, 2);
        });

        statusBtn.addEventListener('click', async () => {
            const response = await fetch('/status');
            const result = await response.json();
            output.textContent = JSON.stringify(result, null, 2);
        });
    </script>
</body>
</html>

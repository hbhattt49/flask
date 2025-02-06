<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resources</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        .container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px; /* Spacing between columns */
        }
        .column {
            flex: 1; /* Each column takes equal space */
            min-width: 300px; /* Ensures responsiveness */
        }
        .resource-box {
            border: 1px solid #ccc;
            padding: 15px;
            border-radius: 8px;
            background-color: #f9f9f9;
        }
    </style>
</head>
<body>

    <h2>Resources</h2>

    <div class="container">
        <!-- Left Column: Pods & PVC -->
        <div class="column">
            <div class="resource-box">
                <h3>Pods List</h3>
                <ul>
                    <li>Pod 1</li>
                    <li>Pod 2</li>
                    <li>Pod 3</li>
                </ul>
            </div>
            <div class="resource-box">
                <h3>PVC List</h3>
                <ul>
                    <li>PVC 1</li>
                    <li>PVC 2</li>
                </ul>
            </div>
        </div>

        <!-- Right Column: Routes & Services -->
        <div class="column">
            <div class="resource-box">
                <h3>Routes List</h3>
                <ul>
                    <li>Route 1</li>
                    <li>Route 2</li>
                </ul>
            </div>
            <div class="resource-box">
                <h3>Services List</h3>
                <ul>
                    <li>Service 1</li>
                    <li>Service 2</li>
                </ul>
            </div>
        </div>
    </div>

</body>
</html>

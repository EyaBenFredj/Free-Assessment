# Save this as create_proper_html.py
from pathlib import Path

graph_dir = Path(r"/results/graph")
graph_dir.mkdir(parents=True, exist_ok=True)

# Create a proper working HTML file
html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Knowledge Graph Results</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f0f2f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1a73e8;
            border-bottom: 3px solid #1a73e8;
            padding-bottom: 10px;
        }
        .file-list {
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .file-item {
            padding: 10px;
            border-bottom: 1px solid #dee2e6;
        }
        .graph-container {
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        img {
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>✅ Knowledge Graph Analysis Complete</h1>

        <div class="file-list">
            <h3>Generated Files:</h3>
            <div class="file-item">📊 <strong>knowledge_graph.png</strong> - Graph visualization</div>
            <div class="file-item">📈 <strong>entity_frequencies.csv</strong> - Entity statistics</div>
            <div class="file-item">🔗 <strong>graph_edges.csv</strong> - Connection data</div>
            <div class="file-item">📄 <strong>report.txt</strong> - Summary report</div>
        </div>

        <div class="graph-container">
            <h3>Graph Visualization:</h3>
            <div id="graph-placeholder">
                <!-- Graph will load here -->
            </div>
        </div>
    </div>

    <script>
        // Try to load the graph image
        function loadGraph() {
            const img = document.createElement('img');
            img.alt = 'Knowledge Graph';
            img.onload = function() {
                document.getElementById('graph-placeholder').innerHTML = '';
                document.getElementById('graph-placeholder').appendChild(img);
            };
            img.onerror = function() {
                document.getElementById('graph-placeholder').innerHTML = 
                    '<p style="color: #666; padding: 20px;">Graph image not available. The graph may be empty or not generated.</p>';
            };
            img.src = 'knowledge_graph.png';
        }

        // Load when page is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', loadGraph);
        } else {
            loadGraph();
        }
    </script>
</body>
</html>"""

# Save it
html_file = graph_dir / "knowledge_graph_working.html"
html_file.write_text(html_content, encoding='utf-8')

print(f"✅ Created: {html_file}")
print(f"📎 Open this URL in your browser:")
print(f"   file:///{html_file.absolute().as_posix()}")
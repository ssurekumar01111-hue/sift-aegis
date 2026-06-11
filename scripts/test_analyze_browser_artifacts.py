import sys
import os
sys.path.append(os.path.abspath("mcp_server"))
from server import analyze_browser_artifacts
import json

results = analyze_browser_artifacts("/mnt/charlie")
with open("real_browser_artifacts.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"Extracted {len(results)} URLs")

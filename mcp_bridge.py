#!/usr/bin/env python3
"""
SIFT-AEGIS MCP Bridge
Starts the MCP server and exposes tools as Python functions.
"""

import subprocess
import sys
import os
import json
import time

sys.path.insert(0, '/home/sansforensics/sift-aegis/mcp_server')

# Import tools directly from server
from server import (
    get_process_list,
    get_network_connections,
    get_registry_run_keys,
    extract_mft_timeline,
    get_dll_list
)

class MCPBridge:
    """Bridge to SIFT-AEGIS MCP tools."""
    
    def __init__(self, cases_dir="/home/sansforensics/cases/m57"):
        self.cases_dir = cases_dir
        os.environ["CASES_DIR"] = cases_dir
        print(f"[MCP Bridge] Initialized. Cases dir: {cases_dir}")
    
    def run_tool(self, tool_name: str, **kwargs) -> dict:
        """Run a forensic tool and return structured result."""
        tools = {
            "get_process_list": get_process_list,
            "get_network_connections": get_network_connections,
            "get_registry_run_keys": get_registry_run_keys,
            "extract_mft_timeline": extract_mft_timeline,
            "get_dll_list": get_dll_list,
        }
        if tool_name not in tools:
            return {"error": f"Unknown tool: {tool_name}"}
        
        print(f"[MCP Bridge] Running tool: {tool_name} with args: {kwargs}")
        start = time.time()
        result = tools[tool_name](**kwargs)
        elapsed = time.time() - start
        print(f"[MCP Bridge] Tool {tool_name} completed in {elapsed:.2f}s")
        return result

if __name__ == "__main__":
    bridge = MCPBridge()
    # Quick test
    result = bridge.run_tool("get_process_list", 
                             memory_image="charlie-2009-12-11.mddramimage")
    print(f"Process count: {result.get('total_count', 0)}")
    print(f"Suspicious PIDs: {result.get('suspicious_pids', [])}")

#!/usr/bin/env python3
"""
SIFT-AEGIS OpenClaw AgentSkill
Exposes forensic MCP tools to OpenClaw agent.
"""

import sys
import os
import json

sys.path.insert(0, '/home/sansforensics/sift-aegis/mcp_server')
os.environ['CASES_DIR'] = '/home/sansforensics/cases/m57'

from server import (
    get_process_list,
    get_network_connections,
    get_registry_run_keys,
    get_dll_list,
    get_malfind,
    extract_mft_timeline
)

MEMORY_IMAGE = "charlie-2009-11-17.mddramimage"
DISK_IMAGE = "charlie-2009-12-11.E01"

TOOL_MAP = {
    "process_list": lambda: get_process_list(MEMORY_IMAGE),
    "network_connections": lambda: get_network_connections(MEMORY_IMAGE),
    "registry_run_keys": lambda: get_registry_run_keys(MEMORY_IMAGE),
    "malfind": lambda: get_malfind(MEMORY_IMAGE),
    "dll_list": lambda pid="3908": get_dll_list(MEMORY_IMAGE, int(pid)),
    "mft_timeline": lambda: extract_mft_timeline(DISK_IMAGE),
}

def run_forensic_tool(tool_name: str, param: str = "") -> str:
    if tool_name not in TOOL_MAP:
        return json.dumps({"error": f"Unknown tool: {tool_name}",
                          "available": list(TOOL_MAP.keys())})
    try:
        if tool_name == "dll_list" and param:
            result = TOOL_MAP[tool_name](param)
        else:
            result = TOOL_MAP[tool_name]()
        summary = {
            "tool": tool_name,
            "total_count": result.get("total_count", 0),
            "suspicious_count": result.get("suspicious_count",
                len(result.get("suspicious_connections", [])) or
                len(result.get("suspicious_pids", []))),
            "sha256_verified": result.get("evidence", {}).get("verified", False),
            "key_findings": []
        }
        if tool_name == "process_list":
            for p in result.get("processes", []):
                if p["pid"] in result.get("suspicious_pids", []):
                    summary["key_findings"].append(
                        f"PID {p['pid']}: {p['image_name']} parent={p['ppid']}")
        elif tool_name == "malfind":
            for e in result.get("entries", [])[:5]:
                summary["key_findings"].append(
                    f"PID {e['pid']}: {e['process_name']} @ {e['address']}")
        elif tool_name == "network_connections":
            for c in result.get("suspicious_connections", [])[:5]:
                summary["key_findings"].append(
                    f"PID {c['pid']} -> {c['foreign_addr']}:{c['foreign_port']}")
        elif tool_name == "registry_run_keys":
            for k in result.get("run_keys", []):
                if k.get("suspicious"):
                    summary["key_findings"].append(
                        f"{k['value_name']} -> {k['value_data']}")
        return json.dumps(summary, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "tool": tool_name})

if __name__ == "__main__":
    print("Testing SIFT-AEGIS OpenClaw Skill...")
    for tool in ["process_list", "network_connections",
                 "registry_run_keys", "malfind"]:
        print(f"\n[{tool}]")
        result = run_forensic_tool(tool)
        data = json.loads(result)
        print(f"  total={data.get('total_count')} "
              f"suspicious={data.get('suspicious_count')}")
        for f in data.get("key_findings", []):
            print(f"  >> {f}")

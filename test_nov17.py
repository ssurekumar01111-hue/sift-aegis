import sys
sys.path.insert(0, '/home/sansforensics/sift-aegis/mcp_server')
from server import get_process_list
result = get_process_list('charlie-2009-11-17.mddramimage')
print('Processes:', result.get('total_count', 0))
print('Suspicious PIDs:', result.get('suspicious_pids', []))
for p in result.get('processes', []):
    if p['pid'] in result.get('suspicious_pids', []):
        print(f"  PID {p['pid']}: {p['image_name']} parent={p['ppid']}")
